"""
AI Schedule Agent - Intelligent Personal Scheduling Assistant
A comprehensive scheduling agent that integrates with Google Calendar and learns from user patterns
"""

__version__ = "1.0.0"
__author__ = "NYCU AOOP 2025 Group 6"

# Defer imports to speed up startup time
# Components will be imported when actually accessed
__all__ = [
    "ConfigManager",
    "EventType",
    "Priority",
    "Event",
    "UserProfile",
]

def __getattr__(name):
    """Lazy import main components on first access"""
    if name == "ConfigManager":
        from ai_schedule_agent.config.manager import ConfigManager
        return ConfigManager
    elif name == "EventType":
        from ai_schedule_agent.models.enums import EventType
        return EventType
    elif name == "Priority":
        from ai_schedule_agent.models.enums import Priority
        return Priority
    elif name == "Event":
        from ai_schedule_agent.models.event import Event
        return Event
    elif name == "UserProfile":
        from ai_schedule_agent.models.user_profile import UserProfile
        return UserProfile
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
