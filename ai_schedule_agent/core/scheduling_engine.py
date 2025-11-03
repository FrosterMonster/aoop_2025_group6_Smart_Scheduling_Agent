"""Core scheduling engine with optimization algorithms"""

import datetime
from datetime import timedelta
from typing import Optional, Tuple, List, Dict
import numpy as np

from ai_schedule_agent.models.event import Event
from ai_schedule_agent.models.user_profile import UserProfile
from ai_schedule_agent.models.enums import EventType
from ai_schedule_agent.core.pattern_learner import PatternLearner


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
        existing_events = self.calendar.get_events(
            search_start.isoformat() + 'Z',
            search_end.isoformat() + 'Z'
        )

        # Convert to busy slots
        busy_slots = []
        for e in existing_events:
            if 'dateTime' in e.get('start', {}):
                start = datetime.datetime.fromisoformat(e['start']['dateTime'].replace('Z', '+00:00'))
                end = datetime.datetime.fromisoformat(e['end']['dateTime'].replace('Z', '+00:00'))
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
        existing_events = self.calendar.get_events(
            (event.start_time - timedelta(hours=1)).isoformat() + 'Z',
            (event.end_time + timedelta(hours=1)).isoformat() + 'Z'
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
