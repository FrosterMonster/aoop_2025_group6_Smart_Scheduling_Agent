"""
Google Calendar OAuth Service (從阿嚕米_archived移植)

這是精簡版的 Google Calendar 認證服務，
專注於穩定的 OAuth 2.0 流程和 token 管理。
"""

import os
import pickle
import logging
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# 授權範圍：允許應用程式對日曆事件進行讀取和寫入，以及查詢空閒/忙碌時段
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',  # 讀寫事件
    'https://www.googleapis.com/auth/calendar.freebusy'  # 查詢空閒/忙碌
]


class CalendarService:
    """
    Google Calendar OAuth 服務

    這個類別處理所有與 Google Calendar API 認證相關的邏輯，
    包括 token 的儲存、刷新和更新。

    使用範例：
        service = CalendarService(
            token_file='token.pickle',
            credentials_file='credentials.json'
        )
        calendar_api = service.get_service()
    """

    def __init__(self, token_file: str = 'token.pickle',
                 credentials_file: str = 'credentials.json'):
        """
        初始化 Calendar Service

        Args:
            token_file: Token 儲存位置 (default: 'token.pickle')
            credentials_file: Google OAuth credentials 位置 (default: 'credentials.json')
        """
        self.token_file = token_file
        self.credentials_file = credentials_file
        self._service = None
        self._credentials = None

    def get_service(self):
        """
        建立並返回 Google Calendar API 服務物件

        這個方法會：
        1. 檢查是否有已儲存的 token
        2. 如果 token 過期，嘗試刷新
        3. 如果沒有 token 或刷新失敗，啟動 OAuth 流程
        4. 儲存新的 token 供下次使用

        Returns:
            Google Calendar API service object

        Raises:
            FileNotFoundError: 如果 credentials.json 不存在
        """
        if self._service is not None:
            return self._service

        creds = None

        # 1. 嘗試載入儲存的憑證
        if os.path.exists(self.token_file):
            logger.info(f"Loading saved token from: {self.token_file}")
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
            logger.info("✓ Token loaded successfully")

        # 2. 憑證無效或過期，嘗試重新整理或重新授權
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Token expired. Attempting to refresh...")
                try:
                    creds.refresh(Request())
                    logger.info("✓ Token refreshed successfully")
                except Exception as e:
                    logger.warning(f"Token refresh failed: {e}")
                    logger.info("Will request new authorization...")
                    creds = None

            # 3. 需要重新授權
            if not creds:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Google OAuth credentials file not found: {self.credentials_file}\n"
                        f"Please download credentials.json from Google Cloud Console.\n"
                        f"See: .config/README.md for instructions."
                    )

                logger.info("="*60)
                logger.info("GOOGLE CALENDAR AUTHORIZATION REQUIRED")
                logger.info("="*60)
                logger.info("A browser window will open for authentication.")
                logger.info("Steps:")
                logger.info("  1. Sign in to your Google account")
                logger.info("  2. Grant calendar access permissions")
                logger.info("  3. Browser will show 'Authentication successful'")
                logger.info("  4. Return to the application")
                logger.info("")
                logger.info("This only needs to be done ONCE.")
                logger.info("="*60)

                # 啟動桌面應用程式的 OAuth 流程
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)

                logger.info("="*60)
                logger.info("✓ AUTHENTICATION SUCCESSFUL")
                logger.info("="*60)
                logger.info("Token will be saved. You won't need to authenticate again.")
                logger.info("="*60)

            # 4. 儲存憑證供下次使用
            logger.info(f"Saving token to: {self.token_file}")
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
            logger.info("✓ Token saved")

        # 5. 成功連線並取得或更新憑證後，建立服務物件
        self._credentials = creds
        self._service = build('calendar', 'v3', credentials=creds)
        logger.info("✓ Google Calendar service initialized")

        return self._service

    def is_authenticated(self) -> bool:
        """
        檢查是否已認證

        Returns:
            True if authenticated, False otherwise
        """
        return os.path.exists(self.token_file)

    def revoke_authentication(self):
        """
        撤銷認證（刪除 token）

        這會強制下次調用時重新進行 OAuth 流程
        """
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
            logger.info(f"Token removed: {self.token_file}")
            self._service = None
            self._credentials = None


# 全局單例模式（方便使用）
_global_service = None


def get_calendar_service(token_file: str = 'token.pickle',
                         credentials_file: str = 'credentials.json'):
    """
    獲取全局 Calendar Service 單例

    這個函數提供了一個簡單的方式來獲取 Calendar Service，
    適合快速原型開發和簡單應用。

    Args:
        token_file: Token 檔案路徑
        credentials_file: Credentials 檔案路徑

    Returns:
        Google Calendar API service object

    Example:
        >>> service = get_calendar_service()
        >>> events = service.events().list(calendarId='primary').execute()
    """
    global _global_service

    if _global_service is None:
        _global_service = CalendarService(token_file, credentials_file)

    return _global_service.get_service()


if __name__ == '__main__':
    """測試模組"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    print("\n" + "="*60)
    print("Testing Calendar Service")
    print("="*60 + "\n")

    # 測試服務初始化
    service = get_calendar_service()

    # 測試基本 API 調用
    try:
        calendar = service.calendars().get(calendarId='primary').execute()
        print(f"✓ Connection successful!")
        print(f"  Primary calendar: {calendar.get('summary')}")
        print(f"  Time zone: {calendar.get('timeZone')}")
    except Exception as e:
        print(f"✗ Connection test failed: {e}")

    print("\n" + "="*60 + "\n")
