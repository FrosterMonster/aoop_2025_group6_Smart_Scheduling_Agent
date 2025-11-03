from calendar_service import get_calendar_service
from datetime import datetime, timedelta
import pytz
import logging

# 使用與 agent 相同的 logger 名稱以便集中紀錄
logger = logging.getLogger("agent")

# 專案提案中定義的時區
TIMEZONE = 'Asia/Taipei' 

def create_calendar_event(summary: str, description: str, start_time_str: str, end_time_str: str, calendar_id: str = 'primary') -> str:
    """
    在 Google Calendar 中建立一個新活動。

    Args:
        summary (str): 活動標題。
        description (str): 活動描述或筆記。
        start_time_str (str): 活動開始時間，格式為 'YYYY-MM-DD HH:MM:SS'。
        end_time_str (str): 活動結束時間，格式為 'YYYY-MM-DD HH:MM:SS'。
        calendar_id (str): 要建立活動的日曆 ID，'primary' 指預設日曆。
        
    Returns:
        str: 建立成功後的活動連結或錯誤訊息。
    """
    # 如果設置 DRY_RUN=1，則不會呼叫 Google API，僅回傳模擬訊息（方便本地測試）
    import os
    if os.getenv('DRY_RUN') == '1':
        logger.info("DRY_RUN active - not creating event: summary=%s start=%s end=%s calendar=%s", summary, start_time_str, end_time_str, calendar_id)
        return f"DRY_RUN: would create event '{summary}' from {start_time_str} to {end_time_str} on calendar {calendar_id}"

    service = get_calendar_service()
    
    # 1. 處理時間：將字串時間轉換為帶時區的 datetime 物件
    try:
        local_tz = pytz.timezone(TIMEZONE)
        # 注意：Agent 邏輯必須確保輸入是 'YYYY-MM-DD HH:MM:SS' 格式
        start_dt = local_tz.localize(datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S'))
        end_dt = local_tz.localize(datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S'))
    except ValueError as e:
        return f"時間格式錯誤。請確保時間為 'YYYY-MM-DD HH:MM:SS'。錯誤: {e}"

    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': TIMEZONE},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': TIMEZONE},
    }

    try:
        # 2. 調用 API 寫入事件
        logger.info("Calling Google Calendar API to create event: summary=%s calendar=%s", summary, calendar_id)
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        logger.info("Event created: id=%s summary=%s", event.get('id'), event.get('summary'))
        return f"活動已成功建立！標題: {event.get('summary')}。連結: {event.get('htmlLink')}"
    except Exception as e:
        logger.error("建立活動時發生錯誤: %s", e)
        return f"建立活動時發生錯誤: {e}"


def _iso(dt: datetime) -> str:
    return dt.astimezone(pytz.utc).isoformat()


def get_busy_periods(calendar_id: str, start_dt: datetime, end_dt: datetime):
    """Query Google Calendar Freebusy for busy periods between start_dt and end_dt.

    Returns list of dicts with 'start' and 'end' ISO strings.
    """
    service = get_calendar_service()
    body = {
        "timeMin": start_dt.astimezone(pytz.utc).isoformat(),
        "timeMax": end_dt.astimezone(pytz.utc).isoformat(),
        "items": [{"id": calendar_id}]
    }
    try:
        resp = service.freebusy().query(body=body).execute()
        busy = resp.get('calendars', {}).get(calendar_id, {}).get('busy', [])
        return busy
    except Exception as e:
        logger.error("freebusy query failed: %s", e)
        # On failure, return empty busy list to avoid blocking scheduling
        return []


def find_free_slots_between(start_dt: datetime, end_dt: datetime, busy_periods: list, min_duration_minutes: int = 60):
    """Compute free slots between start_dt and end_dt given busy_periods (list of {'start','end'}),
    returning list of (free_start_dt, free_end_dt) in local timezone.
    """
    tz = pytz.timezone(TIMEZONE)
    # normalize busy periods to datetime
    busy = []
    for b in busy_periods:
        try:
            bs = datetime.fromisoformat(b['start']).astimezone(tz)
            be = datetime.fromisoformat(b['end']).astimezone(tz)
            busy.append((bs, be))
        except Exception:
            continue

    # sort and merge busy
    busy.sort(key=lambda x: x[0])
    merged = []
    for bs, be in busy:
        if not merged:
            merged.append((bs, be))
        else:
            last_s, last_e = merged[-1]
            if bs <= last_e:
                merged[-1] = (last_s, max(last_e, be))
            else:
                merged.append((bs, be))

    free_slots = []
    cur = start_dt.astimezone(tz)
    for bs, be in merged:
        if (bs - cur).total_seconds() >= min_duration_minutes * 60:
            free_slots.append((cur, bs))
        cur = max(cur, be)

    if (end_dt.astimezone(tz) - cur).total_seconds() >= min_duration_minutes * 60:
        free_slots.append((cur, end_dt.astimezone(tz)))

    return free_slots


