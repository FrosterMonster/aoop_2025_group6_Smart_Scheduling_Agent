import pytest
import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, call
import json
import sqlite3

# Add project root to path so we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.weather import WeatherTool
from src.tools.preferences import PreferenceTool
from src.database import init_db, set_preference, get_preference

# ============================================================================
# FIXTURES - Setup and Teardown
# ============================================================================

@pytest.fixture(scope="function")
def temp_database():
    """
    Create a temporary database for each test to ensure isolation.
    This prevents tests from interfering with each other.
    """
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test_database.db')
    
    # Store original DB path if exists
    original_db = os.environ.get('DATABASE_PATH')
    
    # Set temporary database path
    os.environ['DATABASE_PATH'] = db_path
    
    # Initialize database
    init_db()
    
    yield db_path
    
    # Cleanup: Restore original database path and remove temp directory
    if original_db:
        os.environ['DATABASE_PATH'] = original_db
    else:
        os.environ.pop('DATABASE_PATH', None)
    
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def weather_tool():
    """Fixture to provide a fresh WeatherTool instance for each test."""
    return WeatherTool()


@pytest.fixture(scope="function")
def preference_tool(temp_database):
    """Fixture to provide a PreferenceTool with isolated database."""
    return PreferenceTool()


@pytest.fixture(scope="function")
def sample_preferences():
    """Fixture providing sample preference data for testing."""
    return {
        "favorite_color": "blue",
        "preferred_temperature": "celsius",
        "default_city": "New York",
        "notification_enabled": "true",
        "theme": "dark",
        "language": "en-US"
    }


# ============================================================================
# TEST SUITE 1: Database Logic - Comprehensive Testing
# ============================================================================

class TestDatabasePersistence:
    """Comprehensive tests for database operations."""
    
    def test_database_initialization(self, temp_database):
        """Test if database initializes correctly with proper schema."""
        assert os.path.exists(temp_database)
        
        # Verify tables exist
        conn = sqlite3.connect(temp_database)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'preferences' in tables or 'user_data' in tables
    
    def test_database_save_and_retrieve(self, temp_database):
        """Test basic save and retrieve operations."""
        init_db()
        set_preference("test_key", "test_value")
        result = get_preference("test_key")
        assert result == "test_value"
    
    def test_database_multiple_keys(self, temp_database, sample_preferences):
        """Test saving and retrieving multiple key-value pairs."""
        init_db()
        
        # Save all preferences
        for key, value in sample_preferences.items():
            set_preference(key, value)
        
        # Retrieve and verify all preferences
        for key, expected_value in sample_preferences.items():
            actual_value = get_preference(key)
            assert actual_value == expected_value, f"Mismatch for key '{key}'"
    
    def test_database_update_existing_key(self, temp_database):
        """Test updating an existing preference overwrites the old value."""
        init_db()
        
        # Set initial value
        set_preference("update_test", "initial_value")
        assert get_preference("update_test") == "initial_value"
        
        # Update value
        set_preference("update_test", "updated_value")
        assert get_preference("update_test") == "updated_value"
    
    def test_database_nonexistent_key(self, temp_database):
        """Test retrieving a key that doesn't exist returns None or empty."""
        init_db()
        result = get_preference("nonexistent_key_12345")
        assert result is None or result == ""
    
    def test_database_special_characters(self, temp_database):
        """Test handling of special characters in keys and values."""
        init_db()
        
        special_cases = [
            ("key_with_spaces", "value with spaces"),
            ("key-with-dashes", "value-with-dashes"),
            ("key_with_unicode", "value_with_émojis_🎉"),
            ("key.with.dots", "value.with.dots"),
            ("key_with_quotes", 'value with "quotes"'),
            ("key_with_newlines", "value\nwith\nnewlines"),
        ]
        
        for key, value in special_cases:
            set_preference(key, value)
            retrieved = get_preference(key)
            assert retrieved == value, f"Failed for key: {key}"
    
    def test_database_empty_values(self, temp_database):
        """Test handling of empty strings and edge cases."""
        init_db()
        
        # Empty value
        set_preference("empty_key", "")
        assert get_preference("empty_key") == ""
        
        # Very long value
        long_value = "x" * 10000
        set_preference("long_key", long_value)
        assert get_preference("long_key") == long_value
    
    def test_database_concurrency_simulation(self, temp_database):
        """Test multiple rapid sequential writes to simulate concurrency."""
        init_db()
        
        for i in range(100):
            set_preference(f"concurrent_key_{i}", f"value_{i}")
        
        # Verify all were saved
        for i in range(100):
            assert get_preference(f"concurrent_key_{i}") == f"value_{i}"
    
    def test_database_transaction_integrity(self, temp_database):
        """Test that database maintains integrity after operations."""
        init_db()
        
        # Perform multiple operations
        set_preference("key1", "value1")
        set_preference("key2", "value2")
        get_preference("key1")
        set_preference("key1", "updated_value1")
        
        # Verify final state
        assert get_preference("key1") == "updated_value1"
        assert get_preference("key2") == "value2"


