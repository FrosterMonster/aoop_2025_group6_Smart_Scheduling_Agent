import pytest
import os
import sys

# Add project root to path so we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.weather import WeatherTool
from src.tools.preferences import PreferenceTool
from src.database import init_db, set_preference, get_preference

# --- TEST 1: Database Logic ---
def test_database_persistence():
    """Test if we can save and retrieve data from SQLite."""
    init_db()
    set_preference("test_key", "test_value")
    result = get_preference("test_key")
    assert result == "test_value"

# --- TEST 2: Preference Tool String Parsing ---
def test_preference_tool_parsing():
    """Test if the tool correctly parses the 'save:' command."""
    tool = PreferenceTool()
    
    # Test Save
    response = tool.execute("save: favorite_color: blue")
    assert "Successfully saved" in response
    
    # Verify it was saved
    saved_val = get_preference("favorite_color")
    assert saved_val == "blue"

# --- TEST 3: Weather Tool Logic ---
def test_weather_determinism():
    """Test if the weather tool returns consistent results for the same date."""
    tool = WeatherTool()
    
    result1 = tool.execute("2025-01-01")
    result2 = tool.execute("2025-01-01")
    
    # The weather for the same date should always be identical (deterministic)
    assert result1 == result2
    assert "Forecast" in result1

# --- TEST 4: Calendar Tool Mock (Simulated) ---
def test_calendar_input_validation():
    from src.tools.calendar import CalendarTool
    
    tool = CalendarTool()
    assert tool.name == "google_calendar"
    # FIX: Convert description to lower case before checking
    assert "json" in tool.description.lower()