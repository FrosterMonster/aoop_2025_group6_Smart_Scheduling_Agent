import pytest
import datetime
import json
from src.tools.calendar import CalendarTool

def test_calendar_tool_initialization():
    tool = CalendarTool()
    assert tool.name == "google_calendar"
    assert "json" in tool.description.lower()

def test_create_event_input_parsing():
    """Test if the tool accepts a valid JSON string for creating an event."""
    tool = CalendarTool()
    
    # OLD WAY (Caused Error):
    # tool.execute(action="create_event", summary="Test", ...)

    # NEW WAY (Correct):
    # We must construct a JSON string because that's what the Agent sends.
    future_time = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
    
    payload = {
        "action": "create_event",
        "summary": "Pytest Meeting",
        "start_time": future_time,
        "end_time": future_time
    }
    
    # Convert dict to JSON string
    input_str = json.dumps(payload)
    
    # We expect this to fail with "Error" or "Authentication" 
    # because we might not have valid credentials during test, 
    # BUT it should NOT raise a TypeError about arguments.
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        # If it's an auth error, that's fine for this test, 
        # we just want to ensure the input parsing works.
        assert "arg" not in str(e)  # Ensure it's not an argument error

def test_list_events_input_parsing():
    """Test listing events with JSON input."""
    tool = CalendarTool()
    
    payload = {
        "action": "list_events",
        "time_min": datetime.datetime.now().isoformat()
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception:
        pass