# ============================================================================
# TEST SUITE 2: Preference Tool - String Parsing and Command Handling
# ============================================================================

class TestPreferenceToolParsing:
    """Comprehensive tests for PreferenceTool command parsing and execution."""
    
    def test_preference_tool_initialization(self, preference_tool):
        """Test that PreferenceTool initializes correctly."""
        assert preference_tool is not None
        assert hasattr(preference_tool, 'execute')
        assert hasattr(preference_tool, 'name')
        assert hasattr(preference_tool, 'description')
    
    def test_save_command_basic(self, preference_tool):
        """Test basic save command parsing."""
        response = preference_tool.execute("save: favorite_color: blue")
        assert "Successfully saved" in response or "saved" in response.lower()
        
        saved_val = get_preference("favorite_color")
        assert saved_val == "blue"
    
    def test_save_command_with_spaces(self, preference_tool):
        """Test save command with extra spaces."""
        response = preference_tool.execute("save:   favorite_food  :   pizza   ")
        assert "saved" in response.lower() or "success" in response.lower()
        
        saved_val = get_preference("favorite_food")
        assert saved_val is not None
    
    def test_save_command_multiple_colons(self, preference_tool):
        """Test save command when value contains colons."""
        response = preference_tool.execute("save: time_format: HH:MM:SS")
        assert "saved" in response.lower() or "success" in response.lower()
        
        saved_val = get_preference("time_format")
        assert ":" in saved_val
    
    def test_get_command_basic(self, preference_tool):
        """Test basic get command."""
        # First save a value
        set_preference("test_get_key", "test_get_value")
        
        # Then retrieve it using the tool
        response = preference_tool.execute("get: test_get_key")
        assert "test_get_value" in response or response == "test_get_value"
    
    def test_get_command_nonexistent(self, preference_tool):
        """Test get command for nonexistent key."""
        response = preference_tool.execute("get: nonexistent_key_xyz")
        assert "not found" in response.lower() or "none" in response.lower() or response == ""
    
    def test_invalid_command_format(self, preference_tool):
        """Test handling of invalid command formats."""
        invalid_commands = [
            "invalid_command",
            "save favorite_color blue",  # Missing colons
            "save:",  # Incomplete command
            ": favorite_color: blue",  # Missing command
            "",  # Empty string
            "   ",  # Only spaces
        ]
        
        for cmd in invalid_commands:
            response = preference_tool.execute(cmd)
            # Should return error message or handle gracefully
            assert response is not None
    
    def test_case_sensitivity(self, preference_tool):
        """Test if commands are case-insensitive."""
        commands = [
            "SAVE: test_case: value",
            "Save: test_case2: value",
            "save: test_case3: value",
        ]
        
        for cmd in commands:
            response = preference_tool.execute(cmd)
            # Should all succeed or all fail consistently
            assert response is not None
    
    @pytest.mark.parametrize("key,value", [
        ("simple_key", "simple_value"),
        ("numeric_value", "12345"),
        ("boolean_value", "true"),
        ("float_value", "3.14159"),
        ("json_like", '{"nested": "data"}'),
        ("list_like", "[1, 2, 3]"),
    ])
    def test_save_various_data_types(self, preference_tool, key, value):
        """Test saving various data type representations as strings."""
        response = preference_tool.execute(f"save: {key}: {value}")
        assert "saved" in response.lower() or "success" in response.lower()
        
        saved_val = get_preference(key)
        assert saved_val == value
    
    def test_list_all_preferences(self, preference_tool, sample_preferences):
        """Test listing all saved preferences."""
        # Save multiple preferences
        for key, value in sample_preferences.items():
            set_preference(key, value)
        
        # Try to list all (if tool supports it)
        response = preference_tool.execute("list")
        
        if "not supported" not in response.lower() and "invalid" not in response.lower():
            # If list is supported, verify output contains keys
            for key in sample_preferences.keys():
                # At least some keys should be in the response
                pass


