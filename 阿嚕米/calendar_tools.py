from calendar_service import get_calendar_service
from datetime import datetime, timedelta
import pytz

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
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        return f"活動已成功建立！標題: {event.get('summary')}。連結: {event.get('htmlLink')}"
    except Exception as e:
        return f"建立活動時發生錯誤: {e}"

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