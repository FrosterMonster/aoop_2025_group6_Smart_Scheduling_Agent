"""Core scheduling engine with optimization algorithms"""

import datetime
from datetime import timedelta
from typing import Optional, Tuple, List, Dict
import numpy as np
import pytz
import logging

from ai_schedule_agent.models.event import Event
from ai_schedule_agent.models.user_profile import UserProfile
from ai_schedule_agent.models.enums import EventType
from ai_schedule_agent.core.pattern_learner import PatternLearner
from ai_schedule_agent.config.manager import ConfigManager

logger = logging.getLogger(__name__)


class SchedulingEngine:
    """Core scheduling engine with optimization"""

    def __init__(self, user_profile: UserProfile, calendar):
        self.user_profile = user_profile
        self.calendar = calendar
        self.pattern_learner = PatternLearner()
        self.pending_events = []

    def find_optimal_slot(self, event: Event,
                         search_start: datetime.datetime = None,
                         search_days: int = 14) -> Optional[Tuple[datetime.datetime, datetime.datetime]]:
        """Find optimal time slot for an event using intelligent scoring"""

        if not search_start:
            search_start = datetime.datetime.now()

        # Get existing events
        search_end = search_start + timedelta(days=search_days)

        # Convert to UTC for Google Calendar API (which expects UTC with 'Z' suffix)
        if hasattr(search_start, 'tzinfo') and search_start.tzinfo is not None:
            search_start_utc = search_start.astimezone(datetime.timezone.utc)
            search_end_utc = search_end.astimezone(datetime.timezone.utc)
        else:
            search_start_utc = search_start
            search_end_utc = search_end

        existing_events = self.calendar.get_events(
            search_start_utc.isoformat().replace('+00:00', 'Z'),
            search_end_utc.isoformat().replace('+00:00', 'Z')
        )

        # Convert to busy slots (make timezone-naive for comparison)
        busy_slots = []
        for e in existing_events:
            if 'dateTime' in e.get('start', {}):
                start = datetime.datetime.fromisoformat(e['start']['dateTime'].replace('Z', '+00:00'))
                end = datetime.datetime.fromisoformat(e['end']['dateTime'].replace('Z', '+00:00'))
                # Remove timezone info for comparison
                start = start.replace(tzinfo=None)
                end = end.replace(tzinfo=None)
                busy_slots.append((start, end))

        # Calculate event duration including prep and followup
        total_duration = ((event.end_time - event.start_time).seconds // 60 if event.end_time and event.start_time
                         else self.user_profile.preferred_meeting_length)
        total_duration += event.prep_time + event.followup_time

        # Find available slots
        candidates = []
        current_date = search_start.date()

        for day_offset in range(search_days):
            check_date = current_date + timedelta(days=day_offset)
            day_name = check_date.strftime('%A')

            # Get working hours for this day
            if day_name in self.user_profile.working_hours:
                start_hour, end_hour = self.user_profile.working_hours[day_name]
                start_time = datetime.datetime.combine(check_date,
                                                       datetime.datetime.strptime(start_hour, '%H:%M').time())
                end_time = datetime.datetime.combine(check_date,
                                                     datetime.datetime.strptime(end_hour, '%H:%M').time())

                # Check each hour slot
                current_slot = start_time
                while current_slot + timedelta(minutes=total_duration) <= end_time:
                    slot_end = current_slot + timedelta(minutes=total_duration)

                    # Check if slot is free
                    is_free = True
                    for busy_start, busy_end in busy_slots:
                        if not (slot_end <= busy_start or current_slot >= busy_end):
                            is_free = False
                            break

                    if is_free:
                        # Calculate slot score based on energy patterns and preferences
                        score = self._calculate_slot_score(current_slot, event.event_type)
                        candidates.append((current_slot, slot_end, score))

                    current_slot += timedelta(minutes=30)  # Check every 30 minutes

        # Return best candidate
        if candidates:
            candidates.sort(key=lambda x: x[2], reverse=True)
            return (candidates[0][0], candidates[0][1])

        return None

    def _calculate_slot_score(self, slot_time: datetime.datetime, event_type: EventType) -> float:
        """Calculate score for a time slot based on user preferences and energy patterns"""
        score = 0.5  # Base score

        hour = slot_time.hour

        # Energy pattern score
        if hour in self.user_profile.energy_patterns:
            energy_level = self.user_profile.energy_patterns[hour]

            # High energy for demanding tasks
            if event_type in [EventType.FOCUS, EventType.LONG_TERM]:
                score += energy_level * 0.3
            # Lower energy acceptable for routine tasks
            elif event_type in [EventType.DAILY, EventType.SHORT_TERM]:
                score += (1 - abs(energy_level - 0.5)) * 0.3

        # Historical preference score
        optimal_hour = self.pattern_learner.get_optimal_time(event_type, slot_time.date())
        if optimal_hour:
            hour_diff = abs(hour - optimal_hour)
            score += max(0, 1 - (hour_diff / 12)) * 0.2

        return score

    def check_conflicts(self, event: Event) -> List[Dict]:
        """Check for scheduling conflicts"""
        conflicts = []

        if not event.start_time or not event.end_time:
            return conflicts

        # Get events in the same timeframe
        # Convert to UTC for Google Calendar API
        time_min = event.start_time - timedelta(hours=1)
        time_max = event.end_time + timedelta(hours=1)

        if hasattr(time_min, 'tzinfo') and time_min.tzinfo is not None:
            time_min_utc = time_min.astimezone(datetime.timezone.utc)
            time_max_utc = time_max.astimezone(datetime.timezone.utc)
        else:
            time_min_utc = time_min
            time_max_utc = time_max

        existing_events = self.calendar.get_events(
            time_min_utc.isoformat().replace('+00:00', 'Z'),
            time_max_utc.isoformat().replace('+00:00', 'Z')
        )

        for e in existing_events:
            if 'dateTime' in e.get('start', {}):
                start = datetime.datetime.fromisoformat(e['start']['dateTime'].replace('Z', '+00:00'))
                end = datetime.datetime.fromisoformat(e['end']['dateTime'].replace('Z', '+00:00'))

                # Check overlap
                if not (event.end_time <= start or event.start_time >= end):
                    conflicts.append({
                        'event': e,
                        'type': 'time_overlap',
                        'severity': 'high'
                    })

        return conflicts

    def suggest_batch_opportunities(self) -> List[Dict]:
        """Suggest opportunities to batch similar tasks"""
        suggestions = []

        batch_candidates = self.pattern_learner.suggest_batch_events()

        for event_type, common_hours in batch_candidates:
            avg_hour = int(np.mean(common_hours))
            suggestions.append({
                'type': 'batch_suggestion',
                'event_type': event_type,
                'suggested_time': avg_hour,
                'frequency': len(common_hours),
                'message': f"You often schedule {event_type.value} tasks around {avg_hour}:00. "
                          f"Would you like to make this a routine?"
            })

        return suggestions

    def get_busy_periods(self, start_dt: datetime.datetime, end_dt: datetime.datetime,
                        calendar_id: str = 'primary') -> List[Tuple[datetime.datetime, datetime.datetime]]:
        """Get busy periods from Google Calendar using FreeBusy API

        Args:
            start_dt: Start of time range
            end_dt: End of time range
            calendar_id: Calendar ID (default: 'primary')

        Returns:
            List of (start, end) tuples for busy periods
        """
        try:
            # Ensure timezone-aware datetimes
            config = ConfigManager()
            tz_str = config.get_timezone()
            tz = pytz.timezone(tz_str)

            if start_dt.tzinfo is None:
                start_dt = tz.localize(start_dt)
            if end_dt.tzinfo is None:
                end_dt = tz.localize(end_dt)

            # Convert to UTC for API call
            start_utc = start_dt.astimezone(pytz.utc)
            end_utc = end_dt.astimezone(pytz.utc)

            # Query FreeBusy API
            body = {
                "timeMin": start_utc.isoformat(),
                "timeMax": end_utc.isoformat(),
                "items": [{"id": calendar_id}]
            }

            result = self.calendar.service.freebusy().query(body=body).execute()
            busy_list = result.get('calendars', {}).get(calendar_id, {}).get('busy', [])

            # Convert to datetime tuples
            busy_periods = []
            for busy_slot in busy_list:
                start_str = busy_slot['start']
                end_str = busy_slot['end']
                start = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                end = datetime.datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                # Convert to local timezone
                start = start.astimezone(tz)
                end = end.astimezone(tz)
                busy_periods.append((start, end))

            logger.info(f"Found {len(busy_periods)} busy periods between {start_dt} and {end_dt}")
            return busy_periods

        except Exception as e:
            logger.error(f"Error querying busy periods: {e}", exc_info=True)
            return []

    def find_free_slots_between(self, start_dt: datetime.datetime, end_dt: datetime.datetime,
                                min_duration_minutes: int = 60,
                                calendar_id: str = 'primary') -> List[Tuple[datetime.datetime, datetime.datetime]]:
        """Find free time slots in a given range

        Args:
            start_dt: Start of search range
            end_dt: End of search range
            min_duration_minutes: Minimum slot duration in minutes
            calendar_id: Calendar ID (default: 'primary')

        Returns:
            List of (start, end) tuples for free slots
        """
        # Get busy periods
        busy_periods = self.get_busy_periods(start_dt, end_dt, calendar_id)

        if not busy_periods:
            # No busy periods - entire range is free
            return [(start_dt, end_dt)]

        # Sort and merge overlapping busy periods
        busy_periods.sort(key=lambda x: x[0])
        merged_busy = []
        current_start, current_end = busy_periods[0]

        for start, end in busy_periods[1:]:
            if start <= current_end:
                # Overlapping or adjacent - merge
                current_end = max(current_end, end)
            else:
                # No overlap - save current and start new
                merged_busy.append((current_start, current_end))
                current_start, current_end = start, end

        merged_busy.append((current_start, current_end))

        # Find gaps (free slots) between busy periods
        free_slots = []

        # Check before first busy period
        if merged_busy[0][0] > start_dt:
            gap_duration = (merged_busy[0][0] - start_dt).total_seconds() / 60
            if gap_duration >= min_duration_minutes:
                free_slots.append((start_dt, merged_busy[0][0]))

        # Check gaps between busy periods
        for i in range(len(merged_busy) - 1):
            gap_start = merged_busy[i][1]
            gap_end = merged_busy[i + 1][0]
            gap_duration = (gap_end - gap_start).total_seconds() / 60

            if gap_duration >= min_duration_minutes:
                free_slots.append((gap_start, gap_end))

        # Check after last busy period
        if merged_busy[-1][1] < end_dt:
            gap_duration = (end_dt - merged_busy[-1][1]).total_seconds() / 60
            if gap_duration >= min_duration_minutes:
                free_slots.append((merged_busy[-1][1], end_dt))

        logger.info(f"Found {len(free_slots)} free slots (min {min_duration_minutes} min)")
        return free_slots

    def plan_week_schedule(self, summary: str, total_hours: float, chunk_hours: float = 2.0,
                          daily_window: Tuple[int, int] = (9, 18), max_weeks: int = 4,
                          calendar_id: str = 'primary', event_type: EventType = EventType.FOCUS,
                          description: str = None) -> List[Dict]:
        """Automatically schedule a task across multiple weeks by finding free slots

        This is the advanced auto-scheduling feature from 阿嚕米.

        Args:
            summary: Event title/summary
            total_hours: Total hours to schedule
            chunk_hours: Preferred chunk size in hours (default: 2.0)
            daily_window: Time window tuple (start_hour, end_hour), e.g., (9, 18) for 9am-6pm
            max_weeks: Maximum weeks to look ahead (default: 4)
            calendar_id: Calendar ID (default: 'primary')
            event_type: Type of event (default: FOCUS)
            description: Optional event description

        Returns:
            List of created event dictionaries with 'start', 'end', 'summary', 'event_id'

        Example:
            >>> engine.plan_week_schedule("Study Electronics", total_hours=10, chunk_hours=2.5)
            # Creates 4 events of 2.5 hours each across available slots
        """
        config = ConfigManager()
        tz_str = config.get_timezone()
        tz = pytz.timezone(tz_str)

        now = datetime.datetime.now(tz)
        hours_remaining = total_hours
        chunk_minutes = int(chunk_hours * 60)
        created_events = []

        logger.info(f"Planning week schedule: '{summary}' - {total_hours}h total in {chunk_hours}h chunks")

        # Check DRY_RUN mode
        is_dry_run = config.is_dry_run()
        if is_dry_run:
            logger.info("DRY_RUN mode active - will simulate event creation")

        # Iterate through days
        for week in range(max_weeks):
            for day in range(7):
                if hours_remaining <= 0:
                    break

                # Calculate date
                target_date = (now + timedelta(days=week * 7 + day)).date()
                day_name = target_date.strftime('%A')

                # Create daily window
                window_start = tz.localize(datetime.datetime.combine(
                    target_date,
                    datetime.time(daily_window[0], 0)
                ))
                window_end = tz.localize(datetime.datetime.combine(
                    target_date,
                    datetime.time(daily_window[1], 0)
                ))

                # Skip if window is in the past
                if window_end < now:
                    continue

                # Adjust window start if partially in past
                if window_start < now:
                    window_start = now

                # Find free slots in this daily window
                free_slots = self.find_free_slots_between(
                    window_start,
                    window_end,
                    min_duration_minutes=min(chunk_minutes, int(hours_remaining * 60)),
                    calendar_id=calendar_id
                )

                # Try to fill free slots
                for slot_start, slot_end in free_slots:
                    if hours_remaining <= 0:
                        break

                    # Calculate chunk size for this slot
                    slot_duration_hours = (slot_end - slot_start).total_seconds() / 3600
                    chunk_to_schedule = min(chunk_hours, hours_remaining, slot_duration_hours)

                    if chunk_to_schedule < 0.5:  # Skip very small chunks
                        continue

                    # Create event
                    event_start = slot_start
                    event_end = event_start + timedelta(hours=chunk_to_schedule)

                    # Create Event object
                    event = Event(
                        title=summary,
                        start_time=event_start,
                        end_time=event_end,
                        event_type=event_type,
                        description=description or f"Auto-scheduled: {chunk_to_schedule:.1f}h block"
                    )

                    try:
                        if is_dry_run:
                            # Simulate
                            logger.info(f"DRY_RUN: Would create event '{summary}' on {event_start.strftime('%Y-%m-%d %H:%M')} - {event_end.strftime('%H:%M')} ({chunk_to_schedule:.1f}h)")
                            event_id = f"dry_run_{len(created_events)}"
                        else:
                            # Actually create the event
                            event_result = self.calendar.create_event(event)
                            event_id = event_result.get('id', 'unknown')
                            logger.info(f"Created event '{summary}' on {event_start.strftime('%Y-%m-%d %H:%M')} ({chunk_to_schedule:.1f}h)")

                        created_events.append({
                            'start': event_start,
                            'end': event_end,
                            'summary': summary,
                            'event_id': event_id,
                            'duration_hours': chunk_to_schedule,
                            'dry_run': is_dry_run
                        })

                        hours_remaining -= chunk_to_schedule

                    except Exception as e:
                        logger.error(f"Failed to create event: {e}")

            if hours_remaining <= 0:
                break

        # Summary
        total_scheduled = total_hours - hours_remaining
        logger.info(f"Scheduled {total_scheduled:.1f}h out of {total_hours}h requested ({len(created_events)} events)")

        if hours_remaining > 0:
            logger.warning(f"Could not schedule remaining {hours_remaining:.1f}h (no free slots found in {max_weeks} weeks)")

        return created_events