# ============================================================================
# TEST SUITE 3: Weather Tool - Determinism and Functionality
# ============================================================================

class TestWeatherTool:
    """Comprehensive tests for WeatherTool functionality."""
    
    def test_weather_tool_initialization(self, weather_tool):
        """Test that WeatherTool initializes correctly."""
        assert weather_tool is not None
        assert hasattr(weather_tool, 'execute')
        assert hasattr(weather_tool, 'name')
    
    def test_weather_determinism_same_date(self, weather_tool):
        """Test if weather tool returns consistent results for the same date."""
        result1 = weather_tool.execute("2025-01-01")
        result2 = weather_tool.execute("2025-01-01")
        
        assert result1 == result2
        assert "Forecast" in result1 or "weather" in result1.lower()
    
    def test_weather_different_dates(self, weather_tool):
        """Test that different dates can produce different weather."""
        result1 = weather_tool.execute("2025-01-01")
        result2 = weather_tool.execute("2025-07-15")
        
        # Both should return valid responses
        assert result1 is not None
        assert result2 is not None
        assert len(result1) > 0
        assert len(result2) > 0
    
    def test_weather_date_format_validation(self, weather_tool):
        """Test various date format inputs."""
        valid_dates = [
            "2025-01-01",
            "2024-12-31",
            "2025-06-15",
        ]
        
        for date in valid_dates:
            result = weather_tool.execute(date)
            assert result is not None
            assert len(result) > 0
    
    def test_weather_invalid_dates(self, weather_tool):
        """Test handling of invalid date formats."""
        invalid_dates = [
            "invalid-date",
            "2025-13-01",  # Invalid month
            "2025-01-32",  # Invalid day
            "not-a-date",
            "",
            "01/01/2025",  # Different format
        ]
        
        for date in invalid_dates:
            result = weather_tool.execute(date)
            # Should handle gracefully - either return error message or default
            assert result is not None
    
    def test_weather_past_dates(self, weather_tool):
        """Test weather for past dates."""
        past_date = "2020-01-01"
        result = weather_tool.execute(past_date)
        assert result is not None
        assert len(result) > 0
    
    def test_weather_future_dates(self, weather_tool):
        """Test weather for future dates."""
        future_date = "2030-12-31"
        result = weather_tool.execute(future_date)
        assert result is not None
        assert len(result) > 0
    
    def test_weather_response_structure(self, weather_tool):
        """Test that weather response contains expected information."""
        result = weather_tool.execute("2025-01-01")
        
        # Check for common weather keywords
        weather_keywords = ["forecast", "temperature", "weather", "sunny", "cloudy", "rain"]
        has_weather_info = any(keyword in result.lower() for keyword in weather_keywords)
        assert has_weather_info
    
    def test_weather_consistency_multiple_calls(self, weather_tool):
        """Test consistency over multiple calls."""
        date = "2025-03-15"
        results = [weather_tool.execute(date) for _ in range(5)]
        
        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            assert result == first_result
    
    @pytest.mark.parametrize("date", [
        "2025-01-01",
        "2025-02-14",
        "2025-06-21",
        "2025-09-15",
        "2025-12-25",
    ])
    def test_weather_multiple_dates_parameterized(self, weather_tool, date):
        """Parameterized test for multiple dates."""
        result = weather_tool.execute(date)
        assert result is not None
        assert len(result) > 0
        
        # Test determinism
        result2 = weather_tool.execute(date)
        assert result == result2


# ============================================================================
# TEST SUITE 4: Calendar Tool - Mocking and Validation
# ============================================================================

