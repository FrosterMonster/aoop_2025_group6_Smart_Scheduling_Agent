"""Enhanced time parser with Chinese language support"""

import re
import logging
from datetime import datetime, timedelta
from typing import Optional
import pytz
import dateparser

from ai_schedule_agent.config.manager import ConfigManager

logger = logging.getLogger(__name__)


def parse_nl_time(nl_time_str: str, prefer_future: bool = True, timezone: Optional[str] = None) -> Optional[datetime]:
    """Parse natural language time expression to timezone-aware datetime

    Supports both English and Chinese (繁體中文) time expressions:
    - English: "tomorrow 2pm", "next Monday at 10am", "today at 8pm"
    - Chinese: "明天下午2點", "今天晚上8點", "後天上午10點"

    Args:
        nl_time_str: Natural language time string
        prefer_future: If True, prefer future dates for ambiguous times (default: True)
        timezone: Timezone string (e.g., 'Asia/Taipei'). If None, uses config default.

    Returns:
        Timezone-aware datetime object, or None if parsing fails

    Examples:
        >>> parse_nl_time("明天下午2點")
        datetime(2025, 11, 5, 14, 0, 0, tzinfo=<DstTzInfo 'Asia/Taipei' ...>)

        >>> parse_nl_time("today at 8pm")
        datetime(2025, 11, 4, 20, 0, 0, tzinfo=<DstTzInfo 'Asia/Taipei' ...>)
    """
    if not nl_time_str or not isinstance(nl_time_str, str):
        logger.warning(f"Invalid time string: {nl_time_str}")
        return None

    # Get timezone
    if timezone is None:
        config = ConfigManager()
        timezone = config.get_timezone()

    try:
        tz = pytz.timezone(timezone)
    except Exception as e:
        logger.error(f"Invalid timezone '{timezone}': {e}")
        tz = pytz.timezone('Asia/Taipei')  # Fallback

    now = datetime.now(tz)
    s = nl_time_str.strip()

    logger.debug(f"Parsing time string: '{s}' (timezone: {timezone})")

    # ----- Quick heuristic for Chinese patterns -----
    base = None
    hour = None
    minute = 0

    # Relative date detection (Chinese and English)
    if '明天' in s or '明日' in s or 'tomorrow' in s.lower():
        base = now + timedelta(days=1)
        logger.debug("Detected: 明天/tomorrow")
    elif '今天' in s or '今日' in s or 'today' in s.lower():
        base = now
        logger.debug("Detected: 今天/today")
    elif '後天' in s or 'day after tomorrow' in s.lower():
        base = now + timedelta(days=2)
        logger.debug("Detected: 後天/day after tomorrow")
    elif '昨天' in s or '昨日' in s or 'yesterday' in s.lower():
        base = now - timedelta(days=1)
        logger.debug("Detected: 昨天/yesterday")
    elif '這周' in s or '這週' in s or '本周' in s or '本週' in s or 'this week' in s.lower():
        # For "this week", use today as base (schedule optimization will find best time)
        base = now
        logger.debug("Detected: 這周/this week")
    elif '下周' in s or '下週' in s or 'next week' in s.lower():
        # For "next week", use next Monday as base
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7  # If today is Monday, go to next Monday
        base = now + timedelta(days=days_until_monday)
        logger.debug(f"Detected: 下周/next week -> +{days_until_monday} days")

    # Handle "next [day]" patterns (e.g., "next monday", "next friday")
    next_day_match = re.search(r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)', s.lower())
    if next_day_match and 'week' not in s.lower():  # Don't match if "week" is present (handled below)
        day_name = next_day_match.group(1)
        day_map = {
            'monday': 0, 'mon': 0,
            'tuesday': 1, 'tue': 1,
            'wednesday': 2, 'wed': 2,
            'thursday': 3, 'thu': 3,
            'friday': 4, 'fri': 4,
            'saturday': 5, 'sat': 5,
            'sunday': 6, 'sun': 6
        }
        target_weekday = day_map.get(day_name)
        if target_weekday is not None:
            # Calculate days until next occurrence of target day
            days_ahead = target_weekday - now.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7  # Move to next week
            base = now + timedelta(days=days_ahead)
            logger.debug(f"Detected: next {day_name} -> +{days_ahead} days")

    # Handle "next week [day]" patterns (e.g., "next week monday", "next week 星期一")
    next_week_match = re.search(r'next\s+week\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)', s.lower())
    if next_week_match:
        day_name = next_week_match.group(1)
        day_map = {
            'monday': 0, 'mon': 0,
            'tuesday': 1, 'tue': 1,
            'wednesday': 2, 'wed': 2,
            'thursday': 3, 'thu': 3,
            'friday': 4, 'fri': 4,
            'saturday': 5, 'sat': 5,
            'sunday': 6, 'sun': 6
        }
        target_weekday = day_map.get(day_name)
        if target_weekday is not None:
            # Calculate days until next week's target day
            days_ahead = target_weekday - now.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7  # Move to next week
            days_ahead += 7  # Add another week for "next week"
            base = now + timedelta(days=days_ahead)
            logger.debug(f"Detected: next week {day_name} -> +{days_ahead} days")

    # Handle "下週[day]" or "下周[day]" patterns (Chinese)
    next_week_cn_match = re.search(r'下[週周]\s*([星期礼拜禮拜]?[一二三四五六日天])', s)
    if next_week_cn_match:
        day_char = next_week_cn_match.group(1)
        day_char = day_char.replace('星期', '').replace('礼拜', '').replace('禮拜', '')
        day_map_cn = {'一': 0, '二': 1, '三': 2, '四': 3, '五': 4, '六': 5, '日': 6, '天': 6}
        target_weekday = day_map_cn.get(day_char)
        if target_weekday is not None:
            days_ahead = target_weekday - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            days_ahead += 7  # Add another week for "next week"
            base = now + timedelta(days=days_ahead)
            logger.debug(f"Detected: 下週{day_char} -> +{days_ahead} days")

    # If we found a relative date, try to extract time
    if base is not None:
        # Extract hour from patterns like "下午2點", "晚上8點", "上午10點", "2pm", etc.
        m = re.search(r'(\d{1,2})\s*[點点时時]', s)
        if m:
            hour = int(m.group(1))
            logger.debug(f"Extracted hour: {hour}")

            # Extract minutes if present (e.g., "2點30分")
            m_min = re.search(r'[點点时時]\s*(\d{1,2})\s*[分]', s)
            if m_min:
                minute = int(m_min.group(1))
                logger.debug(f"Extracted minute: {minute}")

            # Time period adjustment (Chinese)
            if '下午' in s or '晚上' in s:
                # 下午 (afternoon) or 晚上 (evening/night)
                if 1 <= hour <= 11:
                    hour = hour + 12
                    logger.debug(f"Adjusted hour for 下午/晚上: {hour}")
            elif '上午' in s or '早上' in s:
                # 上午 (morning) or 早上 (early morning)
                if hour == 12:
                    hour = 0
                    logger.debug("Adjusted hour for 上午: 0 (midnight)")
        else:
            # Try English time patterns
            m_eng = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', s.lower())
            if m_eng:
                hour = int(m_eng.group(1))
                minute = int(m_eng.group(2)) if m_eng.group(2) else 0
                am_pm = m_eng.group(3)

                if am_pm == 'pm' and hour < 12:
                    hour += 12
                elif am_pm == 'am' and hour == 12:
                    hour = 0

                logger.debug(f"Extracted English time: {hour}:{minute:02d}")

        # If we extracted time, construct the datetime
        if hour is not None:
            # Construct datetime
            result = base.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # If prefer_future and result is in the past, add a day
            if prefer_future and result < now:
                result = result + timedelta(days=1)
                logger.debug("Adjusted to future date (prefer_future=True)")

            logger.info(f"Successfully parsed '{nl_time_str}' to {result}")
            return result
        else:
            # No time specified, use default time (9 AM for future dates)
            result = base.replace(hour=9, minute=0, second=0, microsecond=0)
            logger.info(f"Successfully parsed '{nl_time_str}' to {result} (default 9 AM)")
            return result

    # ----- Try standard datetime format (ISO 8601 or similar) -----
    # Patterns like "2025-11-05 14:00:00" or "2025-11-05 14:00"
    iso_pattern = r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?'
    m = re.match(iso_pattern, s)
    if m:
        year, month, day, hour, minute = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))
        second = int(m.group(6)) if m.group(6) else 0
        try:
            result = tz.localize(datetime(year, month, day, hour, minute, second))
            logger.info(f"Parsed ISO format '{nl_time_str}' to {result}")
            return result
        except Exception as e:
            logger.warning(f"Failed to create datetime from ISO format: {e}")

    # ----- Try MM/DD date format (e.g., "11/21", "11/21 2pm") -----
    # Match patterns like "11/21" or "11/21 下午2點" or "11/21 2pm"
    date_only_pattern = r'(\d{1,2})/(\d{1,2})(?:\s+(.+))?$'
    m = re.match(date_only_pattern, s)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        time_part = m.group(3) if m.group(3) else None

        # Determine the year (assume current year, or next year if date has passed)
        year = now.year
        try:
            # Try to create the date
            candidate_date = tz.localize(datetime(year, month, day, 0, 0, 0))

            # If the date is in the past, try next year
            if prefer_future and candidate_date.date() < now.date():
                year += 1
                candidate_date = tz.localize(datetime(year, month, day, 0, 0, 0))

            # If there's a time part, try to extract the hour and minute
            if time_part:
                logger.debug(f"Date parsed: {candidate_date.date()}, now parsing time: {time_part}")

                # Try Chinese time patterns first
                hour_extracted = None
                minute_extracted = 0

                # Extract hour from patterns like "下午2點", "晚上8點", "上午10點", "2pm", "3:30pm"
                m_hour = re.search(r'(\d{1,2})\s*[點点时時]', time_part)
                if m_hour:
                    hour_extracted = int(m_hour.group(1))
                    # Extract minutes if present
                    m_min = re.search(r'[點点时時]\s*(\d{1,2})\s*[分]', time_part)
                    if m_min:
                        minute_extracted = int(m_min.group(1))

                    # Time period adjustment (Chinese)
                    if '下午' in time_part or '晚上' in time_part:
                        if 1 <= hour_extracted <= 11:
                            hour_extracted += 12
                    elif '上午' in time_part or '早上' in time_part:
                        if hour_extracted == 12:
                            hour_extracted = 0
                else:
                    # Try English time patterns like "2pm", "3:30pm", "14:00"
                    m_eng = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_part.lower())
                    if m_eng:
                        hour_extracted = int(m_eng.group(1))
                        minute_extracted = int(m_eng.group(2)) if m_eng.group(2) else 0
                        am_pm = m_eng.group(3)

                        if am_pm == 'pm' and hour_extracted < 12:
                            hour_extracted += 12
                        elif am_pm == 'am' and hour_extracted == 12:
                            hour_extracted = 0

                if hour_extracted is not None:
                    result = candidate_date.replace(
                        hour=hour_extracted,
                        minute=minute_extracted,
                        second=0,
                        microsecond=0
                    )
                    logger.info(f"Parsed MM/DD with time '{nl_time_str}' to {result}")
                    return result

            # No time specified, default to 9 AM
            result = candidate_date.replace(hour=9, minute=0, second=0, microsecond=0)
            logger.info(f"Parsed MM/DD date '{nl_time_str}' to {result}")
            return result

        except Exception as e:
            logger.warning(f"Failed to parse MM/DD format: {e}")

    # ----- Fallback to dateparser library -----
    # dateparser handles many English formats and some international formats
    logger.debug("Trying dateparser library as fallback")

    settings = {
        'PREFER_DATES_FROM': 'future' if prefer_future else 'current_period',
        'TIMEZONE': timezone,
        'RETURN_AS_TIMEZONE_AWARE': True,
        'RELATIVE_BASE': now,
        'PREFER_DAY_OF_MONTH': 'first',  # For "next monday" style patterns
        'PREFER_DATES_FROM': 'future',
    }

    try:
        # Try with languages including English and Chinese
        parsed = dateparser.parse(s, settings=settings, languages=['en', 'zh'])
        if parsed:
            # Ensure timezone-aware
            if parsed.tzinfo is None:
                parsed = tz.localize(parsed)
            else:
                parsed = parsed.astimezone(tz)

            logger.info(f"dateparser successfully parsed '{nl_time_str}' to {parsed}")
            return parsed
        else:
            logger.warning(f"dateparser could not parse: '{nl_time_str}'")
    except Exception as e:
        logger.error(f"dateparser error: {e}")

    # ----- All methods failed -----
    logger.error(f"Failed to parse time string: '{nl_time_str}'")
    return None


