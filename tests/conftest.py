"""Pytest configuration and fixtures"""
import pytest
import os
from ai_schedule_agent.config.manager import ConfigManager


@pytest.fixture(scope="session")
def config():
    """Test configuration with DRY_RUN enabled"""
    os.environ['DRY_RUN'] = '1'
    os.environ['DEFAULT_TIMEZONE'] = 'Asia/Taipei'
    return ConfigManager()


@pytest.fixture
def sample_chinese_text():
    """Sample Chinese scheduling requests for testing"""
    return [
        "請安排「與教授會面」，時間是今天晚上8點到9點",
        "明天下午2點開會",
        "後天上午10點30分討論專案",
    ]


@pytest.fixture
def sample_english_text():
    """Sample English scheduling requests for testing"""
    return [
        "Schedule meeting tomorrow 2pm",
        "Book a room for next Monday at 10am",
        "Add focus time for 2 hours today",
    ]
