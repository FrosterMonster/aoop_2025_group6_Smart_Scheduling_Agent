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
            'action': None,
            'event_type': None,
            'participants': [],
            'datetime': None,
            'duration': None,
            'location': None,
            'title': None
        }

        # Extract datetime
        parsed_date = dateparser.parse(text, settings={'PREFER_DATES_FROM': 'future'})
        if parsed_date:
            result['datetime'] = parsed_date

        # Basic keyword extraction
        text_lower = text.lower()

        # Determine action
        if any(word in text_lower for word in ['schedule', 'book', 'arrange', 'set up']):
            result['action'] = 'create'
        elif any(word in text_lower for word in ['reschedule', 'move', 'change']):
            result['action'] = 'reschedule'
        elif any(word in text_lower for word in ['cancel', 'delete', 'remove']):
            result['action'] = 'cancel'

        # Determine event type
        if 'meeting' in text_lower:
            result['event_type'] = EventType.MEETING
        elif 'focus' in text_lower or 'deep work' in text_lower:
            result['event_type'] = EventType.FOCUS
        elif 'break' in text_lower:
            result['event_type'] = EventType.BREAK

        # Extract participants (email patterns)
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        result['participants'] = emails

        # Extract duration
        duration_patterns = [
            (r'(\d+)\s*hour', lambda x: int(x) * 60),
            (r'(\d+)\s*minute', lambda x: int(x)),
            (r'(\d+)\s*min', lambda x: int(x))
        ]

        for pattern, converter in duration_patterns:
            match = re.search(pattern, text_lower)
            if match:
                result['duration'] = converter(match.group(1))
                break

        # Extract title (simplified - take the quoted text or main noun phrase)
        quoted = re.findall(r'"([^"]*)"', text)
        if quoted:
            result['title'] = quoted[0]

        return result
