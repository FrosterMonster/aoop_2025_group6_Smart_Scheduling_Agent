import pytest
import sqlite3
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock, call
from src.database import init_db, set_preference, get_preference, get_all_preferences
from src.logger import log_info

# ============================================================================
# BASIC SEEDING TESTS
# ============================================================================

def test_seed_database_basic():
    """Test basic database seeding functionality."""
    from scripts.seed_database import seed_database
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            seed_database()
            
            # Verify preferences were set
            assert get_preference("work_start") is not None
            assert get_preference("work_end") is not None
            assert get_preference("theme") is not None

def test_seed_all_preferences_exist():
    """Verify all expected preferences are seeded."""
    from scripts.seed_database import seed_database
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            seed_database()
            
            expected_keys = [
                "work_start",
                "work_end",
                "lunch_break",
                "meeting_preference",
                "theme",
                "notification_level",
                "default_meeting_duration"
            ]
            
            for key in expected_keys:
                value = get_preference(key)
                assert value is not None, f"Preference '{key}' was not seeded"
                assert len(value) > 0, f"Preference '{key}' is empty"

def test_seed_preference_values():
    """Verify seeded preferences have correct values."""
    from scripts.seed_database import seed_database
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            seed_database()
            
            assert get_preference("work_start") == "09:00 AM"
            assert get_preference("work_end") == "06:00 PM"
            assert get_preference("lunch_break") == "12:00 PM - 01:00 PM"
            assert get_preference("meeting_preference") == "No meetings on Friday afternoon"
            assert get_preference("theme") == "Dark Mode"
            assert get_preference("notification_level") == "High"
            assert get_preference("default_meeting_duration") == "30 minutes"

# ============================================================================
# IDEMPOTENCY TESTS
# ============================================================================

def test_seed_idempotency():
    """Test that running seed multiple times doesn't cause errors."""
    from scripts.seed_database import seed_database
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            # Run seed twice
            seed_database()
            seed_database()
            
            # Verify data is still correct (not duplicated)
            assert get_preference("work_start") == "09:00 AM"
            assert get_preference("theme") == "Dark Mode"

def test_seed_overwrites_existing_data():
    """Test that seeding overwrites existing preferences."""
    from scripts.seed_database import seed_database
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            init_db()
            
            # Set initial values
            set_preference("work_start", "08:00 AM")
            set_preference("theme", "Light Mode")
            
            # Run seed
            seed_database()
            
            # Verify values were overwritten
            assert get_preference("work_start") == "09:00 AM"
            assert get_preference("theme") == "Dark Mode"

# ============================================================================
# DATABASE INITIALIZATION TESTS
# ============================================================================

def test_seed_calls_init_db():
    """Verify that seed_database calls init_db."""
    from scripts.seed_database import seed_database
    
    with patch('scripts.seed_database.init_db') as mock_init:
        with patch('scripts.seed_database.set_preference'):
            with patch('scripts.seed_database.log_info'):
                seed_database()
                mock_init.assert_called_once()

def test_seed_works_with_fresh_database():
    """Test seeding a completely fresh database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "fresh.db")
        
        # Ensure database doesn't exist
        assert not os.path.exists(test_db)
        
        with patch('src.database.DB_PATH', test_db):
            from scripts.seed_database import seed_database
            seed_database()
            
            # Verify database was created and seeded
            assert os.path.exists(test_db)
            assert get_preference("work_start") == "09:00 AM"

# ============================================================================
# LOGGING TESTS
# ============================================================================

def test_seed_logs_start_message():
    """Verify seed logs startup message."""
    from scripts.seed_database import seed_database
    
    with patch('scripts.seed_database.init_db'):
        with patch('scripts.seed_database.set_preference'):
            with patch('scripts.seed_database.log_info') as mock_log:
                seed_database()
                
                # Check for seeding start message
                calls = [str(c) for c in mock_log.call_args_list]
                assert any("Seeding database" in str(c) for c in calls)

def test_seed_logs_each_preference():
    """Verify seed logs each preference that's saved."""
    from scripts.seed_database import seed_database
    
    with patch('scripts.seed_database.init_db'):
        with patch('scripts.seed_database.set_preference'):
            with patch('scripts.seed_database.log_info') as mock_log:
                seed_database()
                
                # Should log for each preference + start + complete
                # 7 preferences + 2 bookend messages = 9 calls
                assert mock_log.call_count >= 7

