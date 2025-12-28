"""
Google Calendar 工具函數 (從阿嚕米_archived移植)

這個模組包含了核心的 Google Calendar 操作邏輯：
1. create_calendar_event - 建立日曆事件
2. get_busy_periods - 使用 FreeBusy API 查詢忙碌時段
3. find_free_slots_between - 找出空閒時段（時間區間合併算法）
4. plan_week_schedule - 智能週排程

這些函數是阿嚕米_archived系統的核心，已被證明穩定可靠。
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import pytz

from ai_schedule_agent.integrations.calendar_service import get_calendar_service

logger = logging.getLogger(__name__)

# 專案使用的時區
TIMEZONE = 'Asia/Taipei'


def create_calendar_event(
    summary: str,
    description: str,
    start_time_str: str,
    end_time_str: str,
    calendar_id: str = 'primary',
    service=None
) -> str:
    """
    在 Google Calendar 中建立一個新活動

    Args:
        summary: 活動標題
        description: 活動描述或筆記
        start_time_str: 活動開始時間，格式為 'YYYY-MM-DD HH:MM:SS'
        end_time_str: 活動結束時間，格式為 'YYYY-MM-DD HH:MM:SS'
        calendar_id: 要建立活動的日曆 ID，'primary' 指預設日曆
        service: Google Calendar service object (optional)

    Returns:
        建立成功後的活動連結或錯誤訊息

    Example:
        >>> result = create_calendar_event(
        ...     "團隊會議",
        ...     "討論 Q1 規劃",
        ...     "2025-12-29 14:00:00",
        ...     "2025-12-29 15:00:00"
        ... )
        >>> print(result)
        活動已成功建立！標題: 團隊會議。連結: https://...
    """
    # DRY_RUN 保護機制：如果設置環境變數，則不會呼叫 Google API
    if os.getenv('DRY_RUN') == '1':
        logger.info(
            f"DRY_RUN active - not creating event: "
            f"summary={summary} start={start_time_str} end={end_time_str} calendar={calendar_id}"
        )
        return (
            f"DRY_RUN: would create event '{summary}' "
            f"from {start_time_str} to {end_time_str} on calendar {calendar_id}"
        )

    # 獲取 Calendar service
    if service is None:
        service = get_calendar_service()

    # 1. 處理時間：將字串時間轉換為帶時區的 datetime 物件
    try:
        local_tz = pytz.timezone(TIMEZONE)
        # Agent 邏輯必須確保輸入是 'YYYY-MM-DD HH:MM:SS' 格式
        start_dt = local_tz.localize(
            datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        )
        end_dt = local_tz.localize(
            datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
        )
    except ValueError as e:
        error_msg = (
            f"時間格式錯誤。請確保時間為 'YYYY-MM-DD HH:MM:SS'。"
            f"錯誤: {e}"
        )
        logger.error(error_msg)
        return error_msg

    # 2. 建立事件物件
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': TIMEZONE
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': TIMEZONE
        },
    }

    try:
        # 3. 調用 API 寫入事件
        logger.info(
            f"Calling Google Calendar API to create event: "
            f"summary={summary} calendar={calendar_id}"
        )
        event_result = service.events().insert(
            calendarId=calendar_id,
            body=event
        ).execute()

        logger.info(
            f"Event created: id={event_result.get('id')} "
            f"summary={event_result.get('summary')}"
        )

        return (
            f"活動已成功建立！標題: {event_result.get('summary')}。"
            f"連結: {event_result.get('htmlLink')}"
        )

    except Exception as e:
        error_msg = f"建立活動時發生錯誤: {e}"
        logger.error(error_msg)
        return error_msg


def get_busy_periods(
    calendar_id: str,
    start_dt: datetime,
    end_dt: datetime,
    service=None
) -> List[Dict[str, str]]:
    """
    使用 Google Calendar FreeBusy API 查詢忙碌時段

    這是一個高效的方法來獲取時間範圍內的所有忙碌時段，
    比逐一查詢事件更快。

    Args:
        calendar_id: 日曆 ID (e.g., 'primary')
        start_dt: 查詢開始時間 (timezone-aware datetime)
        end_dt: 查詢結束時間 (timezone-aware datetime)
        service: Google Calendar service object (optional)

    Returns:
        List of busy periods, each with 'start' and 'end' ISO strings
        Example: [{'start': '2025-12-29T10:00:00+08:00', 'end': '2025-12-29T11:00:00+08:00'}]

    Example:
        >>> tz = pytz.timezone('Asia/Taipei')
        >>> start = tz.localize(datetime(2025, 12, 29, 0, 0, 0))
        >>> end = tz.localize(datetime(2025, 12, 30, 0, 0, 0))
        >>> busy = get_busy_periods('primary', start, end)
        >>> print(len(busy))  # 顯示有幾個忙碌時段
    """
    if service is None:
        service = get_calendar_service()

    # 建立 FreeBusy 查詢請求
    body = {
        "timeMin": start_dt.astimezone(pytz.utc).isoformat(),
        "timeMax": end_dt.astimezone(pytz.utc).isoformat(),
        "items": [{"id": calendar_id}]
    }

    try:
        logger.debug(
            f"Querying FreeBusy: {calendar_id} "
            f"from {start_dt} to {end_dt}"
        )

        resp = service.freebusy().query(body=body).execute()
        busy = resp.get('calendars', {}).get(calendar_id, {}).get('busy', [])

        logger.debug(f"Found {len(busy)} busy periods")
        return busy

    except Exception as e:
        logger.error(f"FreeBusy query failed: {e}")
        # 失敗時返回空列表，避免阻塞排程
        return []


def find_free_slots_between(
    start_dt: datetime,
    end_dt: datetime,
    busy_periods: List[Dict[str, str]],
    min_duration_minutes: int = 60
) -> List[Tuple[datetime, datetime]]:
    """
    計算空閒時段（使用時間區間合併算法）

    這個函數實現了經典的「時間區間合併」算法，
    用於在已知忙碌時段的情況下找出所有空閒時段。

    算法步驟：
    1. 將所有忙碌時段按開始時間排序
    2. 合併重疊的忙碌時段
    3. 計算相鄰忙碌時段之間的空閒時間

    Args:
        start_dt: 搜尋範圍開始時間
        end_dt: 搜尋範圍結束時間
        busy_periods: 忙碌時段列表 (from get_busy_periods)
        min_duration_minutes: 最小空閒時段長度（分鐘）

    Returns:
        List of (free_start, free_end) tuples in local timezone

    Example:
        >>> tz = pytz.timezone('Asia/Taipei')
        >>> start = tz.localize(datetime(2025, 12, 29, 8, 0))
        >>> end = tz.localize(datetime(2025, 12, 29, 18, 0))
        >>> busy = [{'start': '2025-12-29T10:00:00Z', 'end': '2025-12-29T11:00:00Z'}]
        >>> free = find_free_slots_between(start, end, busy)
        >>> # 結果: [(8:00-10:00), (11:00-18:00)]
    """
    tz = pytz.timezone(TIMEZONE)

    # 1. 將忙碌時段轉換為 datetime 並正規化為本地時區
    busy = []
    for b in busy_periods:
        try:
            bs = datetime.fromisoformat(b['start'].replace('Z', '+00:00')).astimezone(tz)
            be = datetime.fromisoformat(b['end'].replace('Z', '+00:00')).astimezone(tz)
            busy.append((bs, be))
        except Exception as e:
            logger.warning(f"Failed to parse busy period: {b} - {e}")
            continue

    # 2. 排序並合併重疊的忙碌時段
    busy.sort(key=lambda x: x[0])

    merged = []
    for bs, be in busy:
        if not merged:
            merged.append((bs, be))
        else:
            last_s, last_e = merged[-1]
            if bs <= last_e:
                # 有重疊，合併
                merged[-1] = (last_s, max(last_e, be))
            else:
                # 無重疊，新增
                merged.append((bs, be))

    logger.debug(
        f"Merged {len(busy)} busy periods into {len(merged)} "
        f"non-overlapping periods"
    )

    # 3. 計算空閒時段
    free_slots = []
    cur = start_dt.astimezone(tz)

    for bs, be in merged:
        # 當前位置到下一個忙碌時段之間的時間
        if (bs - cur).total_seconds() >= min_duration_minutes * 60:
            free_slots.append((cur, bs))
        cur = max(cur, be)

    # 最後一個忙碌時段後到結束時間
    if (end_dt.astimezone(tz) - cur).total_seconds() >= min_duration_minutes * 60:
        free_slots.append((cur, end_dt.astimezone(tz)))

    logger.debug(f"Found {len(free_slots)} free slots")

    return free_slots


def plan_week_schedule(
    summary: str,
    total_hours: float,
    calendar_id: str = 'primary',
    week_start: Optional[datetime] = None,
    chunk_hours: float = 2.0,
    daily_window: Tuple[int, int] = (9, 18),
    max_weeks: int = 4,
    service=None
) -> List[Dict]:
    """
    智能週排程：自動在日曆中找空檔並排入事件

    這是阿嚕米_archived的核心功能，能夠：
    1. 查詢未來幾週的忙碌時段
    2. 找出所有可用的空閒時段
    3. 按照指定的 chunk 大小自動排入事件
    4. 持續到排滿指定的總時數或超過最大週數

    Args:
        summary: 事件名稱（如「讀電子學」）
        total_hours: 總共要安排幾小時（如 4.0）
        calendar_id: 日曆 ID (default: 'primary')
        week_start: 從哪一週開始（None = 從今天開始）
        chunk_hours: 每次安排幾小時（default: 2.0）
        daily_window: 每天可用時段（default: 9:00-18:00）
        max_weeks: 最多往後找幾週（default: 4）
        service: Google Calendar service object (optional)

    Returns:
        List of created events with 'start', 'end', 'result' keys

    Example:
        >>> planned = plan_week_schedule("讀電子學", total_hours=4.0, chunk_hours=2.0)
        >>> for p in planned:
        ...     print(f"{p['start']} -> {p['end']}: {p['result']}")
    """
    if service is None:
        service = get_calendar_service()

    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)

    # 如果沒指定開始週，從今天開始找
    if week_start is None:
        week_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        week_start = week_start.astimezone(tz).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    planned = []
    current_week_start = week_start
    weeks_tried = 0
    hours_left = total_hours

    logger.info(
        f"Starting week schedule planning: summary='{summary}' "
        f"total_hours={total_hours} chunk_hours={chunk_hours}"
    )

    # 主循環：逐週找空檔
    while hours_left > 0 and weeks_tried < max_weeks:
        logger.debug(f"Searching week {weeks_tried+1}, hours_left={hours_left:.1f}")

        # 1. 建立這週的時間視窗（每天的 daily_window 區間）
        candidate_windows = []
        for d in range(7):
            day = current_week_start + timedelta(days=d)

            # 跳過已經過去的時段
            if day < now:
                continue

            start_dt = day.replace(
                hour=daily_window[0], minute=0, second=0, microsecond=0
            )
            end_dt = day.replace(
                hour=daily_window[1], minute=0, second=0, microsecond=0
            )
            candidate_windows.append((start_dt, end_dt))

        if not candidate_windows:
            # 這週沒有可用時段，試下週
            current_week_start += timedelta(days=7)
            weeks_tried += 1
            logger.debug("No available windows this week, moving to next week")
            continue

        # 2. 查詢這週的忙碌時段
        overall_start = candidate_windows[0][0]
        overall_end = candidate_windows[-1][1]
        busy_periods = get_busy_periods(calendar_id, overall_start, overall_end, service)

        logger.debug(f"Found {len(busy_periods)} busy periods in this week")

        # 3. 在這週的空閒時段中嘗試排程
        min_chunk = int(chunk_hours * 60)

        for day_start, day_end in candidate_windows:
            if hours_left <= 0:
                break

            # 找出這天的空閒時段
            frees = find_free_slots_between(
                day_start, day_end, busy_periods,
                min_duration_minutes=30
            )

            logger.debug(
                f"Day {day_start.date()}: found {len(frees)} free slots"
            )

            # 在空閒時段中安排
            for fs, fe in frees:
                if hours_left <= 0:
                    break

                slot_minutes = int((fe - fs).total_seconds() // 60)
                cur = fs

                # 在這個空檔中持續安排
                while slot_minutes >= min_chunk and hours_left > 0:
                    # 計算這次要安排多久
                    take_minutes = min(
                        min_chunk,
                        slot_minutes,
                        int(hours_left * 60)
                    )
                    end_take = cur + timedelta(minutes=take_minutes)

                    # 建立活動
                    res = create_calendar_event(
                        summary,
                        f'自動排程 (總時數目標: {total_hours:.1f}h)',
                        cur.strftime('%Y-%m-%d %H:%M:%S'),
                        end_take.strftime('%Y-%m-%d %H:%M:%S'),
                        calendar_id=calendar_id,
                        service=service
                    )

                    planned.append({
                        'start': cur,
                        'end': end_take,
                        'result': res
                    })

                    logger.info(
                        f"Scheduled: {cur.strftime('%Y-%m-%d %H:%M')} -> "
                        f"{end_take.strftime('%H:%M')} ({take_minutes}min)"
                    )

                    # 更新剩餘時數
                    hours_left -= take_minutes / 60.0
                    cur = end_take
                    slot_minutes = int((fe - cur).total_seconds() // 60)

        # 如果這週排不完，往下週找
        if hours_left > 0:
            current_week_start += timedelta(days=7)
            weeks_tried += 1
        else:
            break

    logger.info(
        f"Planning complete: scheduled {len(planned)} events, "
        f"remaining hours: {hours_left:.1f}"
    )

    return planned


if __name__ == '__main__':
    """測試模組"""
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    # 設定 DRY_RUN 模式
    os.environ['DRY_RUN'] = '1'

    print("\n" + "="*60)
    print("Testing Calendar Tools (DRY_RUN mode)")
    print("="*60 + "\n")

    # 測試 1: 建立單一事件
    print("Test 1: Create single event")
    now = datetime.now()
    start = now + timedelta(minutes=30)
    end = now + timedelta(minutes=90)

    result = create_calendar_event(
        summary="測試會議",
        description="這是一個測試事件",
        start_time_str=start.strftime('%Y-%m-%d %H:%M:%S'),
        end_time_str=end.strftime('%Y-%m-%d %H:%M:%S')
    )
    print(f"Result: {result}\n")

    # 測試 2: plan_week_schedule
    print("Test 2: Plan week schedule (4 hours, 2-hour chunks)")
    planned = plan_week_schedule("讀電子學", total_hours=4.0, chunk_hours=2.0)

    if planned:
        print(f"\nScheduled {len(planned)} time slots:")
        for i, p in enumerate(planned, 1):
            print(
                f"{i}. {p['start'].strftime('%Y-%m-%d %H:%M')} -> "
                f"{p['end'].strftime('%H:%M')}"
            )
    else:
        print("No slots scheduled (this is expected in DRY_RUN mode)")

    print("\n" + "="*60 + "\n")
