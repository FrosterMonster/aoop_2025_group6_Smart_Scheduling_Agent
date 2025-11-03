"""
AI Schedule Agent - Intelligent Personal Scheduling Assistant
A comprehensive scheduling agent that integrates with Google Calendar and learns from user patterns
"""

__version__ = "1.0.0"
__author__ = "NYCU AOOP 2025 Group 6"

# Import main components for easy access
from ai_schedule_agent.config.manager import ConfigManager
from ai_schedule_agent.models.enums import EventType, Priority
from ai_schedule_agent.models.event import Event
from ai_schedule_agent.models.user_profile import UserProfile

__all__ = [
    "ConfigManager",
    "EventType",
    "Priority",
    "Event",
    "UserProfile",
]