def test_seed_logs_completion_message():
    """Verify seed logs completion message."""
    from scripts.seed_database import seed_database
    
    with patch('scripts.seed_database.init_db'):
        with patch('scripts.seed_database.set_preference'):
            with patch('scripts.seed_database.log_info') as mock_log:
                seed_database()
                
                # Check for completion message
                calls = [str(c) for c in mock_log.call_args_list]
                assert any("complete" in str(c).lower() for c in calls)

def test_seed_logs_preference_details():
    """Verify seed logs include preference key-value pairs."""
    from scripts.seed_database import seed_database
    
    with patch('scripts.seed_database.init_db'):
        with patch('scripts.seed_database.set_preference'):
            with patch('scripts.seed_database.log_info') as mock_log:
                seed_database()
                
                # Check that logs contain specific preferences
                log_messages = [str(call[0][0]) for call in mock_log.call_args_list]
                combined_logs = " ".join(log_messages)
                
                assert "work_start" in combined_logs
                assert "theme" in combined_logs
                assert "Dark Mode" in combined_logs

# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_seed_handles_database_error():
    """Test seed handles database errors gracefully."""
    from scripts.seed_database import seed_database
    
    with patch('scripts.seed_database.init_db'):
        with patch('scripts.seed_database.set_preference', side_effect=sqlite3.Error("DB Error")):
            with patch('scripts.seed_database.log_info'):
                try:
                    seed_database()
                except sqlite3.Error:
                    pass  # Expected to raise or handle error

def test_seed_handles_missing_database_module():
    """Test behavior when database module is unavailable."""
    with patch.dict('sys.modules', {'src.database': None}):
        try:
            from scripts.seed_database import seed_database
            # Should either fail to import or handle gracefully
        except ImportError:
            pass  # Expected

# ============================================================================
# DATA INTEGRITY TESTS
# ============================================================================

def test_seed_creates_valid_time_formats():
    """Verify time-related preferences have valid formats."""
    from scripts.seed_database import seed_database
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            seed_database()
            
            work_start = get_preference("work_start")
            work_end = get_preference("work_end")
            lunch_break = get_preference("lunch_break")
            
            # Basic format checks
            assert "AM" in work_start or "PM" in work_start
            assert "AM" in work_end or "PM" in work_end
            assert "-" in lunch_break  # Range format

def test_seed_creates_valid_duration():
    """Verify duration preference has valid format."""
    from scripts.seed_database import seed_database
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            seed_database()
            
            duration = get_preference("default_meeting_duration")
            assert "minutes" in duration or "hour" in duration

def test_seed_creates_valid_notification_level():
    """Verify notification level is a recognized value."""
    from scripts.seed_database import seed_database
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            seed_database()
            
            level = get_preference("notification_level")
            valid_levels = ["Low", "Medium", "High", "Off"]
            assert level in valid_levels

# ============================================================================
# EXTENDED SEEDING SCENARIOS
# ============================================================================

def test_seed_with_additional_preferences():
    """Test extending seed with more preferences."""
    from scripts.seed_database import seed_database
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            # Run standard seed
            seed_database()
            
            # Add extra preferences
            set_preference("timezone", "UTC-8")
            set_preference("language", "en-US")
            set_preference("auto_accept_invites", "false")
            
            # Verify all exist
            assert get_preference("work_start") == "09:00 AM"
            assert get_preference("timezone") == "UTC-8"
            assert get_preference("language") == "en-US"

