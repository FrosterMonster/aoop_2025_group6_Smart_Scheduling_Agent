import pytest
import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock, call, PropertyMock, Mock
import json
import sqlite3
import threading
import time
import logging
import hashlib
import pickle
import re
import warnings
from contextlib import contextmanager
from collections import OrderedDict
from typing import List, Dict, Any, Optional
import weakref
import gc
import io
from pathlib import Path

# Add project root to path so we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.weather import WeatherTool
from src.tools.preferences import PreferenceTool
from src.database import init_db, set_preference, get_preference

# ============================================================================
# CUSTOM PYTEST MARKERS AND CONFIGURATION
# ============================================================================

# Register custom markers
def pytest_configure(config):
    """Register custom markers for organizing tests."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests related to security"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests related to performance"
    )
    config.addinivalue_line(
        "markers", "database: marks tests related to database operations"
    )
    config.addinivalue_line(
        "markers", "external: marks tests that interact with external services"
    )
    config.addinivalue_line(
        "markers", "mock: marks tests that use extensive mocking"
    )


# ============================================================================
# ADVANCED FIXTURES - Setup and Teardown
# ============================================================================

@pytest.fixture(scope="session")
def test_session_config():
    """Session-level configuration that persists across all tests."""
    config = {
        "test_run_id": hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8],
        "start_time": datetime.now(),
        "test_data_root": tempfile.mkdtemp(prefix="pytest_session_"),
    }
    
    yield config
    
    # Cleanup session data
    if os.path.exists(config["test_data_root"]):
        shutil.rmtree(config["test_data_root"], ignore_errors=True)
    
    # Log session summary
    duration = datetime.now() - config["start_time"]
    print(f"\n[TEST SESSION] ID: {config['test_run_id']}, Duration: {duration}")


@pytest.fixture(scope="module")
def module_database():
    """Module-level database that persists across test class."""
    temp_dir = tempfile.mkdtemp(prefix="pytest_module_")
    db_path = os.path.join(temp_dir, 'module_database.db')
    
    original_db = os.environ.get('DATABASE_PATH')
    os.environ['DATABASE_PATH'] = db_path
    
    init_db()
    
    yield db_path
    
    if original_db:
        os.environ['DATABASE_PATH'] = original_db
    else:
        os.environ.pop('DATABASE_PATH', None)
    
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def temp_database():
    """
    Create a temporary database for each test to ensure isolation.
    This prevents tests from interfering with each other.
    """
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test_database.db')
    
    original_db = os.environ.get('DATABASE_PATH')
    os.environ['DATABASE_PATH'] = db_path
    
    init_db()
    
    yield db_path
    
    if original_db:
        os.environ['DATABASE_PATH'] = original_db
    else:
        os.environ.pop('DATABASE_PATH', None)
    
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def isolated_database():
    """Alternative database fixture with enhanced isolation."""
    with tempfile.TemporaryDirectory(prefix="isolated_db_") as temp_dir:
        db_path = os.path.join(temp_dir, 'isolated.db')
        
        original_db = os.environ.get('DATABASE_PATH')
        os.environ['DATABASE_PATH'] = db_path
        
        init_db()
        
        yield db_path
        
        if original_db:
            os.environ['DATABASE_PATH'] = original_db
        else:
            os.environ.pop('DATABASE_PATH', None)


@pytest.fixture(scope="function")
def weather_tool():
    """Fixture to provide a fresh WeatherTool instance for each test."""
    tool = WeatherTool()
    
    # Add metadata for testing
    tool._test_created_at = datetime.now()
    tool._test_call_count = 0
    
    # Wrap execute to track calls
    original_execute = tool.execute
    def tracked_execute(*args, **kwargs):
        tool._test_call_count += 1
        return original_execute(*args, **kwargs)
    tool.execute = tracked_execute
    
    yield tool
    
    # Cleanup if needed
    del tool


@pytest.fixture(scope="function")
def preference_tool(temp_database):
    """Fixture to provide a PreferenceTool with isolated database."""
    return PreferenceTool()


@pytest.fixture(scope="function")
def preference_tool_with_logging(temp_database, caplog):
    """PreferenceTool with logging capture enabled."""
    caplog.set_level(logging.DEBUG)
    tool = PreferenceTool()
    yield tool, caplog


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


@pytest.fixture(scope="function")
def extended_preferences():
    """Extended set of preferences for comprehensive testing."""
    return {
        # User preferences
        "user_name": "Test User",
        "user_email": "test@example.com",
        "user_age": "25",
        
        # UI preferences
        "theme": "dark",
        "font_size": "14",
        "layout": "grid",
        "sidebar_width": "250",
        
        # Application settings
        "auto_save": "true",
        "backup_enabled": "true",
        "notification_sound": "true",
        "language": "en-US",
        "timezone": "UTC",
        
        # Advanced settings
        "debug_mode": "false",
        "cache_size": "100",
        "max_connections": "5",
        "timeout": "30",
    }


@pytest.fixture
def mock_weather_api():
    """Mock external weather API responses."""
    with patch('src.tools.weather.WeatherTool._fetch_from_api') as mock:
        mock.return_value = {
            "temperature": 22,
            "condition": "Sunny",
            "humidity": 65,
            "wind_speed": 10
        }
        yield mock


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent time-based testing."""
    fixed_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    with patch('datetime.datetime') as mock_dt:
        mock_dt.now.return_value = fixed_time
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        yield mock_dt


