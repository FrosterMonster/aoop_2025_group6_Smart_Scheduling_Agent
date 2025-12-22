"""NLP Processor tests - Chinese pattern extraction

Tests for the Chinese regex fallback patterns ported from 阿嚕米
"""
import pytest
from datetime import datetime
import pytz
from ai_schedule_agent.core.nlp_processor import NLPProcessor


class TestChinesePatterns:
    """Test Chinese pattern extraction from NLPProcessor"""

    def setup_method(self):
        """Set up test fixture with LLM disabled"""
        self.nlp = NLPProcessor(use_llm=False)  # Force rule-based mode

    def test_chinese_brackets_single_quote(self):
        """Test extraction from Chinese single quotes 「」"""
        result = self.nlp.parse_scheduling_request("請安排「與教授會面」")
        assert result['title'] == "與教授會面"
        assert result['action'] == 'create'

    def test_chinese_brackets_double_quote(self):
        """Test extraction from Chinese double quotes 『』"""
        result = self.nlp.parse_scheduling_request("請安排『團隊討論』")
        assert result['title'] == "團隊討論"

    def test_english_quotes(self):
        """Test extraction from English quotes"""
        result = self.nlp.parse_scheduling_request('Schedule "Project Review"')
        assert result['title'] == "Project Review"

    def test_arrange_pattern_with_brackets(self):
        """Test '安排「...」' pattern"""
        result = self.nlp.parse_scheduling_request("安排「專案討論」，明天下午2點")
        assert result['title'] == "專案討論"
        # Should also extract time
        assert result['datetime'] is not None
        assert result['datetime'].hour == 14

    def test_arrange_pattern_without_brackets(self):
        """Test '安排...' pattern without brackets"""
        result = self.nlp.parse_scheduling_request("安排專案討論，明天下午2點")
        assert result['title'] is not None
        # May extract "專案討論" or partial

    def test_time_range_with_dao(self):
        """Test time range with '到' (to) pattern"""
        result = self.nlp.parse_scheduling_request("時間是今天晚上8點到9點")
        assert result['datetime'] is not None
        assert result['datetime'].hour == 20  # 8pm
        assert result['end_datetime'] is not None
        assert result['end_datetime'].hour == 21  # 9pm
        # Duration should be calculated
        assert result['duration'] == 60  # 1 hour

    def test_full_chinese_request(self):
        """Test full Chinese scheduling request"""
        text = "請安排「與教授會面」，時間是明天晚上8點到9點"
        result = self.nlp.parse_scheduling_request(text)

        assert result['title'] == "與教授會面"
        assert result['datetime'] is not None
        assert result['datetime'].hour == 20
        assert result['end_datetime'] is not None
        assert result['end_datetime'].hour == 21
        assert result['duration'] == 60

    def test_relative_date_today(self):
        """Test '今天' (today) extraction"""
        result = self.nlp.parse_scheduling_request("今天下午3點開會")
        assert result['datetime'] is not None
        assert result['datetime'].hour == 15  # 3pm
        # Verify it's today
        today = datetime.now(pytz.timezone('Asia/Taipei')).date()
        assert result['datetime'].date() == today

    def test_relative_date_tomorrow(self):
        """Test '明天' (tomorrow) extraction"""
        result = self.nlp.parse_scheduling_request("明天上午10點")
        assert result['datetime'] is not None
        assert result['datetime'].hour == 10

    def test_relative_date_day_after_tomorrow(self):
        """Test '後天' (day after tomorrow) extraction"""
        result = self.nlp.parse_scheduling_request("後天下午2點")
        assert result['datetime'] is not None
        assert result['datetime'].hour == 14

    def test_dao_pattern_with_punctuation(self):
        """Test '到' pattern with various punctuation"""
        test_cases = [
            "8點到9點。",  # Period
            "8點到9點，",  # Comma
            "8點到9點",     # No punctuation
        ]
        for text in test_cases:
            result = self.nlp.parse_scheduling_request(text)
            assert result['datetime'] is not None
            assert result['end_datetime'] is not None

    def test_mixed_chinese_english(self):
        """Test mixed Chinese and English input"""
        result = self.nlp.parse_scheduling_request("安排「Team Meeting」明天下午2點")
        assert result['title'] == "Team Meeting"
        assert result['datetime'] is not None
        assert result['datetime'].hour == 14


