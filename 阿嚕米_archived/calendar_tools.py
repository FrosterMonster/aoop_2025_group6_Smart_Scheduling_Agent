from calendar_service import get_calendar_service
from datetime import datetime, timedelta
import pytz
import logging

# 使用與 agent 相同的 logger 名稱以便集中紀錄
logger = logging.getLogger("agent")

# 專案提案中定義的時區
TIMEZONE = 'Asia/Taipei' 

def get_all_calendar_ids(service):
    """獲取使用者清單中所有勾選的日曆 ID"""
    calendar_list = service.calendarList().list().execute()
    # 這裡過濾出在截圖中看到的那些日曆
    return [item['id'] for item in calendar_list.get('items', [])]


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


def plan_week_schedule(service, summary, total_hours, daily_window=(9, 21)):
    """
    搜尋未來 7 天內的空檔，並避開所有日曆中的忙碌時段
    """
    calendar_ids = get_all_calendar_ids(service)
    now = datetime.now()
    
    # 準備 FreeBusy 查詢：一次檢查未來 7 天
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=7)).isoformat() + 'Z'
    
    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "items": [{"id": cid} for cid in calendar_ids]
    }
    
    # 向 Google 詢問哪些時段是忙碌的
    freebusy_res = service.freebusy().query(body=body).execute()
    
    # 整合所有日曆的忙碌時段
    all_busy_periods = []
    for cal_id in calendar_ids:
        periods = freebusy_res['calendars'].get(cal_id, {}).get('busy', [])
        all_busy_periods.extend(periods)
    
    # 這裡簡化邏輯：尋找第一個符合 daily_window 且不衝突的 1 小時空檔
    # (實際演算法會比這複雜，這邊先提供一個確保能運行的基礎版本)
    test_start = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    
    for _ in range(168): # 檢查未來 168 小時
        if test_start.hour < daily_window[0] or test_start.hour >= daily_window[1]:
            test_start += timedelta(hours=1)
            continue
            
        test_end = test_start + timedelta(hours=total_hours)
        
        # 檢查是否與任何忙碌時段重疊
        is_conflict = False
        for busy in all_busy_periods:
            b_start = datetime.fromisoformat(busy['start'].replace('Z', ''))
            b_end = datetime.fromisoformat(busy['end'].replace('Z', ''))
            if not (test_end <= b_start or test_start >= b_end):
                is_conflict = True
                break
        
        if not is_conflict:
            # 找到空檔了！回傳格式與你的 web_app 匹配
            return [{
                'start': test_start,
                'end': test_end,
                'result': f"幫你找到了！這個時段避開了你的{len(calendar_ids)}個日曆衝突"
            }]
        
        test_start += timedelta(hours=1)
    
    raise Exception("抱歉，這週真的排不進去了！")
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