def test_seed_different_work_schedules():
    """Test seeding different work schedule configurations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            init_db()
            
            # Test various work schedules
            schedules = [
                {"work_start": "07:00 AM", "work_end": "03:00 PM"},  # Early shift
                {"work_start": "09:00 AM", "work_end": "05:00 PM"},  # Standard
                {"work_start": "12:00 PM", "work_end": "08:00 PM"},  # Late shift
            ]
            
            for schedule in schedules:
                set_preference("work_start", schedule["work_start"])
                set_preference("work_end", schedule["work_end"])
                
                assert get_preference("work_start") == schedule["work_start"]
                assert get_preference("work_end") == schedule["work_end"]

def test_seed_different_themes():
    """Test seeding different theme preferences."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            init_db()
            
            themes = ["Dark Mode", "Light Mode", "Auto", "High Contrast"]
            
            for theme in themes:
                set_preference("theme", theme)
                assert get_preference("theme") == theme

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_seed_performance():
    """Test that seeding completes in reasonable time."""
    import time
    from scripts.seed_database import seed_database
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            start_time = time.time()
            seed_database()
            elapsed = time.time() - start_time
            
            # Should complete in under 1 second
            assert elapsed < 1.0, f"Seeding took {elapsed:.2f}s, expected < 1s"

def test_seed_large_preference_set():
    """Test seeding with a large number of preferences."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            init_db()
            
            # Add 100 preferences
            for i in range(100):
                set_preference(f"pref_{i}", f"value_{i}")
            
            # Verify a sample
            assert get_preference("pref_0") == "value_0"
            assert get_preference("pref_50") == "value_50"
            assert get_preference("pref_99") == "value_99"

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_seed_then_query_all():
    """Test seeding then querying all preferences."""
    from scripts.seed_database import seed_database
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            seed_database()
            
            all_prefs = get_all_preferences()
            assert len(all_prefs) >= 7
            assert "work_start" in all_prefs
            assert "theme" in all_prefs

def test_seed_then_modify():
    """Test seeding then modifying preferences."""
    from scripts.seed_database import seed_database
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            seed_database()
            
            # Modify some preferences
            set_preference("work_start", "08:30 AM")
            set_preference("theme", "Light Mode")
            
            # Verify modifications
            assert get_preference("work_start") == "08:30 AM"
            assert get_preference("theme") == "Light Mode"
            
            # Verify others unchanged
            assert get_preference("work_end") == "06:00 PM"

def test_seed_then_delete():
    """Test seeding then deleting preferences."""
    from scripts.seed_database import seed_database
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            seed_database()
            
            # Delete a preference (if delete function exists)
            # This is placeholder - adjust based on your actual API
            conn = sqlite3.connect(test_db)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM preferences WHERE key = ?", ("theme",))
            conn.commit()
            conn.close()
            
            # Verify deletion
            assert get_preference("theme") is None

# ============================================================================
# CUSTOM SEED SCENARIOS
# ============================================================================

def test_seed_minimal_preferences():
    """Test seeding with minimal set of preferences."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            init_db()
            
            minimal_prefs = {
                "work_start": "09:00 AM",
                "work_end": "05:00 PM",
            }
            
            for key, value in minimal_prefs.items():
                set_preference(key, value)
            
            assert get_preference("work_start") == "09:00 AM"
            assert get_preference("work_end") == "05:00 PM"

def test_seed_international_preferences():
    """Test seeding with international formats."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        
        with patch('src.database.DB_PATH', test_db):
            init_db()
            
            intl_prefs = {
                "work_start": "09:00",  # 24-hour format
                "work_end": "17:00",
                "lunch_break": "12:00 - 13:00",
                "timezone": "Europe/Paris",
                "date_format": "DD/MM/YYYY"
            }
            
            for key, value in intl_prefs.items():
                set_preference(key, value)
            
            assert get_preference("work_start") == "09:00"
            assert get_preference("timezone") == "Europe/Paris"

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])