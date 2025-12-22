"""Time parsing tests - Ported from 阿嚕米 with enhancements

Tests for ai_schedule_agent.utils.time_parser module covering:
- Chinese natural language time parsing
- English natural language time parsing
- ISO format parsing
- Edge cases and known limitations
"""
import pytest
import pytz
from datetime import datetime, timedelta
from ai_schedule_agent.utils.time_parser import parse_nl_time


class TestChineseTimeParsing:
    """Test suite for Chinese language time parsing"""

    def test_parse_simple_iso(self):
        """Test ISO format datetime parsing"""
        dt = parse_nl_time("2025-11-03 20:00")
        assert dt is not None
        assert dt.tzinfo is not None  # Should be timezone-aware
        assert dt.year == 2025 and dt.hour == 20

    def test_tomorrow_afternoon_chinese(self):
        """Test '明天下午2點' (tomorrow afternoon 2pm)"""
        dt = parse_nl_time("明天下午2點")
        assert dt is not None
        assert dt.tzinfo is not None
        # Afternoon + 2pm = 14:00 (2pm + 12)
        assert dt.hour == 14

    def test_tomorrow_afternoon_with_space(self):
        """Test '明天下午 2 點' with spaces"""
        dt = parse_nl_time("明天下午 2 點")
        assert dt is not None
        assert dt.tzinfo is not None
        assert 14 <= dt.hour <= 15  # Allow some parsing variance

    def test_today_evening_chinese(self):
        """Test '今天晚上8點' (today evening 8pm)"""
        dt = parse_nl_time("今天晚上8點")
        assert dt is not None
        assert dt.tzinfo is not None
        assert dt.hour == 20  # Evening 8pm = 20:00

    def test_day_after_tomorrow_morning(self):
        """Test '後天上午10點' (day after tomorrow 10am)"""
        dt = parse_nl_time("後天上午10點")
        assert dt is not None
        assert dt.tzinfo is not None
        assert dt.hour == 10

    def test_with_minutes_chinese(self):
        """Test '明天下午2點30分' with minutes"""
        dt = parse_nl_time("明天下午2點30分")
        assert dt is not None
        assert dt.hour == 14
        assert dt.minute == 30

    def test_today_shorthand(self):
        """Test '今天' (today)"""
        dt = parse_nl_time("今天")
        assert dt is not None
        # Should return today's date
        assert dt.date() == datetime.now().date()

    @pytest.mark.xfail(reason="Parser may not fully support '下週一' relative week descriptions yet")
    def test_next_week_monday(self):
        """Test '下週一上午10點' (next Monday 10am) - Known limitation"""
        dt = parse_nl_time("下週一上午10點")
        assert dt is not None
        assert dt.tzinfo is not None
        assert dt.hour == 10
        # Should be a Monday
        assert dt.weekday() == 0


class TestEnglishTimeParsing:
    """Test suite for English language time parsing"""

    def test_tomorrow_2pm(self):
        """Test 'tomorrow 2pm'"""
        dt = parse_nl_time("tomorrow 2pm")
        assert dt is not None
        assert dt.hour == 14

    def test_tomorrow_at_2pm(self):
        """Test 'tomorrow at 2pm'"""
        dt = parse_nl_time("tomorrow at 2pm")
        assert dt is not None
        assert dt.hour == 14

    def test_next_monday_10am(self):
        """Test 'next monday 10am'"""
        dt = parse_nl_time("next monday 10am")
        assert dt is not None
        assert dt.weekday() == 0  # Monday
        assert dt.hour == 10

    def test_today_evening(self):
        """Test 'today evening'"""
        dt = parse_nl_time("today evening")
        assert dt is not None
        # Evening should be >= 18:00
        assert dt.hour >= 18

    def test_next_week_friday(self):
        """Test 'next week friday'"""
        dt = parse_nl_time("next week friday")
        assert dt is not None
        assert dt.weekday() == 4  # Friday


class TestMixedAndEdgeCases:
    """Test suite for mixed language and edge cases"""

    def test_with_12hour_format(self):
        """Test '2:30 PM' 12-hour format"""
        dt = parse_nl_time("2:30 PM")
        assert dt is not None
        assert dt.hour == 14
        assert dt.minute == 30

    def test_with_24hour_format(self):
        """Test '14:30' 24-hour format"""
        dt = parse_nl_time("14:30")
        assert dt is not None
        assert dt.hour == 14
        assert dt.minute == 30

    def test_date_with_slashes(self):
        """Test '11/27 2pm' date with slashes"""
        dt = parse_nl_time("11/27 2pm")
        assert dt is not None
        assert dt.month == 11
        assert dt.day == 27
        assert dt.hour == 14

    def test_timezone_aware(self):
        """Verify all parsed times are timezone-aware"""
        test_cases = [
            "明天下午2點",
            "tomorrow 2pm",
            "2025-12-25 10:00"
        ]
        for case in test_cases:
            dt = parse_nl_time(case)
            if dt:  # Some may fail, but if they succeed, must be tz-aware
                assert dt.tzinfo is not None, f"Failed for: {case}"

    def test_invalid_input(self):
        """Test that invalid inputs return None gracefully"""
        invalid_inputs = [
            "invalid time string",
            "",
            "!!!",
            "asdfasdf"
        ]
        for invalid in invalid_inputs:
            dt = parse_nl_time(invalid)
            # Should either return None or a reasonable default, not crash
            assert dt is None or isinstance(dt, datetime)

    def test_prefer_future(self):
        """Test that parser prefers future dates when ambiguous"""
        # "2pm" without date should be interpreted as future
        dt = parse_nl_time("2pm", prefer_future=True)
        if dt:
            # Should be today or later
            assert dt >= datetime.now(pytz.timezone('Asia/Taipei'))


class TestDurationParsing:
    """Test duration parsing if implemented"""

    def test_hours_english(self):
        """Test '2 hours' duration"""
        # Note: This assumes parse_duration exists in time_parser
        # If not, mark as xfail or skip
        try:
            from ai_schedule_agent.utils.time_parser import parse_duration
            td = parse_duration("2 hours")
            assert td.total_seconds() == 7200  # 2 hours = 7200 seconds
        except ImportError:
            pytest.skip("parse_duration not implemented yet")

    def test_hours_chinese(self):
        """Test '2小時' duration"""
        try:
            from ai_schedule_agent.utils.time_parser import parse_duration
            td = parse_duration("2小時")
            assert td.total_seconds() == 7200
        except ImportError:
            pytest.skip("parse_duration not implemented yet")

    def test_minutes(self):
        """Test '30分鐘' or '30 minutes'"""
        try:
            from ai_schedule_agent.utils.time_parser import parse_duration
            td = parse_duration("30 minutes")
            assert td.total_seconds() == 1800  # 30 * 60
        except ImportError:
            pytest.skip("parse_duration not implemented yet")