def format_datetime_for_calendar(dt: datetime) -> str:
    """Format datetime for Google Calendar API

    Args:
        dt: datetime object (should be timezone-aware)

    Returns:
        RFC3339 formatted string (e.g., '2025-11-05T14:00:00+08:00')
    """
    if dt.tzinfo is None:
        logger.warning("datetime is not timezone-aware, using default timezone")
        config = ConfigManager()
        tz = pytz.timezone(config.get_timezone())
        dt = tz.localize(dt)

    return dt.isoformat()


def parse_duration(duration_str: str) -> Optional[timedelta]:
    """Parse duration string to timedelta

    Args:
        duration_str: Duration string (e.g., "1 hour", "30 minutes", "1小時", "30分鐘")

    Returns:
        timedelta object or None if parsing fails

    Examples:
        >>> parse_duration("1 hour")
        timedelta(hours=1)

        >>> parse_duration("30分鐘")
        timedelta(minutes=30)
    """
    if not duration_str:
        return None

    s = duration_str.lower().strip()

    # Hours
    m = re.search(r'(\d+\.?\d*)\s*(?:hour|hours|hr|hrs|小時|小时)', s)
    if m:
        return timedelta(hours=float(m.group(1)))

    # Minutes
    m = re.search(r'(\d+)\s*(?:minute|minutes|min|mins|分鐘|分钟|分)', s)
    if m:
        return timedelta(minutes=int(m.group(1)))

    # Days
    m = re.search(r'(\d+)\s*(?:day|days|天)', s)
    if m:
        return timedelta(days=int(m.group(1)))

    logger.warning(f"Could not parse duration: '{duration_str}'")
    return None


def get_relative_day_offset(day_str: str) -> Optional[int]:
    """Get day offset for relative day expressions

    Args:
        day_str: Day expression (e.g., "today", "tomorrow", "今天", "明天")

    Returns:
        Day offset (0 for today, 1 for tomorrow, etc.) or None
    """
    s = day_str.lower().strip()

    # Today
    if any(word in s for word in ['today', '今天', '今日']):
        return 0

    # Tomorrow
    if any(word in s for word in ['tomorrow', '明天', '明日']):
        return 1

    # Day after tomorrow
    if any(word in s for word in ['後天', '后天']):
        return 2

    # Yesterday (negative offset)
    if any(word in s for word in ['yesterday', '昨天', '昨日']):
        return -1

    return None