def plan_week_schedule(summary: str, total_hours: float, calendar_id: str = 'primary',
                       week_start: datetime | None = None, chunk_hours: float = 2.0,
                       daily_window: tuple = (9, 18), max_weeks: int = 4) -> list:
    """Plan a weekly schedule for `summary` totaling `total_hours` hours.

    - week_start: datetime for the week start (Monday). If None, use next Monday.
    - chunk_hours: preferred chunk size in hours (e.g., 2.0)
    - daily_window: tuple(start_hour, end_hour) in local time to consider for scheduling.
    - max_weeks: maximum number of weeks to look ahead for free slots.

    Returns list of created event results (or DRY_RUN messages).
    """
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    # 如果沒指定開始週，從今天開始找
    if week_start is None:
        week_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        week_start = week_start.astimezone(tz).replace(hour=0, minute=0, second=0, microsecond=0)

    planned = []
    current_week_start = week_start
    weeks_tried = 0
    hours_left = total_hours

    # 持續找空檔直到排滿或超過最大週數
    while hours_left > 0 and weeks_tried < max_weeks:
        # 建立這週的時間視窗（每天的 daily_window 區間）
        candidate_windows = []
        for d in range(7):
            day = current_week_start + timedelta(days=d)
            # 跳過已經過去的時段
            if day < now:
                continue
            start_dt = day.replace(hour=daily_window[0], minute=0, second=0, microsecond=0)
            end_dt = day.replace(hour=daily_window[1], minute=0, second=0, microsecond=0)
            candidate_windows.append((start_dt, end_dt))

        if not candidate_windows:
            # 這週沒有可用時段，試下週
            current_week_start += timedelta(days=7)
            weeks_tried += 1
            continue

        # 查詢這週的忙碌時段
        overall_start = candidate_windows[0][0]
        overall_end = candidate_windows[-1][1]
        busy_periods = get_busy_periods(calendar_id, overall_start, overall_end)

        # 在這週的空閒時段中嘗試排程
        min_chunk = int(chunk_hours * 60)
        hours_left = total_hours - sum((p['end'] - p['start']).total_seconds() / 3600 for p in planned)

        for day_start, day_end in candidate_windows:
            if hours_left <= 0:
                break
            frees = find_free_slots_between(day_start, day_end, busy_periods, min_duration_minutes=30)
            
            # 在這天的空檔中嘗試安排
            for fs, fe in frees:
                if hours_left <= 0:
                    break
                slot_minutes = int((fe - fs).total_seconds() // 60)
                # 在這個空檔中建立固定大小的時段直到填滿或空檔用完
                cur = fs
                while slot_minutes >= min_chunk and hours_left > 0:
                    take_minutes = min(min_chunk, slot_minutes, int(hours_left * 60))
                    end_take = cur + timedelta(minutes=take_minutes)
                    # 建立活動
                    res = create_calendar_event(
                        summary, 
                        '自動排程 (總時數目標: {:.1f}h)'.format(total_hours),
                        cur.strftime('%Y-%m-%d %H:%M:%S'), 
                        end_take.strftime('%Y-%m-%d %H:%M:%S'), 
                        calendar_id=calendar_id
                    )
                    planned.append({'start': cur, 'end': end_take, 'result': res})
                    # 前進到下一個位置
                    hours_left -= take_minutes / 60.0
                    cur = end_take
                    slot_minutes = int((fe - cur).total_seconds() // 60)

        # 如果這週沒排完，往下週找
        if hours_left > 0:
            current_week_start += timedelta(days=7)
            weeks_tried += 1
        else:
            break

    return planned

# 獨立測試區塊
if __name__ == '__main__':
    # 計算一個未來時間，例如現在時間的 30 分鐘後到 60 分鐘後
    now = datetime.now()
    start = now + timedelta(minutes=30)
    end = now + timedelta(minutes=60)
    
    result = create_calendar_event(
        summary="Agent 核心功能測試",
        description="這是您的第一個成功寫入的日曆活動！",
        start_time_str=start.strftime('%Y-%m-%d %H:%M:%S'),
        end_time_str=end.strftime('%Y-%m-%d %H:%M:%S')
    )
    print(result)