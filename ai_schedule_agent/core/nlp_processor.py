"""Natural Language Processing for scheduling requests"""

import re
from typing import Dict
import spacy
import dateparser

from ai_schedule_agent.models.enums import EventType
from ai_schedule_agent.config.manager import ConfigManager
from ai_schedule_agent.utils.logging import logger


class NLPProcessor:
    """Natural Language Processing for scheduling requests"""

    def __init__(self):
        config = ConfigManager()
        # Get spacy model from config
        spacy_model = config.get_setting('nlp', 'spacy_model', default='en_core_web_sm')
        try:
            self.nlp = spacy.load(spacy_model)
        except:
            # If spacy model not installed, use basic parsing
            self.nlp = None
            logger.warning(f"Spacy model '{spacy_model}' not found. Using basic NLP parsing.")

    def parse_scheduling_request(self, text: str) -> Dict:
        """Parse natural language scheduling request"""
        result = {
            'action': 'create',  # Default to create
            'event_type': EventType.MEETING,  # Default to meeting
            'participants': [],
            'datetime': None,
            'duration': None,
            'location': None,
            'title': None,
            'description': None
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
