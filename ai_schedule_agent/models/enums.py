"""Enumeration types for the scheduling system"""

from enum import Enum


class EventType(Enum):
    """Event categorization types"""
    DAILY = "daily"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    FOCUS = "focus"
    MEETING = "meeting"
    PERSONAL = "personal"
    BREAK = "break"


class Priority(Enum):
    """Event priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