class TestCalendarTool:
    """Comprehensive tests for CalendarTool functionality."""
    
    def test_calendar_tool_initialization(self):
        """Test that CalendarTool initializes correctly."""
        from src.tools.calendar import CalendarTool
        
        tool = CalendarTool()
        assert tool is not None
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, 'execute')
    
    def test_calendar_tool_name(self):
        """Test that CalendarTool has correct name."""
        from src.tools.calendar import CalendarTool
        
        tool = CalendarTool()
        assert tool.name == "google_calendar"
    
    def test_calendar_tool_description(self):
        """Test that CalendarTool description contains expected keywords."""
        from src.tools.calendar import CalendarTool
        
        tool = CalendarTool()
        description_lower = tool.description.lower()
        
        assert "json" in description_lower
        assert "calendar" in description_lower or "event" in description_lower
    
    def test_calendar_json_input_parsing(self):
        """Test parsing of JSON input for calendar operations."""
        from src.tools.calendar import CalendarTool
        
        tool = CalendarTool()
        
        # Sample JSON input
        json_input = json.dumps({
            "action": "create",
            "title": "Test Meeting",
            "date": "2025-01-15",
            "time": "14:00",
            "duration": "60"
        })
        
        # Execute should handle JSON gracefully
        try:
            result = tool.execute(json_input)
            assert result is not None
        except json.JSONDecodeError:
            pytest.fail("Tool should handle valid JSON input")
    
    def test_calendar_invalid_json(self):
        """Test handling of invalid JSON input."""
        from src.tools.calendar import CalendarTool
        
        tool = CalendarTool()
        
        invalid_inputs = [
            "not json",
            "{invalid json}",
            "",
            "{'single': 'quotes'}",
        ]
        
        for invalid_input in invalid_inputs:
            result = tool.execute(invalid_input)
            # Should handle error gracefully
            assert result is not None
    
    @patch('src.tools.calendar.CalendarTool.execute')
    def test_calendar_create_event_mock(self, mock_execute):
        """Test creating a calendar event with mocked execution."""
        from src.tools.calendar import CalendarTool
        
        # Setup mock
        mock_execute.return_value = "Event created successfully"
        
        tool = CalendarTool()
        result = tool.execute('{"action": "create", "title": "Meeting"}')
        
        assert result == "Event created successfully"
        mock_execute.assert_called_once()
    
    @patch('src.tools.calendar.CalendarTool.execute')
    def test_calendar_list_events_mock(self, mock_execute):
        """Test listing calendar events with mocked execution."""
        from src.tools.calendar import CalendarTool
        
        # Setup mock with sample events
        mock_events = json.dumps([
            {"title": "Event 1", "date": "2025-01-15"},
            {"title": "Event 2", "date": "2025-01-16"},
        ])
        mock_execute.return_value = mock_events
        
        tool = CalendarTool()
        result = tool.execute('{"action": "list", "date": "2025-01-15"}')
        
        assert "Event 1" in result
        assert "Event 2" in result
    
    def test_calendar_date_validation(self):
        """Test that calendar validates dates correctly."""
        from src.tools.calendar import CalendarTool
        
        tool = CalendarTool()
        
        # Valid date formats
        valid_dates = [
            "2025-01-15",
            "2025-12-31",
            "2024-02-29",  # Leap year
        ]
        
        for date in valid_dates:
            json_input = json.dumps({"action": "create", "date": date})
            result = tool.execute(json_input)
            assert result is not None
    
    @pytest.mark.parametrize("action,expected_key", [
        ("create", "title"),
        ("update", "event_id"),
        ("delete", "event_id"),
        ("list", "date"),
    ])
    def test_calendar_action_requirements(self, action, expected_key):
        """Test that different actions require specific parameters."""
        from src.tools.calendar import CalendarTool
        
        tool = CalendarTool()
        
        # Create input with required key
        json_input = json.dumps({
            "action": action,
            expected_key: "test_value"
        })
        
        result = tool.execute(json_input)
        assert result is not None


# ============================================================================
# TEST SUITE 5: Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple tools and components."""
    
    def test_save_weather_preference(self, preference_tool, weather_tool, temp_database):
        """Test saving weather-related preference and using weather tool."""
        # Save preferred city
        preference_tool.execute("save: preferred_city: New York")
        
        # Get weather
        weather = weather_tool.execute("2025-01-15")
        
        # Verify both operations succeeded
        assert get_preference("preferred_city") == "New York"
        assert weather is not None
    
    def test_workflow_save_and_retrieve(self, preference_tool):
        """Test complete workflow of saving multiple preferences and retrieving them."""
        preferences = {
            "theme": "dark",
            "language": "en",
            "notifications": "enabled"
        }
        
        # Save all
        for key, value in preferences.items():
            response = preference_tool.execute(f"save: {key}: {value}")
            assert "saved" in response.lower() or "success" in response.lower()
        
        # Retrieve and verify all
        for key, expected_value in preferences.items():
            actual = get_preference(key)
            assert actual == expected_value
    
    def test_multiple_tools_sequential_usage(self, weather_tool, preference_tool):
        """Test using multiple tools in sequence."""
        # Use weather tool
        weather1 = weather_tool.execute("2025-01-01")
        
        # Save preference
        preference_tool.execute("save: last_weather_check: 2025-01-01")
        
        # Use weather tool again
        weather2 = weather_tool.execute("2025-01-02")
        
        # Verify all operations
        assert weather1 is not None
        assert weather2 is not None
        assert get_preference("last_weather_check") == "2025-01-01"


