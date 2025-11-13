import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 授權範圍：允許應用程式對日曆事件進行讀取和寫入，以及查詢空閒/忙碌時段
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',  # 讀寫事件
    'https://www.googleapis.com/auth/calendar.freebusy'  # 查詢空閒/忙碌
]
TOKEN_FILE = 'token.pickle'
CREDS_FILE = 'credentials.json'

def get_calendar_service():
    """建立並返回 Google Calendar API 服務物件。"""
    creds = None
    
    # 嘗試載入儲存的憑證
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # 憑證無效或過期，嘗試重新整理或重新授權
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # 啟動桌面應用程式的 OAuth 流程
            # 注意：這裡會查找您的 credentials.json 檔案
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 儲存憑證供下次使用
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    # 成功連線並取得或更新憑證後，建立服務物件
    service = build('calendar', 'v3', credentials=creds)
    return service

if __name__ == '__main__':
    # 嘗試獲取服務
    service = get_calendar_service()
    
    # 為了確認，嘗試使用最低權限來獲取日曆清單
    try:
        # **關鍵變更：** 我們不使用 list()，而是使用 get('primary') 這種較溫和的調用
        calendar = service.calendars().get(calendarId='primary').execute()
        print("Google Calendar 服務已成功連線！")
        print(f"您的主要日曆名稱: {calendar.get('summary')}")
    except Exception as e:
        print(f"連線測試失敗: {e}")