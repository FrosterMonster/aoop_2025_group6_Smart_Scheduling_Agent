"""Natural Language Processing for scheduling requests"""

import re
from typing import Dict, Optional
import spacy
import dateparser

from ai_schedule_agent.models.enums import EventType
from ai_schedule_agent.config.manager import ConfigManager
from ai_schedule_agent.utils.logging import logger
from ai_schedule_agent.utils.time_parser import parse_nl_time


class NLPProcessor:
    """Natural Language Processing for scheduling requests with LLM and rule-based fallback"""

    def __init__(self, use_llm: Optional[bool] = None, calendar=None):
        """Initialize NLP Processor

        Args:
            use_llm: If True, use LLM for processing. If False, use rule-based.
                     If None, auto-detect based on config and API key availability.
            calendar: Optional calendar integration for schedule checking
        """
        self.config = ConfigManager()
        self.calendar = calendar

        # Determine if LLM should be used
        if use_llm is None:
            # Auto-detect: use LLM if configured and API key available
            self.use_llm = self.config.use_llm() and bool(self.config.get_api_key('openai'))
        else:
            self.use_llm = use_llm

        # Lazy initialization - LLM agent will be loaded on first use
        self.llm_agent = None
        self._llm_initialized = False

        # Lazy initialization - spacy will be loaded on first use
        self.nlp = None
        self._spacy_initialized = False
        self._spacy_model = self.config.get_setting('nlp', 'spacy_model', default='en_core_web_sm')

        logger.info(f"NLP Processor initialized (lazy loading enabled)")

    def _ensure_llm_initialized(self):
        """Lazy initialization of LLM agent on first use"""
        if self._llm_initialized:
            return

        self._llm_initialized = True
        if self.use_llm:
            try:
                from ai_schedule_agent.core.llm_agent import LLMAgent
                self.llm_agent = LLMAgent(self.config)
                if self.llm_agent.is_available():
                    logger.info("LLM agent initialized successfully")
                else:
                    logger.warning("LLM agent not available. Falling back to rule-based NLP.")
                    self.use_llm = False
            except Exception as e:
                logger.warning(f"Failed to initialize LLM agent: {e}. Using rule-based NLP.")
                self.use_llm = False

    def _ensure_spacy_initialized(self):
        """Lazy initialization of spacy model on first use"""
        if self._spacy_initialized:
            return

        self._spacy_initialized = True
        try:
            logger.info(f"Loading spacy model '{self._spacy_model}'...")
            self.nlp = spacy.load(self._spacy_model)
            logger.info("Spacy model loaded successfully")
        except:
            # If spacy model not installed, use basic parsing
            self.nlp = None
            logger.warning(f"Spacy model '{self._spacy_model}' not found. Using basic NLP parsing.")

    def parse_scheduling_request(self, text: str) -> Dict:
        """Parse natural language scheduling request using LLM or rule-based fallback

        Args:
            text: Natural language scheduling request

        Returns:
            Dictionary with parsed scheduling information
        """
        # Try LLM processing first if enabled
        # LLM handles intelligent time selection and form filling
        if self.use_llm:
            self._ensure_llm_initialized()  # Lazy load LLM on first use

        if self.use_llm and self.llm_agent:
            try:
                logger.info(f"Processing with LLM: '{text}'")
                llm_result = self.llm_agent.process_request(text)

                action = llm_result.get('action')

                if llm_result.get('success'):
                    if action == 'check_schedule':
                        logger.info("LLM requested schedule check before scheduling")
                        return self._handle_check_schedule(llm_result, text)
                    elif action == 'schedule_event':
                        return self._convert_llm_result_to_dict(llm_result, text)
                    elif action == 'query':
                        logger.info(f"LLM requested query: {llm_result.get('data', {}).get('query_type')}")
                        return self._handle_query(llm_result, text)
                    elif action == 'edit_event':
                        logger.info(f"LLM requested edit: {llm_result.get('data', {}).get('event_identifier')}")
                        return self._handle_edit(llm_result, text)
                    elif action == 'delete_event':
                        logger.info(f"LLM requested delete: {llm_result.get('data', {}).get('event_identifier')}")
                        return self._handle_delete(llm_result, text)
                    elif action == 'move_event':
                        logger.info(f"LLM requested move: {llm_result.get('data', {}).get('event_identifier')}")
                        return self._handle_move(llm_result, text)
                    elif action == 'multi_schedule':
                        logger.info(f"LLM requested multi-schedule: {len(llm_result.get('data', {}).get('multi_events', []))} events")
                        return self._handle_multi_schedule(llm_result, text)
                    elif action == 'conversation' or action == 'chat':
                        logger.info("LLM responded with conversation, no scheduling action")
                        return {
                            'action': 'conversation',
                        'response': llm_result.get('response'),
                        'llm_mode': True
                    }
                else:
                    # LLM failed, fall back to rule-based
                    logger.warning("LLM processing failed, falling back to rule-based NLP")
            except Exception as e:
                logger.error(f"Error in LLM processing: {e}. Falling back to rule-based NLP.")

        # Rule-based processing (original logic)
        logger.info(f"Processing with rule-based NLP: '{text}'")

        # Try Chinese-specific patterns (from 阿嚕米)
        chinese_result = self._extract_with_chinese_patterns(text)

        result = {
            'action': 'create',  # Default to create
            'event_type': EventType.MEETING,  # Default to meeting
            'participants': [],
            'datetime': chinese_result.get('datetime'),  # Prefer Chinese extraction
            'end_datetime': chinese_result.get('end_datetime'),  # From Chinese patterns
            'duration': chinese_result.get('duration'),  # From Chinese patterns
            'location': None,
            'title': chinese_result.get('title'),  # Prefer Chinese extraction
            'description': None,
            'llm_mode': False,
            # CRITICAL: Include time preference fields for UI layer
            'target_date': chinese_result.get('target_date'),  # For time period scheduling
            'time_preference': chinese_result.get('time_preference')  # afternoon/morning/evening
        }

        # Basic keyword extraction
        text_lower = text.lower()
        original_text = text

        # Determine action (including Chinese keywords)
        create_keywords = ['schedule', 'book', 'arrange', 'set up', 'add', 'create',
                          '安排', '排', '訂', '預定', '建立', '新增']
        reschedule_keywords = ['reschedule', 'move', 'change', '改', '移動', '更改', '調整']
        cancel_keywords = ['cancel', 'delete', 'remove', '取消', '刪除', '移除']

        if any(word in text_lower or word in text for word in create_keywords):
            result['action'] = 'create'
        elif any(word in text_lower or word in text for word in reschedule_keywords):
            result['action'] = 'reschedule'
        elif any(word in text_lower or word in text for word in cancel_keywords):
            result['action'] = 'cancel'

        # Determine event type
        if 'meeting' in text_lower:
            result['event_type'] = EventType.MEETING
        elif 'lunch' in text_lower or 'dinner' in text_lower or 'breakfast' in text_lower:
            result['event_type'] = EventType.BREAK
        elif 'focus' in text_lower or 'deep work' in text_lower or 'coding' in text_lower:
            result['event_type'] = EventType.FOCUS
        elif 'break' in text_lower or 'rest' in text_lower:
            result['event_type'] = EventType.BREAK
        elif 'workout' in text_lower or 'gym' in text_lower or 'exercise' in text_lower:
            result['event_type'] = EventType.PERSONAL
        elif 'appointment' in text_lower or 'doctor' in text_lower or 'dentist' in text_lower:
            result['event_type'] = EventType.TASK

        # Extract participants
        # Names with "with" keyword
        with_pattern = r'with\s+([A-Z][a-z]+(?:\s+and\s+[A-Z][a-z]+)*(?:\s*,\s*[A-Z][a-z]+)*)'
        with_match = re.search(with_pattern, original_text)
        if with_match:
            names_str = with_match.group(1)
            names = re.split(r'\s+and\s+|\s*,\s*', names_str)
            result['participants'] = [name.strip() for name in names if name.strip()]

        # Extract emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            result['participants'].extend(emails)

        # Extract location
        location_patterns = [
            r'at\s+([A-Z][A-Za-z\s]+?)(?:\s+on|\s+at|\s+for|\s+tomorrow|\s+next|\s+this|$)',
            r'in\s+([A-Z][A-Za-z\s]+?)(?:\s+on|\s+at|\s+for|\s+tomorrow|\s+next|\s+this|$)',
            r'@\s*([A-Za-z\s]+?)(?:\s+on|\s+at|\s+for|\s+tomorrow|\s+next|\s+this|$)'
        ]

        for pattern in location_patterns:
            loc_match = re.search(pattern, original_text)
            if loc_match:
                location = loc_match.group(1).strip()
                # Check if it's not a time reference
                if not any(time_word in location.lower() for time_word in ['morning', 'afternoon', 'evening', 'night', 'noon']):
                    result['location'] = location
                    break

        # Extract duration
        duration_patterns = [
            (r'for\s+(\d+)\s*hour(?:s)?', lambda x: int(x) * 60),
            (r'for\s+(\d+)\s*hr(?:s)?', lambda x: int(x) * 60),
            (r'(\d+)\s*hour(?:s)?', lambda x: int(x) * 60),
            (r'for\s+(\d+)\s*minute(?:s)?', lambda x: int(x)),
            (r'for\s+(\d+)\s*min(?:s)?', lambda x: int(x)),
            (r'(\d+)\s*min(?:s)?', lambda x: int(x))
        ]

        for pattern, converter in duration_patterns:
            match = re.search(pattern, text_lower)
            if match:
                result['duration'] = converter(match.group(1))
                break

        # Extract datetime (do this after extracting location to avoid conflicts)
        # Only use dateparser fallback if Chinese patterns didn't find datetime
        if not result.get('datetime'):
            # First, try to normalize common date/time patterns
            normalized_text = text

            # Handle patterns like "11/27 pm9:00" -> "11/27 9:00 PM"
            normalized_text = re.sub(r'(\d{1,2}/\d{1,2})\s*(pm|am)(\d{1,2}):(\d{2})',
                                    r'\1 \3:\4 \2', normalized_text, flags=re.IGNORECASE)

            # Try parsing the normalized text first
            parsed_date = dateparser.parse(normalized_text, settings={
                'PREFER_DATES_FROM': 'future'
            })

            # If that fails, try original text
            if not parsed_date:
                parsed_date = dateparser.parse(text, settings={
                    'PREFER_DATES_FROM': 'future'
                })

            if parsed_date:
                result['datetime'] = parsed_date

        # Extract title (smart extraction) - only if Chinese patterns didn't find one
        title = result.get('title')  # Use Chinese-extracted title if available

        if not title:
            # 1. Check for quoted text
            quoted = re.findall(r'"([^"]*)"', text)
            if quoted:
                title = quoted[0]
            else:
                # 2. Try to extract based on patterns
                # Remove action words and temporal expressions
                clean_text = original_text

                # Remove common action words
                for word in ['schedule', 'book', 'arrange', 'set up', 'add', 'create', 'please', 'can you']:
                    clean_text = re.sub(rf'\b{word}\b', '', clean_text, flags=re.IGNORECASE)

                # Remove time expressions
                time_words = ['tomorrow', 'today', 'next week', 'next month', 'on monday', 'on tuesday',
                             'on wednesday', 'on thursday', 'on friday', 'on saturday', 'on sunday',
                             r'at \d+', r'for \d+', 'this morning', 'this afternoon', 'this evening']
                for word in time_words:
                    clean_text = re.sub(rf'\b{word}\b[^,]*', '', clean_text, flags=re.IGNORECASE)

                # Remove participant references
                if with_match:
                    clean_text = clean_text.replace(with_match.group(0), '')

                # Remove location references (at/in location)
                clean_text = re.sub(r'\s+(?:at|in|@)\s+[A-Z][A-Za-z\s]+', '', clean_text)

                # Clean up and extract
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                clean_text = clean_text.strip(',.-')

                if clean_text and len(clean_text) > 2:
                    title = clean_text
                else:
                    # Fallback: use the first few words
                    words = original_text.split()
                    if len(words) >= 2:
                        title = ' '.join(words[:3])
                    else:
                        title = original_text

        result['title'] = title.strip() if title else 'New Event'

        # Log parsing result for debugging
        logger.info(f"NLP Parse: '{text}' -> title='{result['title']}', "
                   f"datetime={result.get('datetime')}, "
                   f"target_date={result.get('target_date')}, "
                   f"time_preference={result.get('time_preference')}, "
                   f"duration={result.get('duration')}")

        return result

    def _handle_query(self, llm_result: Dict, original_text: str) -> Dict:
        """Handle query action - user wants to view/search their schedule"""
        data = llm_result.get('data', {})
        query_data = data.get('query', {})

        return {
            'action': 'query',
            'query_type': query_data.get('query_type', 'show_schedule'),
            'time_range': query_data.get('time_range'),
            'search_term': query_data.get('search_term'),
            'llm_response': llm_result.get('response'),
            'llm_mode': True
        }

    def _handle_edit(self, llm_result: Dict, original_text: str) -> Dict:
        """Handle edit action - user wants to modify an existing event"""
        data = llm_result.get('data', {})
        edit_data = data.get('edit', {})

        return {
            'action': 'edit',
            'event_identifier': edit_data.get('event_identifier'),
            'changes': edit_data.get('changes', {}),
            'llm_response': llm_result.get('response'),
            'llm_mode': True
        }

    def _handle_delete(self, llm_result: Dict, original_text: str) -> Dict:
        """Handle delete action - user wants to cancel/remove events"""
        data = llm_result.get('data', {})
        delete_data = data.get('delete', {})

        return {
            'action': 'delete',
            'event_identifier': delete_data.get('event_identifier'),
            'time_range': delete_data.get('time_range'),
            'llm_response': llm_result.get('response'),
            'llm_mode': True
        }

    def _handle_move(self, llm_result: Dict, original_text: str) -> Dict:
        """Handle move action - user wants to reschedule an event"""
        data = llm_result.get('data', {})
        move_data = data.get('move', {})

        return {
            'action': 'move',
            'event_identifier': move_data.get('event_identifier'),
            'new_time': move_data.get('new_time'),
            'llm_response': llm_result.get('response'),
            'llm_mode': True
        }

    def _handle_multi_schedule(self, llm_result: Dict, original_text: str) -> Dict:
        """Handle multi-schedule action - user wants to schedule multiple events"""
        data = llm_result.get('data', {})
        events = data.get('multi_events', [])

        # Parse each event
        parsed_events = []
        for event in events:
            parsed_event = {
                'title': event.get('summary', 'Untitled Event'),
                'start_time_str': event.get('start_time_str'),
                'end_time_str': event.get('end_time_str', '1 hour'),
                'description': event.get('description', ''),
                'location': event.get('location', '')
            }
            parsed_events.append(parsed_event)

        return {
            'action': 'multi_schedule',
            'events': parsed_events,
            'llm_response': llm_result.get('response'),
            'llm_mode': True
        }

    def _ask_llm_for_optimal_time(self, target_date, duration, title, description, location, original_request):
        """Ask LLM to analyze calendar and suggest optimal time slots

        Args:
            target_date: Target date for the event (or None for flexible)
            duration: Duration in minutes
            title: Event title
            description: Event description
            location: Event location
            original_request: Original user request

        Returns:
            Dictionary with suggested_start_time, suggested_end_time, and reasoning
        """
        if not self.calendar:
            logger.warning("No calendar available for schedule checking")
            return None

        # Ensure LLM is initialized
        self._ensure_llm_initialized()
        if not self.llm_agent or not self.use_llm:
            logger.warning("LLM not available for schedule analysis")
            return None

        import datetime
        from datetime import timedelta

        # Determine search range
        if target_date:
            search_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            search_days = 3  # Check target day and next 2 days
        else:
            search_start = datetime.datetime.now()
            search_days = 7  # Check next week

        search_end = search_start + timedelta(days=search_days)

        # Convert to UTC for Google Calendar API
        import pytz
        if hasattr(search_start, 'tzinfo') and search_start.tzinfo is not None:
            search_start_utc = search_start.astimezone(datetime.timezone.utc)
            search_end_utc = search_end.astimezone(datetime.timezone.utc)
        else:
            # Naive datetime - assume local timezone
            local_tz = pytz.timezone('Asia/Taipei')
            search_start = local_tz.localize(search_start)
            search_end = local_tz.localize(search_end)
            search_start_utc = search_start.astimezone(datetime.timezone.utc)
            search_end_utc = search_end.astimezone(datetime.timezone.utc)

        # Fetch existing events
        try:
            # Ensure proper RFC3339 format with 'Z' suffix
            time_min = search_start_utc.isoformat().replace('+00:00', 'Z')
            time_max = search_end_utc.isoformat().replace('+00:00', 'Z')

            # Validate format (should end with 'Z')
            if not time_min.endswith('Z') or not time_max.endswith('Z'):
                logger.error(f"Invalid timestamp format: time_min={time_min}, time_max={time_max}")
                return None

            existing_events = self.calendar.get_events(time_min, time_max)
        except Exception as e:
            logger.error(f"Failed to fetch calendar events: {e}")
            return None

        # Format events for LLM
        events_summary = self._format_events_for_llm(existing_events, search_start, search_end)

        # Ask LLM to find optimal time
        max_attempts = 3 if not target_date else 1  # Try multiple dates if flexible
        for attempt in range(max_attempts):
            if attempt > 0:
                # Expand search window for subsequent attempts
                search_start = search_start + timedelta(days=attempt * 3)
                search_end = search_end + timedelta(days=attempt * 3)

                # Fetch events for new window
                if hasattr(search_start, 'tzinfo') and search_start.tzinfo is not None:
                    search_start_utc = search_start.astimezone(datetime.timezone.utc)
                    search_end_utc = search_end.astimezone(datetime.timezone.utc)
                else:
                    import pytz
                    local_tz = pytz.timezone('Asia/Taipei')
                    search_start = local_tz.localize(search_start)
                    search_end = local_tz.localize(search_end)
                    search_start_utc = search_start.astimezone(datetime.timezone.utc)
                    search_end_utc = search_end.astimezone(datetime.timezone.utc)

                existing_events = self.calendar.get_events(
                    search_start_utc.isoformat().replace('+00:00', 'Z'),
                    search_end_utc.isoformat().replace('+00:00', 'Z')
                )
                events_summary = self._format_events_for_llm(existing_events, search_start, search_end)

            prompt = self._build_schedule_analysis_prompt(
                events_summary=events_summary,
                duration=duration,
                title=title,
                description=description,
                location=location,
                original_request=original_request,
                search_start=search_start,
                search_end=search_end
            )

            logger.info(f"Asking LLM to analyze schedule (attempt {attempt + 1}/{max_attempts})")

            # Use the LLM agent's underlying provider to get a direct text response
            try:
                # Call the LLM with a simple text prompt (not structured)
                messages = [{"role": "user", "content": prompt}]
                response = self.llm_agent.provider.call_llm(
                    messages=messages,
                    tools=[],  # No tools, just want text response
                    max_tokens=500
                )

                llm_response = response.get('content', '')
                suggested_time = self._parse_llm_time_suggestion(llm_response)

                if suggested_time:
                    logger.info(f"LLM suggested time: {suggested_time}")
                    return suggested_time
            except Exception as e:
                logger.warning(f"LLM schedule analysis failed: {e}")

        logger.warning("LLM could not find optimal time after multiple attempts")
        return None

    def _format_events_for_llm(self, events, search_start, search_end):
        """Format calendar events for LLM analysis"""
        if not events:
            return f"No events scheduled between {search_start.strftime('%Y-%m-%d')} and {search_end.strftime('%Y-%m-%d')}."

        formatted = []
        formatted.append(f"Existing events from {search_start.strftime('%Y-%m-%d')} to {search_end.strftime('%Y-%m-%d')}:")
        formatted.append("")

        import datetime as dt
        for event in events:
            summary = event.get('summary', 'Untitled')
            start = event.get('start', {})
            end = event.get('end', {})

            if 'dateTime' in start:
                start_dt = dt.datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                end_dt = dt.datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))

                # Convert to local timezone for display
                import pytz
                local_tz = pytz.timezone('Asia/Taipei')
                start_local = start_dt.astimezone(local_tz)
                end_local = end_dt.astimezone(local_tz)

                formatted.append(f"- {summary}")
                formatted.append(f"  {start_local.strftime('%Y-%m-%d %H:%M')} - {end_local.strftime('%H:%M')}")

        return "\n".join(formatted)

    def _build_schedule_analysis_prompt(self, events_summary, duration, title, description, location, original_request, search_start, search_end):
        """Build prompt for LLM to analyze schedule and suggest time"""
        hours = duration // 60
        mins = duration % 60
        duration_str = f"{hours}h {mins}m" if mins else f"{hours}h"

        prompt = f"""Find an optimal time slot for scheduling.

Request: {original_request}
Event: {title}
Duration: {duration_str}
Search window: {search_start.strftime('%Y-%m-%d')} to {search_end.strftime('%Y-%m-%d')}

{events_summary}

Requirements:
- No conflicts with existing events
- Working hours: 9 AM - 6 PM (flexible)
- Allow 15min between events

Respond with:
START TIME: YYYY-MM-DD HH:MM
REASON: Brief explanation

Example:
START TIME: 2025-11-07 14:00
REASON: Free slot in afternoon, no conflicts, good spacing"""

        return prompt

    def _parse_llm_time_suggestion(self, llm_response):
        """Parse LLM response to extract suggested time"""
        if not llm_response or llm_response.strip() == '':
            logger.warning("Empty LLM response for time suggestion")
            return None

        import re
        import datetime

        # Try multiple patterns to be more flexible
        patterns = [
            r'START TIME:\s*(\d{4}-\d{2}-\d{2})\s+(\d{1,2}):(\d{2})',  # New format
            r'(\d{4}-\d{2}-\d{2})\s+at\s+(\d{1,2}):(\d{2})',  # Old format with "at"
            r'(\d{4}-\d{2}-\d{2})\s+(\d{1,2}):(\d{2})',  # Simple format
        ]

        for pattern in patterns:
            match = re.search(pattern, llm_response)
            if match:
                date_str = match.group(1)
                hour = int(match.group(2))
                minute = int(match.group(3))

                try:
                    suggested_start = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    suggested_start = suggested_start.replace(hour=hour, minute=minute)

                    # Add timezone
                    import pytz
                    local_tz = pytz.timezone('Asia/Taipei')
                    suggested_start = local_tz.localize(suggested_start)

                    # Extract reasoning if present
                    reasoning_match = re.search(r'REASON:\s*(.+?)(?:\n|$)', llm_response, re.DOTALL)
                    reasoning = reasoning_match.group(1).strip() if reasoning_match else llm_response

                    return {
                        'start_time': suggested_start,
                        'reasoning': reasoning
                    }
                except Exception as e:
                    logger.warning(f"Failed to parse time suggestion: {e}")

        logger.warning(f"Could not parse time from LLM response: {llm_response[:200]}")
        return None

    def _handle_check_schedule(self, llm_result: Dict, original_text: str) -> Dict:
        """Handle check_schedule action from LLM by fetching calendar and asking LLM to find optimal time

        Args:
            llm_result: Result from LLM with check_schedule action
            original_text: Original user input

        Returns:
            Dictionary with check_schedule information including LLM-suggested time
        """
        data = llm_result.get('data', {})
        event_details = data.get('event_details', {})

        # Parse the date
        date_str = data.get('date')
        target_date = None
        if date_str:
            target_date = parse_nl_time(date_str, prefer_future=True)
            if not target_date:
                target_date = dateparser.parse(date_str, settings={'PREFER_DATES_FROM': 'future'})

        # Parse duration
        from ai_schedule_agent.utils.time_parser import parse_duration
        duration_str = data.get('duration', '1 hour')
        duration_td = parse_duration(duration_str)
        duration = int(duration_td.total_seconds() / 60) if duration_td else 60  # minutes

        # Get title and other details
        title = event_details.get('summary', 'New Event')
        description = event_details.get('description', '')
        location = event_details.get('location', '')

        logger.info(f"Check schedule request: date={target_date}, duration={duration}min, title={title}")

        # Now fetch calendar events and ask LLM to find optimal time
        suggested_time = self._ask_llm_for_optimal_time(
            target_date=target_date,
            duration=duration,
            title=title,
            description=description,
            location=location,
            original_request=original_text
        )

        result = {
            'action': 'check_schedule',
            'target_date': target_date,
            'duration': duration,
            'title': title,
            'description': description,
            'location': location,
            'llm_mode': True,
            'llm_response': llm_result.get('response'),
            'event_type': EventType.MEETING,
            'participants': [],
            'suggested_time': suggested_time  # LLM-suggested optimal time
        }

        return result

    def _convert_llm_result_to_dict(self, llm_result: Dict, original_text: str) -> Dict:
        """Convert LLM processing result to standard dict format

        Args:
            llm_result: Result from LLM agent
            original_text: Original user input

        Returns:
            Dictionary in standard format for scheduling
        """
        data = llm_result.get('data', {})

        # Parse start and end times using enhanced time parser
        start_time = None
        end_time = None

        start_time_str = data.get('start_time_str')
        end_time_str = data.get('end_time_str')

        # Parse start time
        if start_time_str:
            logger.debug(f"Parsing start_time_str: '{start_time_str}'")
            start_time = parse_nl_time(start_time_str, prefer_future=True)
            if not start_time:
                # Fallback to dateparser
                start_time = dateparser.parse(start_time_str, settings={'PREFER_DATES_FROM': 'future'})

            if start_time:
                logger.info(f"Successfully parsed start time: {start_time}")
            else:
                logger.warning(f"Failed to parse start_time_str: '{start_time_str}'")
        else:
            logger.warning("No start_time_str provided by LLM")

        # Check if end_time_str is a duration string or an actual end time
        duration = None
        if end_time_str:
            logger.debug(f"Parsing end_time_str: '{end_time_str}'")
            # Try to parse as duration first (e.g., "3 hours", "90 minutes", "2 hrs")
            from ai_schedule_agent.utils.time_parser import parse_duration
            duration_td = parse_duration(end_time_str)

            if duration_td:
                # It's a duration string
                duration = int(duration_td.total_seconds() / 60)  # Convert to minutes
                logger.info(f"Parsed duration: {duration} minutes from '{end_time_str}'")

                # Calculate end_time from start_time + duration
                if start_time:
                    end_time = start_time + duration_td
                else:
                    logger.warning("Cannot calculate end_time: start_time is None")
            else:
                # Not a duration, try to parse as actual end time
                end_time = parse_nl_time(end_time_str, prefer_future=True)
                if not end_time:
                    # Fallback to dateparser
                    end_time = dateparser.parse(end_time_str, settings={'PREFER_DATES_FROM': 'future'})

                # Calculate duration if both times available
                if start_time and end_time:
                    duration = int((end_time - start_time).total_seconds() / 60)  # minutes
                    logger.info(f"Calculated duration: {duration} minutes from time difference")
                else:
                    logger.warning(f"Failed to parse end_time_str as time: '{end_time_str}'")
        else:
            # No end time provided, default to 1 hour
            logger.warning("No end_time_str provided by LLM, defaulting to 1 hour")
            duration = 60
            if start_time:
                from datetime import timedelta
                end_time = start_time + timedelta(minutes=60)

        # Ensure we have at least duration if parsing failed
        if duration is None and start_time and end_time:
            duration = int((end_time - start_time).total_seconds() / 60)
        elif duration is None:
            duration = 60  # Default fallback

        result = {
            'action': 'create',
            'event_type': EventType.MEETING,  # Default, could be enhanced to detect from LLM
            'participants': data.get('participants', []),
            'datetime': start_time,
            'end_datetime': end_time,  # Add end datetime explicitly
            'duration': duration,
            'location': data.get('location', ''),
            'title': data.get('summary', 'New Event'),
            'description': data.get('description', ''),
            'llm_mode': True,
            'llm_response': llm_result.get('response', '')  # Keep LLM's response for user feedback
        }

        logger.info(f"Converted LLM result: title='{result['title']}', datetime={result['datetime']}, duration={result['duration']}min")
        return result

    def _extract_with_chinese_patterns(self, text: str) -> Dict:
        """Enhanced Chinese pattern extraction from 阿嚕米 Mock mode

        This method uses the exact pattern matching logic from 阿嚕米_archived/agent_main.py
        mock_handle() function to extract event details from Chinese text.

        Extracts event details using regex patterns optimized for Chinese text:
        - Brackets: 「」 "" 『』
        - Time ranges: 到 (to)
        - Relative dates: 今天/明天/後天
        - Duration: X小時
        - Action keywords: 安排/排/訂/預定

        Args:
            text: Natural language text (Chinese or mixed)

        Returns:
            Dict with 'title', 'datetime', 'end_datetime', 'duration' keys
        """
        result = {}

        # === 阿嚕米 Mock Mode: Title Extraction ===
        # Extract title from Chinese brackets or quotes (阿嚕米's pattern)
        summary = None
        # Pattern 1: Chinese/English quotes: 「」 "" 『』 (exact match from 阿嚕米)
        m = re.search(r'["\u201c\u201d\u300c\u300d\u300e\u300f](.+?)["\u201c\u201d\u300c\u300d\u300e\u300f]', text)
        if m:
            summary = m.group(1)
            logger.debug(f"阿嚕米 pattern (quoted): extracted title '{summary}'")
        else:
            # Pattern 2: Action keywords + optional 一個/個 + content (阿嚕米's pattern)
            # Exact regex from 阿嚕米: r'安排(?:一個|個)?(?:「([^」]+)」|(.+?)(?:，|,|。|$))'
            m2 = re.search(r'安排(?:一個|個)?(?:「([^」]+)」|(.+?)(?:，|,|。|$))', text)
            if m2:
                summary = m2.group(1) or m2.group(2)
                logger.debug(f"阿嚕米 pattern (action): extracted title '{summary}'")
            else:
                # Pattern 3: Extract event name after duration info (ASA enhancement)
                # Examples: "明天下午排3小時開會" -> "開會", "排1小時討論" -> "討論"
                duration_pattern = re.search(r'(\d+)\s*(?:小時|分鐘)(.+?)(?:，|,|。|$)', text)
                if duration_pattern:
                    summary = duration_pattern.group(2).strip()
                    logger.debug(f"Enhanced pattern (post-duration): extracted title '{summary}'")
                else:
                    # Pattern 4: Extract after time + action keyword (排/安排)
                    # Examples: "明天下午3點排開會" -> "開會"
                    time_action_pattern = re.search(r'(?:今天|明天|後天|本週|下週).*?\d+\s*點\s*(?:排|安排)(.+?)(?:，|,|。|$)', text)
                    if time_action_pattern:
                        summary = time_action_pattern.group(1).strip()
                        logger.debug(f"Enhanced pattern (after time+action): extracted title '{summary}'")

        if summary:
            result['title'] = summary.strip()
            logger.info(f"阿嚕米 Mock mode extracted title: '{result['title']}'")

        # Extract duration: X小時 or X分鐘
        duration_match = re.search(r'(\d+)\s*小時', text)
        if duration_match:
            hours = int(duration_match.group(1))
            result['duration'] = hours * 60  # Convert to minutes
            logger.debug(f"Chinese pattern extracted duration: {result['duration']} minutes ({hours} hours)")

        if not duration_match:
            minute_match = re.search(r'(\d+)\s*分鐘', text)
            if minute_match:
                result['duration'] = int(minute_match.group(1))
                logger.debug(f"Chinese pattern extracted duration: {result['duration']} minutes")

        # === 阿嚕米 Mock Mode: Time Range Extraction ===
        # Extract time range using '到' (to) pattern (exact logic from 阿嚕米)
        if '到' in text:
            parts = text.split('到')
            # Extract start time (after '時間是' if present) - 阿嚕米's logic
            start_str = parts[0].split('時間是')[-1].strip() if '時間是' in parts[0] else parts[0].strip()
            # Extract end time (before punctuation) - 阿嚕米's logic
            end_str = parts[1].split('。')[0].split('，')[0].strip()

            logger.debug(f"阿嚕米 time range: start_str='{start_str}', end_str='{end_str}'")

            # Use parse_nl_time (same as 阿嚕米's parse_nl_time from calendar_time_parser)
            start_dt = parse_nl_time(start_str)
            end_dt = parse_nl_time(end_str)

            # If end_dt parsing failed and it looks like just an hour (e.g., "4點" or "9點")
            # try to construct it from start_dt's date
            if start_dt and not end_dt and re.match(r'^\d{1,2}\s*點', end_str):
                hour_match = re.match(r'^(\d{1,2})\s*點', end_str)
                if hour_match:
                    from datetime import datetime, timedelta
                    hour = int(hour_match.group(1))

                    # Smart AM/PM detection based on start time and context
                    start_hour = start_dt.hour

                    # If hour is 1-12 and could be either AM or PM
                    if 1 <= hour <= 12:
                        # Check context for 下午/晚上 (afternoon/evening) in the full text
                        if '下午' in text or '晚上' in text:
                            # Afternoon/evening context - use PM (12-hour -> 24-hour)
                            if hour != 12:
                                hour = hour + 12 if hour < 12 else hour
                        # If start is in afternoon (12-18) and end hour is small (1-11)
                        elif 12 <= start_hour < 18 and hour < 12:
                            hour += 12  # Convert to PM
                        # If start is in evening (18-23) and end hour is small (1-11)
                        elif 18 <= start_hour and hour < 12:
                            hour += 12  # Convert to PM

                    # Construct end time on same day as start time
                    end_dt = start_dt.replace(hour=hour, minute=0, second=0)

                    # If end is still before or equal to start, something went wrong
                    if end_dt <= start_dt:
                        # Only add a day if it makes sense (e.g., overnight event)
                        if hour < 6:  # Late night/early morning hours
                            end_dt = end_dt + timedelta(days=1)
                        else:
                            # Otherwise, keep it on same day (user likely meant same day)
                            logger.warning(f"End time {hour}:00 is before start time {start_hour}:00 on same day")

                    logger.info(f"阿嚕米 constructed end time from hour '{end_str}': {end_dt} (hour={hour})")

            if start_dt:
                result['datetime'] = start_dt
                logger.info(f"阿嚕米 Mock mode extracted start time: {start_dt}")
            if end_dt:
                result['end_datetime'] = end_dt
                logger.info(f"阿嚕米 Mock mode extracted end time: {end_dt}")
                if start_dt:
                    # Calculate duration in minutes
                    result['duration'] = int((end_dt - start_dt).total_seconds() / 60)
                    logger.info(f"阿嚕米 Mock mode calculated duration: {result['duration']} minutes")

        # === 阿嚕米 Mock Mode: Single Time Extraction ===
        # Extract single time with relative date pattern (阿嚕米's exact pattern)
        if not result.get('datetime'):
            # Exact pattern from 阿嚕米: r'(今天|明天|後天|本週\S*|下週\S*).*?(\d{1,2})\s*點'
            m3 = re.search(r'(今天|明天|後天|本週\S*|下週\S*).*?(\d{1,2})\s*點', text)
            if m3:
                time_str = m3.group(0)
                logger.debug(f"阿嚕米 single time pattern matched: '{time_str}'")

                # Parse using parse_nl_time (same as 阿嚕米)
                dt = parse_nl_time(time_str)
                if dt:
                    result['datetime'] = dt
                    logger.info(f"阿嚕米 Mock mode extracted datetime: {dt}")
                    # If we have duration and datetime, calculate end_datetime
                    if result.get('duration') and not result.get('end_datetime'):
                        from datetime import timedelta
                        result['end_datetime'] = dt + timedelta(minutes=result['duration'])
                        logger.info(f"阿嚕米 calculated end_datetime: {result['end_datetime']}")
            else:
                # Fallback: Check for time period without specific time (ASA enhancement)
                # This is NOT in 阿嚕米's Mock mode, but useful for "明天下午" without specific hour
                period_pattern = re.search(r'(明天|今天|後天)(下午|上午|早上|中午|晚上|傍晚)', text)
                if period_pattern:
                    time_str = period_pattern.group(0)
                    # NO specific time - store time preference for scheduling engine
                    # Don't set datetime - let scheduling engine find optimal slot
                    time_period = None
                    if '下午' in time_str:
                        time_period = 'afternoon'
                        result['time_preference'] = {'period': 'afternoon', 'start_hour': 13, 'end_hour': 18}
                    elif '上午' in time_str or '早上' in time_str:
                        time_period = 'morning'
                        result['time_preference'] = {'period': 'morning', 'start_hour': 9, 'end_hour': 12}
                    elif '晚上' in time_str or '傍晚' in time_str:
                        time_period = 'evening'
                        result['time_preference'] = {'period': 'evening', 'start_hour': 18, 'end_hour': 21}
                    elif '中午' in time_str:
                        time_period = 'noon'
                        result['time_preference'] = {'period': 'noon', 'start_hour': 11, 'end_hour': 14}

                    # Store target date without time (scheduling engine will find slot)
                    date_only_str = period_pattern.group(1)  # 明天/今天/後天
                    dt = parse_nl_time(date_only_str)
                    if dt:
                        # Store as target_date instead of datetime
                        result['target_date'] = dt.date()
                        logger.info(f"Chinese pattern: target_date={dt.date()}, time_preference={time_period}, "
                                   f"let scheduling engine find optimal slot")

        # === 阿嚕米 Mock Mode: Default Duration Fallback ===
        # If we have datetime but no end_datetime and no duration, default to 1 hour (阿嚕米's logic)
        if result.get('datetime') and not result.get('end_datetime') and not result.get('duration'):
            from datetime import timedelta
            result['duration'] = 60  # 1 hour default (same as 阿嚕米)
            result['end_datetime'] = result['datetime'] + timedelta(hours=1)
            logger.info(f"阿嚕米 Mock mode: applied default 1-hour duration")

        # Log extracted fields for debugging
        extracted_fields = {k: v for k, v in result.items() if v is not None}
        logger.info(f"阿嚕米 Mock mode extraction complete: {extracted_fields}")
        return result

    def reset_conversation(self):
        """Reset LLM conversation history (if using LLM)"""
        if self.llm_agent:
            self.llm_agent.reset_conversation()
            logger.info("Conversation history reset")

    def is_using_llm(self) -> bool:
        """Check if processor is using LLM

        Returns:
            bool: True if LLM is enabled and available
        """
        return self.use_llm and self.llm_agent is not None