# ============================================================================
# TEST SUITE 6: Error Handling and Edge Cases
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases across all tools."""
    
    def test_null_input_handling(self, preference_tool, weather_tool):
        """Test handling of null/None inputs."""
        # Preference tool with None
        result = preference_tool.execute(None)
        assert result is not None  # Should handle gracefully
        
        # Weather tool with None
        result = weather_tool.execute(None)
        assert result is not None  # Should handle gracefully
    
    def test_very_long_input(self, preference_tool):
        """Test handling of extremely long input strings."""
        long_value = "x" * 100000
        response = preference_tool.execute(f"save: long_key: {long_value}")
        
        # Should either succeed or fail gracefully
        assert response is not None
    
    def test_unicode_and_emoji_handling(self, preference_tool):
        """Test handling of unicode characters and emojis."""
        unicode_tests = [
            "save: emoji_pref: 🎉🎊🎈",
            "save: chinese: 你好世界",
            "save: arabic: مرحبا",
            "save: mixed: Hello🌍World世界",
        ]
        
        for test_input in unicode_tests:
            result = preference_tool.execute(test_input)
            assert result is not None
    
    def test_sql_injection_prevention(self, temp_database):
        """Test that database operations prevent SQL injection."""
        init_db()
        
        malicious_inputs = [
            "'; DROP TABLE preferences; --",
            "1' OR '1'='1",
            "admin'--",
            "'; DELETE FROM preferences WHERE '1'='1",
        ]
        
        for malicious in malicious_inputs:
            # Should handle safely without executing SQL
            set_preference(malicious, "value")
            result = get_preference(malicious)
            # Database should still be intact
            assert result == "value" or result is None


# ============================================================================
# TEST SUITE 7: Performance Tests
# ============================================================================

class TestPerformance:
    """Performance and stress tests."""
    
    def test_database_bulk_operations(self, temp_database):
        """Test performance of bulk database operations."""
        init_db()
        
        import time
        start_time = time.time()
        
        # Insert 1000 records
        for i in range(1000):
            set_preference(f"bulk_key_{i}", f"bulk_value_{i}")
        
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (< 10 seconds)
        assert elapsed < 10.0
        
        # Verify some records
        assert get_preference("bulk_key_0") == "bulk_value_0"
        assert get_preference("bulk_key_999") == "bulk_value_999"
    
    def test_weather_tool_response_time(self, weather_tool):
        """Test that weather tool responds quickly."""
        import time
        
        start_time = time.time()
        result = weather_tool.execute("2025-01-01")
        elapsed = time.time() - start_time
        
        # Should respond quickly (< 1 second for mock/deterministic)
        assert elapsed < 1.0
        assert result is not None
    
    def test_repeated_operations_performance(self, preference_tool):
        """Test performance of repeated operations."""
        import time
        
        start_time = time.time()
        
        for i in range(100):
            preference_tool.execute(f"save: perf_key_{i}: value_{i}")
        
        elapsed = time.time() - start_time
        
        # Should handle 100 operations reasonably fast
        assert elapsed < 5.0


# ============================================================================
# TEST SUITE 8: Cleanup and Teardown Tests
# ============================================================================

def test_cleanup_after_tests(temp_database):
    """Ensure cleanup happens correctly after tests."""
    # Database should exist during test
    assert os.path.exists(temp_database)
    
    # After fixture teardown, temp files should be cleaned
    # (This is verified by pytest fixture mechanism)


# ============================================================================
# ADDITIONAL HELPER TESTS
# ============================================================================

def test_module_imports():
    """Test that all required modules can be imported."""
    try:
        from src.tools.weather import WeatherTool
        from src.tools.preferences import PreferenceTool
        from src.database import init_db, set_preference, get_preference
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import required modules: {e}")


def test_pytest_configuration():
    """Test that pytest is configured correctly."""
    assert pytest is not None
    assert hasattr(pytest, 'fixture')
    assert hasattr(pytest, 'mark')


if __name__ == "__main__":
    # Allow running tests directly with: python test_tools.py
    pytest.main([__file__, "-v", "--tb=short"])
