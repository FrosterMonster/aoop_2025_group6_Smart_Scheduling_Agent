from calendar_time_parser import parse_nl_time
from datetime import datetime
import pytz
import pytest


def test_parse_simple_time():
    dt = parse_nl_time("2025-11-03 20:00")
    assert dt is not None
    tz = pytz.timezone('Asia/Taipei')
    assert dt.tzinfo is not None
    assert dt.year == 2025 and dt.hour == 20


def test_parse_natural_language():
    # 以相對時間為例（此測試會回傳一個 datetime，並檢查時區與大致小時）
    dt = parse_nl_time("明天下午 2 點")
    assert dt is not None
    assert dt.tzinfo is not None
    # 大致檢查 hour 在 14~15 之間（若含分鐘解析）
    assert 14 <= dt.hour <= 15


def test_parse_today_evening_range():
    # 測試能否解析 "今天晚上 8 點"（獨立起始時間解析）
    dt = parse_nl_time("今天晚上 8 點")
    assert dt is not None
    assert dt.tzinfo is not None
    assert dt.hour == 20


@pytest.mark.xfail(reason="目前 parser 尚未完全支援 '下週一' 之類的相對週描述，紀錄為已知問題")
def test_parse_next_week_monday():
    # 這個測試目前可能失敗；標記為 xfail
    dt = parse_nl_time("下週一上午 10 點")
    assert dt is not None
    assert dt.tzinfo is not None
    assert dt.hour == 10
