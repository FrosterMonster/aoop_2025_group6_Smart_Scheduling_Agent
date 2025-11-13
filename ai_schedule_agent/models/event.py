"""Event data model"""

import datetime
from dataclasses import dataclass, field
from typing import List
from ai_schedule_agent.models.enums import EventType, Priority


@dataclass
class Event:
    """Event data model with Google Calendar integration support"""
    title: str
    description: str = ""
    start_time: datetime.datetime = None
    end_time: datetime.datetime = None
    event_type: EventType = EventType.MEETING
    priority: Priority = Priority.MEDIUM
    location: str = ""
    is_virtual: bool = False
    participants: List[str] = field(default_factory=list)
    required_resources: List[str] = field(default_factory=list)
    prep_time: int = 0  # minutes
    followup_time: int = 0  # minutes
    is_flexible: bool = True
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # event IDs
    google_event_id: str = ""
    recurrence_rule: str = ""  # RRULE for recurring events

    def to_google_event(self):
        """Convert to Google Calendar event format"""
        event = {
            'summary': self.title,
            'description': self.description,
            'start': {
                'dateTime': self.start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': self.end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'location': self.location,
            'attendees': [{'email': p} for p in self.participants],
            'extendedProperties': {
                'private': {
                    'eventType': self.event_type.value,
                    'priority': str(self.priority.value),
                    'isFlexible': str(self.is_flexible),
                    'tags': ','.join(self.tags),
                    'prepTime': str(self.prep_time),
                    'followupTime': str(self.followup_time),
                }
            }
        }

        if self.recurrence_rule:
            event['recurrence'] = [self.recurrence_rule]

        return event
