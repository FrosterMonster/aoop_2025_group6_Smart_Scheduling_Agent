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

    def __init__(self, use_llm: Optional[bool] = None):
        """Initialize NLP Processor

        Args:
            use_llm: If True, use LLM for processing. If False, use rule-based.
                     If None, auto-detect based on config and API key availability.
        """
        self.config = ConfigManager()

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
        if self.use_llm:
            self._ensure_llm_initialized()  # Lazy load LLM on first use

        if self.use_llm and self.llm_agent:
            try:
                logger.info(f"Processing with LLM: '{text}'")
                llm_result = self.llm_agent.process_request(text)

                if llm_result.get('success') and llm_result.get('action') == 'schedule_event':
                    # Convert LLM result to expected format
                    return self._convert_llm_result_to_dict(llm_result, text)
                elif llm_result.get('success') and llm_result.get('action') == 'conversation':
                    # LLM responded but didn't schedule - return conversation result
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
        result = {
            'action': 'create',  # Default to create
            'event_type': EventType.MEETING,  # Default to meeting
            'participants': [],
            'datetime': None,
            'duration': None,
            'location': None,
            'title': None,
            'description': None,
            'llm_mode': False
        }

        # Basic keyword extraction
        text_lower = text.lower()
        original_text = text

        # Determine action
        if any(word in text_lower for word in ['schedule', 'book', 'arrange', 'set up', 'add', 'create']):
            result['action'] = 'create'
        elif any(word in text_lower for word in ['reschedule', 'move', 'change']):
            result['action'] = 'reschedule'
        elif any(word in text_lower for word in ['cancel', 'delete', 'remove']):
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

        # Extract title (smart extraction)
        title = None

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
        logger.info(f"NLP Parse: '{text}' -> {result}")

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

        if start_time_str:
            start_time = parse_nl_time(start_time_str, prefer_future=True)
            if not start_time:
                # Fallback to dateparser
                start_time = dateparser.parse(start_time_str, settings={'PREFER_DATES_FROM': 'future'})

        if end_time_str:
            end_time = parse_nl_time(end_time_str, prefer_future=True)
            if not end_time:
                # Fallback to dateparser
                end_time = dateparser.parse(end_time_str, settings={'PREFER_DATES_FROM': 'future'})

        # Calculate duration if both times available
        duration = None
        if start_time and end_time:
            duration = int((end_time - start_time).total_seconds() / 60)  # minutes

        result = {
            'action': 'create',
            'event_type': EventType.MEETING,  # Default, could be enhanced to detect from LLM
            'participants': data.get('participants', []),
            'datetime': start_time,
            'end_datetime': end_time,  # Add end datetime explicitly
            'duration': duration,
            'location': data.get('location'),
            'title': data.get('summary', 'New Event'),
            'description': data.get('description'),
            'llm_mode': True,
            'llm_response': llm_result.get('response')  # Keep LLM's response for user feedback
        }

        logger.info(f"Converted LLM result: {result}")
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
