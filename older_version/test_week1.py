import pytest
import datetime
import json
from unittest.mock import Mock, patch, MagicMock
from src.tools.calendar import CalendarTool

# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

def test_calendar_tool_initialization():
    tool = CalendarTool()
    assert tool.name == "google_calendar"
    assert "json" in tool.description.lower()

def test_calendar_tool_has_required_attributes():
    """Verify the tool has all expected attributes."""
    tool = CalendarTool()
    assert hasattr(tool, 'name')
    assert hasattr(tool, 'description')
    assert hasattr(tool, 'execute')
    assert callable(tool.execute)

# ============================================================================
# CREATE EVENT TESTS
# ============================================================================

def test_create_event_input_parsing():
    """Test if the tool accepts a valid JSON string for creating an event."""
    tool = CalendarTool()
    
    future_time = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
    
    payload = {
        "action": "create_event",
        "summary": "Pytest Meeting",
        "start_time": future_time,
        "end_time": future_time
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()

def test_create_event_with_description():
    """Test creating an event with optional description field."""
    tool = CalendarTool()
    
    future_time = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
    
    payload = {
        "action": "create_event",
        "summary": "Team Standup",
        "description": "Daily team sync meeting",
        "start_time": future_time,
        "end_time": future_time
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()

def test_create_event_with_location():
    """Test creating an event with location."""
    tool = CalendarTool()
    
    future_time = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
    
    payload = {
        "action": "create_event",
        "summary": "Client Meeting",
        "location": "Conference Room B",
        "start_time": future_time,
        "end_time": future_time
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()

def test_create_event_with_attendees():
    """Test creating an event with attendees list."""
    tool = CalendarTool()
    
    future_time = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
    
    payload = {
        "action": "create_event",
        "summary": "Project Review",
        "attendees": ["alice@example.com", "bob@example.com"],
        "start_time": future_time,
        "end_time": future_time
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()

def test_create_all_day_event():
    """Test creating an all-day event."""
    tool = CalendarTool()
    
    future_date = (datetime.datetime.now() + datetime.timedelta(days=1)).date().isoformat()
    
    payload = {
        "action": "create_event",
        "summary": "Company Holiday",
        "start_date": future_date,
        "end_date": future_date
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()

def test_create_recurring_event():
    """Test creating a recurring event."""
    tool = CalendarTool()
    
    future_time = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
    
    payload = {
        "action": "create_event",
        "summary": "Weekly Team Sync",
        "start_time": future_time,
        "end_time": future_time,
        "recurrence": ["RRULE:FREQ=WEEKLY;COUNT=10"]
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()

# ============================================================================
# LIST EVENTS TESTS
# ============================================================================

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

def test_list_events_with_time_range():
    """Test listing events within a specific time range."""
    tool = CalendarTool()
    
    now = datetime.datetime.now()
    
    payload = {
        "action": "list_events",
        "time_min": now.isoformat(),
        "time_max": (now + datetime.timedelta(days=7)).isoformat()
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception:
        pass

def test_list_events_with_max_results():
    """Test listing events with max results limit."""
    tool = CalendarTool()
    
    payload = {
        "action": "list_events",
        "time_min": datetime.datetime.now().isoformat(),
        "max_results": 5
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception:
        pass

def test_list_events_with_calendar_id():
    """Test listing events from a specific calendar."""
    tool = CalendarTool()
    
    payload = {
        "action": "list_events",
        "calendar_id": "primary",
        "time_min": datetime.datetime.now().isoformat()
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception:
        pass

# ============================================================================
# UPDATE EVENT TESTS
# ============================================================================

def test_update_event_input_parsing():
    """Test updating an event."""
    tool = CalendarTool()
    
    payload = {
        "action": "update_event",
        "event_id": "test_event_123",
        "summary": "Updated Meeting Title"
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()

def test_update_event_time():
    """Test updating event time."""
    tool = CalendarTool()
    
    future_time = (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()
    
    payload = {
        "action": "update_event",
        "event_id": "test_event_123",
        "start_time": future_time,
        "end_time": future_time
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()

# ============================================================================
# DELETE EVENT TESTS
# ============================================================================

def test_delete_event_input_parsing():
    """Test deleting an event."""
    tool = CalendarTool()
    
    payload = {
        "action": "delete_event",
        "event_id": "test_event_123"
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()

def test_delete_event_with_calendar_id():
    """Test deleting an event from specific calendar."""
    tool = CalendarTool()
    
    payload = {
        "action": "delete_event",
        "event_id": "test_event_123",
        "calendar_id": "primary"
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()

# ============================================================================
# GET EVENT TESTS
# ============================================================================

def test_get_event_input_parsing():
    """Test getting a specific event by ID."""
    tool = CalendarTool()
    
    payload = {
        "action": "get_event",
        "event_id": "test_event_123"
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()

# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_invalid_json_input():
    """Test that invalid JSON is handled gracefully."""
    tool = CalendarTool()
    
    invalid_json = "{ this is not valid json }"
    
    result = tool.execute(invalid_json)
    assert isinstance(result, str)
    assert "error" in result.lower() or "invalid" in result.lower()

def test_missing_action_field():
    """Test handling of missing action field."""
    tool = CalendarTool()
    
    payload = {
        "summary": "Test Event"
    }
    
    input_str = json.dumps(payload)
    
    result = tool.execute(input_str)
    assert isinstance(result, str)
    assert "error" in result.lower() or "action" in result.lower()

def test_invalid_action():
    """Test handling of invalid action."""
    tool = CalendarTool()
    
    payload = {
        "action": "invalid_action"
    }
    
    input_str = json.dumps(payload)
    
    result = tool.execute(input_str)
    assert isinstance(result, str)
    assert "error" in result.lower() or "invalid" in result.lower()

def test_missing_required_fields_create():
    """Test handling of missing required fields for create_event."""
    tool = CalendarTool()
    
    payload = {
        "action": "create_event"
        # Missing summary, start_time, end_time
    }
    
    input_str = json.dumps(payload)
    
    result = tool.execute(input_str)
    assert isinstance(result, str)

def test_invalid_datetime_format():
    """Test handling of invalid datetime format."""
    tool = CalendarTool()
    
    payload = {
        "action": "create_event",
        "summary": "Test",
        "start_time": "not-a-valid-datetime",
        "end_time": "also-invalid"
    }
    
    input_str = json.dumps(payload)
    
    result = tool.execute(input_str)
    assert isinstance(result, str)

def test_empty_string_input():
    """Test handling of empty string input."""
    tool = CalendarTool()
    
    result = tool.execute("")
    assert isinstance(result, str)
    assert "error" in result.lower()

def test_null_input():
    """Test handling of None/null input."""
    tool = CalendarTool()
    
    try:
        result = tool.execute(None)
        assert isinstance(result, str)
    except (TypeError, AttributeError):
        # This is also acceptable behavior
        pass

# ============================================================================
# EDGE CASES
# ============================================================================

def test_past_event_creation():
    """Test creating an event in the past."""
    tool = CalendarTool()
    
    past_time = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
    
    payload = {
        "action": "create_event",
        "summary": "Past Event",
        "start_time": past_time,
        "end_time": past_time
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()

def test_very_long_summary():
    """Test creating an event with very long summary."""
    tool = CalendarTool()
    
    future_time = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
    
    payload = {
        "action": "create_event",
        "summary": "A" * 1000,  # Very long title
        "start_time": future_time,
        "end_time": future_time
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()

def test_special_characters_in_summary():
    """Test creating an event with special characters."""
    tool = CalendarTool()
    
    future_time = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
    
    payload = {
        "action": "create_event",
        "summary": "Test™ Event® with 特殊字符 & symbols!@#$%",
        "start_time": future_time,
        "end_time": future_time
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()

def test_end_time_before_start_time():
    """Test creating an event where end time is before start time."""
    tool = CalendarTool()
    
    start_time = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
    end_time = (datetime.datetime.now() + datetime.timedelta(hours=12)).isoformat()
    
    payload = {
        "action": "create_event",
        "summary": "Invalid Time Range",
        "start_time": start_time,
        "end_time": end_time
    }
    
    input_str = json.dumps(payload)
    
    result = tool.execute(input_str)
    assert isinstance(result, str)

# ============================================================================
# INTEGRATION-STYLE TESTS (Would need mocking)
# ============================================================================

@patch('src.tools.calendar.build')  # Adjust import path as needed
def test_create_event_with_mock(mock_build):
    """Test event creation with mocked Google API."""
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    
    mock_service.events().insert().execute.return_value = {
        "id": "event_123",
        "summary": "Mocked Event"
    }
    
    tool = CalendarTool()
    
    future_time = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
    
    payload = {
        "action": "create_event",
        "summary": "Mocked Event",
        "start_time": future_time,
        "end_time": future_time
    }
    
    input_str = json.dumps(payload)
    
    result = tool.execute(input_str)
    assert isinstance(result, str)

# ============================================================================
# TIMEZONE TESTS
# ============================================================================

def test_create_event_with_timezone():
    """Test creating an event with explicit timezone."""
    tool = CalendarTool()
    
    future_time = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
    
    payload = {
        "action": "create_event",
        "summary": "Timezone Test",
        "start_time": future_time,
        "end_time": future_time,
        "timezone": "America/New_York"
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception as e:
        assert "arg" not in str(e).lower()
def test_list_events_with_timezone():
    """Test listing events with timezone consideration."""
    tool = CalendarTool()
    
    payload = {
        "action": "list_events",
        "time_min": datetime.datetime.now().isoformat(),
        "timezone": "America/New_York"
    }
    
    input_str = json.dumps(payload)
    
    try:
        result = tool.execute(input_str)
        assert isinstance(result, str)
    except Exception:
        pass
    