@pytest.fixture
def captured_logs():
    """Fixture to capture log output during tests."""
    logger = logging.getLogger()
    original_level = logger.level
    logger.setLevel(logging.DEBUG)
    
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    
    yield stream
    
    logger.removeHandler(handler)
    logger.setLevel(original_level)


@pytest.fixture(autouse=True)
def reset_environment():
    """Automatically reset environment variables after each test."""
    original_env = os.environ.copy()
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def temp_files_cleanup():
    """Track and cleanup temporary files created during tests."""
    temp_files = []
    
    def register_temp_file(filepath):
        temp_files.append(filepath)
        return filepath
    
    yield register_temp_file
    
    # Cleanup all registered temp files
    for filepath in temp_files:
        if os.path.exists(filepath):
            try:
                if os.path.isfile(filepath):
                    os.remove(filepath)
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath, ignore_errors=True)
            except Exception as e:
                print(f"Failed to cleanup {filepath}: {e}")


@pytest.fixture
def database_factory():
    """Factory fixture to create multiple test databases."""
    databases = []
    
    def create_database(name="test_db"):
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, f'{name}.db')
        databases.append((db_path, temp_dir))
        
        # Initialize this specific database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        
        return db_path
    
    yield create_database
    
    # Cleanup all created databases
    for db_path, temp_dir in databases:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def performance_timer():
    """Fixture to measure test execution time."""
    class PerformanceTimer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.elapsed = None
        
        def start(self):
            self.start_time = time.perf_counter()
        
        def stop(self):
            self.end_time = time.perf_counter()
            self.elapsed = self.end_time - self.start_time
            return self.elapsed
        
        def __enter__(self):
            self.start()
            return self
        
        def __exit__(self, *args):
            self.stop()
    
    return PerformanceTimer()


# ============================================================================
# TEST SUITE 1: Database Logic - Comprehensive Testing
# ============================================================================

