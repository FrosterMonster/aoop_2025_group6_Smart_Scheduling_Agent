import pytz
from datetime import datetime, timedelta
import dateparser

# TIMEZONE used for parsing/normalization
DEFAULT_TZ = 'Asia/Taipei'

def parse_nl_time(nl_time_str: str, prefer_future: bool = True) -> datetime | None:
    """
    解析自然語言時間字串，返回一個 timezone-aware datetime（若無法解析回傳 None）。

    Examples:
      "明天下午 2 點" -> datetime(..., tzinfo=Asia/Taipei)
      "2025-11-03 20:00" -> datetime(..., tzinfo=Asia/Taipei)
    """
    if not nl_time_str or not isinstance(nl_time_str, str):
        return None

    # Quick heuristic for common Chinese relative expressions (e.g., "明天下午 2 點")
    try:
        s = nl_time_str.strip()
        now = datetime.now()
        tz = pytz.timezone(DEFAULT_TZ)
        base = None
        if '明天' in s or '明日' in s:
            base = now + timedelta(days=1)
        elif '今天' in s or '今日' in s:
            base = now
        elif '後天' in s:
            base = now + timedelta(days=2)

        if base is not None:
            # extract hour (Arabic numerals)
            import re
            m = re.search(r"(\d{1,2})", s)
            if m:
                hour = int(m.group(1))
                minute = 0
                # adjust for Chinese period words
                if '下午' in s or '晚上' in s:
                    if 1 <= hour <= 11:
                        hour = hour + 12
                if '上午' in s and hour == 12:
                    hour = 0
                dt = datetime(base.year, base.month, base.day, hour, minute)
                return tz.localize(dt)
    except Exception:
        pass

    settings = {
        'PREFER_DATES_FROM': 'future' if prefer_future else 'past',
        'RETURN_AS_TIMEZONE_AWARE': True,
        'TIMEZONE': DEFAULT_TZ,
    }

    # Try parsing with Chinese language hint first, then fallback to default
    try:
        dt = dateparser.parse(nl_time_str, settings=settings, languages=['zh'])
    except Exception:
        dt = None

    if dt is None:
        # fallback: try without explicit language and without timezone-aware setting
        dt = dateparser.parse(nl_time_str, settings={'PREFER_DATES_FROM': 'future' if prefer_future else 'past'})
    if dt is None:
        return None

    # Ensure tz-aware and normalized to DEFAULT_TZ
    try:
        tz = pytz.timezone(DEFAULT_TZ)
        if dt.tzinfo is None:
            dt = tz.localize(dt)
        else:
            dt = dt.astimezone(tz)
    except Exception:
        # If timezone normalization fails, still return dt
        pass

    return dt
