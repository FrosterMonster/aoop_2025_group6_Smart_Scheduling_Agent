import pytest
from src.tools.calendar import CalendarTool
# Mocking the Google API to avoid real calls during tests
from unittest.mock import MagicMock

def test_calendar_tool_parsing():
    tool = CalendarTool()
    # Test if it handles invalid input gracefully
    result = tool.execute("invalid json garbage")
    assert "Error" in result

def test_calendar_date_parsing():
    # If you have helper functions for date parsing, test them here
    pass