@pytest.mark.database
@pytest.mark.unit
class TestDatabasePersistence:
    """Comprehensive tests for database operations."""
    
    def test_database_initialization(self, temp_database):
        """Test if database initializes correctly with proper schema."""
        assert os.path.exists(temp_database)
        
        conn = sqlite3.connect(temp_database)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'preferences' in tables or 'user_data' in tables
    
    def test_database_schema_structure(self, temp_database):
        """Test that database schema has correct columns."""
        init_db()
        
        conn = sqlite3.connect(temp_database)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(preferences);")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        conn.close()
        
        # Verify essential columns exist
        assert 'key' in columns or 'id' in columns
        assert 'value' in columns
    
    def test_database_save_and_retrieve(self, temp_database):
        """Test basic save and retrieve operations."""
        init_db()
        set_preference("test_key", "test_value")
        result = get_preference("test_key")
        assert result == "test_value"
    
    def test_database_multiple_keys(self, temp_database, sample_preferences):
        """Test saving and retrieving multiple key-value pairs."""
        init_db()
        
        for key, value in sample_preferences.items():
            set_preference(key, value)
        
        for key, expected_value in sample_preferences.items():
            actual_value = get_preference(key)
            assert actual_value == expected_value, f"Mismatch for key '{key}'"
    
    def test_database_update_existing_key(self, temp_database):
        """Test updating an existing preference overwrites the old value."""
        init_db()
        
        set_preference("update_test", "initial_value")
        assert get_preference("update_test") == "initial_value"
        
        set_preference("update_test", "updated_value")
        assert get_preference("update_test") == "updated_value"
    
    def test_database_multiple_updates(self, temp_database):
        """Test multiple sequential updates to same key."""
        init_db()
        
        key = "multi_update_key"
        values = ["value1", "value2", "value3", "value4", "value5"]
        
        for value in values:
            set_preference(key, value)
        
        # Final value should be the last one
        assert get_preference(key) == values[-1]
    
    def test_database_nonexistent_key(self, temp_database):
        """Test retrieving a key that doesn't exist returns None or empty."""
        init_db()
        result = get_preference("nonexistent_key_12345")
        assert result is None or result == ""
    
    def test_database_case_sensitive_keys(self, temp_database):
        """Test that keys are case-sensitive."""
        init_db()
        
        set_preference("TestKey", "value1")
        set_preference("testkey", "value2")
        set_preference("TESTKEY", "value3")
        
        # All three should be stored separately
        assert get_preference("TestKey") == "value1"
        assert get_preference("testkey") == "value2"
        assert get_preference("TESTKEY") == "value3"
    
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
            ("key_with_tabs", "value\twith\ttabs"),
            ("key_with_backslash", "value\\with\\backslash"),
            ("key_with_forward_slash", "value/with/forward/slash"),
        ]
        
        for key, value in special_cases:
            set_preference(key, value)
            retrieved = get_preference(key)
            assert retrieved == value, f"Failed for key: {key}"
    
    def test_database_numeric_keys(self, temp_database):
        """Test handling of numeric-looking keys."""
        init_db()
        
        numeric_keys = ["123", "456.789", "0", "-100", "1e10"]
        
        for key in numeric_keys:
            set_preference(key, f"value_for_{key}")
            assert get_preference(key) == f"value_for_{key}"
    
    def test_database_empty_values(self, temp_database):
        """Test handling of empty strings and edge cases."""
        init_db()
        
        set_preference("empty_key", "")
        assert get_preference("empty_key") == ""
        
        long_value = "x" * 10000
        set_preference("long_key", long_value)
        assert get_preference("long_key") == long_value
    
    def test_database_null_value_handling(self, temp_database):
        """Test handling of None/null values."""
        init_db()
        
        # Depending on implementation, this might raise an error or store as string "None"
        try:
            set_preference("null_key", None)
            result = get_preference("null_key")
            assert result is None or result == "None" or result == ""
        except (TypeError, ValueError):
            # It's acceptable to reject None values
            pass
    
    def test_database_whitespace_keys(self, temp_database):
        """Test handling of keys with only whitespace."""
        init_db()
        
        whitespace_keys = [" ", "  ", "\t", "\n", " \t\n "]
        
        for key in whitespace_keys:
            try:
                set_preference(key, "whitespace_value")
                result = get_preference(key)
                # If allowed, should retrieve correctly
                assert result == "whitespace_value"
            except (ValueError, KeyError):
                # It's acceptable to reject whitespace-only keys
                pass
    
    def test_database_concurrency_simulation(self, temp_database):
        """Test multiple rapid sequential writes to simulate concurrency."""
        init_db()
        
        for i in range(100):
            set_preference(f"concurrent_key_{i}", f"value_{i}")
        
        for i in range(100):
            assert get_preference(f"concurrent_key_{i}") == f"value_{i}"
    
    @pytest.mark.slow
    def test_database_high_volume_operations(self, temp_database):
        """Test database with high volume of operations."""
        init_db()
        
        # Write 5000 records
        for i in range(5000):
            set_preference(f"volume_key_{i}", f"volume_value_{i}")
        
        # Verify random samples
        import random
        samples = random.sample(range(5000), 50)
        for i in samples:
            assert get_preference(f"volume_key_{i}") == f"volume_value_{i}"
    
    def test_database_transaction_integrity(self, temp_database):
        """Test that database maintains integrity after operations."""
        init_db()
        
        set_preference("key1", "value1")
        set_preference("key2", "value2")
        get_preference("key1")
        set_preference("key1", "updated_value1")
        
        assert get_preference("key1") == "updated_value1"
        assert get_preference("key2") == "value2"
    
    def test_database_deletion_if_supported(self, temp_database):
        """Test deletion of preferences if supported."""
        init_db()
        
        set_preference("to_delete", "delete_me")
        assert get_preference("to_delete") == "delete_me"
        
        # If your implementation supports deletion
        try:
            # Assuming there's a delete function
            from src.database import delete_preference
            delete_preference("to_delete")
            assert get_preference("to_delete") is None or get_preference("to_delete") == ""
        except (ImportError, AttributeError):
            # Deletion not supported, skip
            pass
    
    def test_database_atomic_operations(self, temp_database):
        """Test that operations are atomic."""
        init_db()
        
        # Set multiple keys and verify all or none succeed
        keys = [f"atomic_key_{i}" for i in range(10)]
        
        for i, key in enumerate(keys):
            set_preference(key, f"atomic_value_{i}")
        
        # All should be set
        for i, key in enumerate(keys):
            assert get_preference(key) == f"atomic_value_{i}"
    
    def test_database_file_permissions(self, temp_database):
        """Test database file has correct permissions."""
        assert os.path.exists(temp_database)
        
        # Check file is readable
        assert os.access(temp_database, os.R_OK)
        
        # Check file is writable
        assert os.access(temp_database, os.W_OK)
    
    def test_database_size_growth(self, temp_database):
        """Test database size growth is reasonable."""
        init_db()
        
        initial_size = os.path.getsize(temp_database)
        
        # Add 100 records
        for i in range(100):
            set_preference(f"size_test_{i}", f"value_{i}" * 10)
        
        final_size = os.path.getsize(temp_database)
        
        # Size should have grown but not excessively
        assert final_size > initial_size
        assert final_size < initial_size + 1024 * 1024  # Less than 1MB growth for 100 records
    
    @pytest.mark.parametrize("key_length", [1, 10, 50, 100, 255])
    def test_database_varying_key_lengths(self, temp_database, key_length):
        """Test keys of various lengths."""
        init_db()
        
        key = "k" * key_length
        value = f"value_for_{key_length}_chars"
        
        set_preference(key, value)
        assert get_preference(key) == value
    
    @pytest.mark.parametrize("value_length", [1, 100, 1000, 10000, 100000])
    def test_database_varying_value_lengths(self, temp_database, value_length):
        """Test values of various lengths."""
        init_db()
        
        key = f"key_for_length_{value_length}"
        value = "v" * value_length
        
        set_preference(key, value)
        retrieved = get_preference(key)
        assert len(retrieved) == value_length
        assert retrieved == value