class TestEnglishPatterns:
    """Test that English patterns still work after Chinese integration"""

    def setup_method(self):
        """Set up test fixture"""
        self.nlp = NLPProcessor(use_llm=False)

    def test_english_schedule_request(self):
        """Test basic English scheduling request"""
        result = self.nlp.parse_scheduling_request("Schedule meeting tomorrow 2pm")
        assert result['datetime'] is not None
        assert result['datetime'].hour == 14
        assert result['title'] is not None

    def test_english_with_participants(self):
        """Test English with participant extraction"""
        result = self.nlp.parse_scheduling_request("Schedule meeting with John tomorrow 2pm")
        assert result['datetime'] is not None
        assert 'John' in result['participants'] or 'John' in result.get('title', '')

    def test_english_with_duration(self):
        """Test English with duration"""
        result = self.nlp.parse_scheduling_request("Schedule meeting for 2 hours tomorrow")
        assert result['duration'] == 120  # 2 hours = 120 minutes

    def test_english_with_location(self):
        """Test English with location"""
        result = self.nlp.parse_scheduling_request("Schedule meeting at Conference Room tomorrow 2pm")
        assert result['location'] is not None
        assert 'conference' in result['location'].lower() or 'Conference Room' in result.get('title', '')


class TestFallbackBehavior:
    """Test fallback behavior when Chinese patterns don't match"""

    def setup_method(self):
        """Set up test fixture"""
        self.nlp = NLPProcessor(use_llm=False)

    def test_fallback_to_dateparser(self):
        """Test that dateparser fallback works when Chinese patterns fail"""
        result = self.nlp.parse_scheduling_request("Schedule something for next Monday")
        assert result['datetime'] is not None
        assert result['datetime'].weekday() == 0  # Monday

    def test_fallback_title_extraction(self):
        """Test fallback title extraction"""
        result = self.nlp.parse_scheduling_request("Let's have a team sync tomorrow at 3pm")
        assert result['title'] is not None
        assert result['datetime'] is not None

    def test_no_time_provided(self):
        """Test when no time is provided"""
        result = self.nlp.parse_scheduling_request("安排會議")
        assert result['title'] is not None
        # datetime may be None or parsed from context


class TestEdgeCases:
    """Test edge cases and error handling"""

    def setup_method(self):
        """Set up test fixture"""
        self.nlp = NLPProcessor(use_llm=False)

    def test_empty_brackets(self):
        """Test empty Chinese brackets"""
        result = self.nlp.parse_scheduling_request("安排「」明天")
        # Should not crash
        assert isinstance(result, dict)

    def test_only_dao_no_times(self):
        """Test '到' without actual times"""
        result = self.nlp.parse_scheduling_request("從這裡到那裡")
        # Should not crash, may not extract times
        assert isinstance(result, dict)

    def test_multiple_brackets(self):
        """Test multiple bracket pairs"""
        result = self.nlp.parse_scheduling_request("安排「會議A」和「會議B」")
        # Should extract at least one title
        assert result['title'] is not None

    def test_very_long_input(self):
        """Test very long input string"""
        long_text = "請" + "安排會議" * 100 + "明天下午2點"
        result = self.nlp.parse_scheduling_request(long_text)
        # Should not crash
        assert isinstance(result, dict)

    def test_special_characters(self):
        """Test special characters in title"""
        result = self.nlp.parse_scheduling_request("安排「CS@NYCU會議」明天")
        assert result['title'] is not None
        assert '@' in result['title'] or 'CS' in result['title']