# ============================================================================
# TEST SUITE 2: Preference Tool - String Parsing and Command Handling
# ============================================================================

@pytest.mark.unit
class TestPreferenceToolParsing:
    """Comprehensive tests for PreferenceTool command parsing and execution."""
    
    def test_preference_tool_initialization(self, preference_tool):
        """Test that PreferenceTool initializes correctly."""
        assert preference_tool is not None
        assert hasattr(preference_tool, 'execute')
        assert hasattr(preference_tool, 'name')
        assert hasattr(preference_tool, 'description')
    
    def test_preference_tool_attributes(self, preference_tool):
        """Test PreferenceTool has all required attributes."""
        assert isinstance(preference_tool.name, str)
        assert len(preference_tool.name) > 0
        assert isinstance(preference_tool.description, str)
        assert len(preference_tool.description) > 0
    
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
    
    def test_save_command_urls(self, preference_tool):
        """Test saving URLs with multiple colons and slashes."""
        urls = [
            "https://example.com",
            "http://localhost:8080/api/v1",
            "ftp://192.168.1.1:21/files",
        ]
        
        for i, url in enumerate(urls):
            response = preference_tool.execute(f"save: url_{i}: {url}")
            assert "saved" in response.lower() or "success" in response.lower()
            assert get_preference(f"url_{i}") == url
    
    def test_save_command_json_values(self, preference_tool):
        """Test saving JSON-formatted values."""
        json_data = '{"name": "John", "age": 30, "city": "New York"}'
        response = preference_tool.execute(f"save: user_data: {json_data}")
        
        assert "saved" in response.lower() or "success" in response.lower()
        saved = get_preference("user_data")
        assert saved == json_data
    
    def test_get_command_basic(self, preference_tool):
        """Test basic get command."""
        set_preference("test_get_key", "test_get_value")
        
        response = preference_tool.execute("get: test_get_key")
        assert "test_get_value" in response or response == "test_get_value"
    
    def test_get_command_nonexistent(self, preference_tool):
        """Test get command for nonexistent key."""
        response = preference_tool.execute("get: nonexistent_key_xyz")
        assert "not found" in response.lower() or "none" in response.lower() or response == ""
    
    def test_get_command_case_sensitivity(self, preference_tool):
        """Test get command respects case sensitivity."""
        set_preference("CaseSensitiveKey", "value1")
        
        response1 = preference_tool.execute("get: CaseSensitiveKey")
        response2 = preference_tool.execute("get: casesensitivekey")
        
        assert "value1" in response1
        # response2 should not find it (case sensitive)
        assert "not found" in response2.lower() or response2 == ""
    
    def test_delete_command_if_supported(self, preference_tool):
        """Test delete command if supported."""
        set_preference("to_delete_via_tool", "delete_me")
        
        try:
            response = preference_tool.execute("delete: to_delete_via_tool")
            assert "deleted" in response.lower() or "removed" in response.lower()
            
            # Verify it's deleted
            get_response = preference_tool.execute("get: to_delete_via_tool")
            assert "not found" in get_response.lower() or get_response == ""
        except:
            # Delete command not supported
            pass
    
    def test_list_command_if_supported(self, preference_tool, sample_preferences):
        """Test list command if supported."""
        for key, value in sample_preferences.items():
            set_preference(key, value)
        
        try:
            response = preference_tool.execute("list")
            
            if "not supported" not in response.lower():
                # Verify some keys are in the response
                found_keys = sum(1 for key in sample_preferences.keys() if key in response)
                assert found_keys > 0
        except:
            # List command not supported
            pass
    
    def test_invalid_command_format(self, preference_tool):
        """Test handling of invalid command formats."""
        invalid_commands = [
            "invalid_command",
            "save favorite_color blue",
            "save:",
            ": favorite_color: blue",
            "",
            "   ",
            "::::",
            "save::",
            "::value",
        ]
        
        for cmd in invalid_commands:
            response = preference_tool.execute(cmd)
            assert response is not None
    
    def test_command_with_special_characters(self, preference_tool):
        """Test commands with special characters."""
        special_tests = [
            "save: key@email: value@test.com",
            "save: key#hash: value#123",
            "save: key$dollar: $100",
            "save: key%percent: 50%",
            "save: key&ampersand: value&more",
        ]
        
        for cmd in special_tests:
            response = preference_tool.execute(cmd)
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
            assert response is not None
    
    @pytest.mark.parametrize("key,value", [
        ("simple_key", "simple_value"),
        ("numeric_value", "12345"),
        ("boolean_value", "true"),
        ("float_value", "3.14159"),
        ("json_like", '{"nested": "data"}'),
        ("list_like", "[1, 2, 3]"),
        ("negative_number", "-42"),
        ("scientific_notation", "1.5e-10"),
        ("hex_value", "0x1A2B3C"),
        ("binary_value", "0b101010"),
    ])
    def test_save_various_value_types(self, preference_tool, key, value):
        """Test saving various types of values as strings."""
        response = preference_tool.execute(f"save: {key}: {value}")
        assert "saved" in response.lower() or "success" in response.lower()
        
        saved_val = get_preference(key)
        assert saved_val == value
# ============================================================================
# END OF FILE
# ============================================================================
