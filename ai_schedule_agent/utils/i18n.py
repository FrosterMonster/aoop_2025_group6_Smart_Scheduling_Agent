"""Internationalization (i18n) support for AI Schedule Agent"""

import json
import os
from typing import Dict, Optional

from ai_schedule_agent.config.manager import ConfigManager
from ai_schedule_agent.utils.logging import logger


class I18n:
    """Internationalization manager for multi-language support"""

    # Translation dictionaries
    TRANSLATIONS = {
        'en': {
            # Application
            'app_name': 'AI Schedule Agent',
            'app_title': 'AI Schedule Agent - Intelligent Personal Scheduling',

            # Common UI
            'ok': 'OK',
            'cancel': 'Cancel',
            'close': 'Close',
            'save': 'Save',
            'delete': 'Delete',
            'edit': 'Edit',
            'add': 'Add',
            'remove': 'Remove',
            'yes': 'Yes',
            'no': 'No',
            'loading': 'Loading...',
            'ready': 'Ready',
            'error': 'Error',
            'success': 'Success',
            'warning': 'Warning',

            # Tabs
            'tab_quick_schedule': 'Quick Schedule',
            'tab_calendar_view': 'Calendar View',
            'tab_settings': 'Settings',
            'tab_insights': 'Insights',

            # Quick Schedule Tab
            'quick_schedule_title': 'Quick Event Scheduling',
            'enter_request': 'Enter your scheduling request:',
            'request_placeholder': 'e.g., "Schedule a meeting with John tomorrow at 2pm"',
            'schedule_button': 'Schedule',
            'clear_button': 'Clear',
            'processing': 'Processing...',
            'event_details': 'Event Details',
            'confirm_schedule': 'Confirm & Schedule',

            # Event fields
            'event_title': 'Title',
            'event_type': 'Type',
            'event_date': 'Date',
            'event_time': 'Time',
            'event_duration': 'Duration',
            'event_location': 'Location',
            'event_participants': 'Participants',
            'event_priority': 'Priority',
            'event_description': 'Description',

            # Event types
            'event_type_meeting': 'Meeting',
            'event_type_focus': 'Focus Time',
            'event_type_break': 'Break',
            'event_type_personal': 'Personal',
            'event_type_task': 'Task',

            # Priority levels
            'priority_low': 'Low',
            'priority_medium': 'Medium',
            'priority_high': 'High',
            'priority_critical': 'Critical',

            # Calendar View
            'calendar_title': 'Your Schedule',
            'today': 'Today',
            'week_view': 'Week View',
            'month_view': 'Month View',
            'refresh': 'Refresh',
            'no_events': 'No events scheduled',

            # Settings Tab
            'settings_title': 'Application Settings',
            'general_settings': 'General Settings',
            'language_setting': 'Language',
            'language_english': 'English',
            'language_chinese': '繁體中文 (Traditional Chinese)',
            'working_hours': 'Working Hours',
            'monday': 'Monday',
            'tuesday': 'Tuesday',
            'wednesday': 'Wednesday',
            'thursday': 'Thursday',
            'friday': 'Friday',
            'saturday': 'Saturday',
            'sunday': 'Sunday',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'notifications': 'Notifications',
            'enable_notifications': 'Enable Desktop Notifications',
            'email_notifications': 'Email Notifications',
            'llm_settings': 'AI Settings',
            'llm_provider': 'LLM Provider',
            'api_key': 'API Key',
            'save_settings': 'Save Settings',
            'settings_saved': 'Settings saved successfully',

            # Insights Tab
            'insights_title': 'Schedule Insights & Analytics',
            'loading_analytics': 'Loading analytics... (this may take a moment)',
            'generate_insights': 'Generate Insights',
            'productivity_patterns': 'Productivity Patterns',
            'time_distribution': 'Time Distribution',
            'suggestions': 'Suggestions',
            'no_data': 'Not enough data for analysis',

            # Status messages
            'status_ready': 'Ready',
            'status_processing': 'Processing your request...',
            'status_scheduling': 'Scheduling event...',
            'status_loading': 'Loading...',

            # Success messages
            'event_scheduled': 'Event "{title}" scheduled successfully!',
            'event_updated': 'Event updated successfully',
            'event_deleted': 'Event deleted successfully',

            # Error messages
            'error_invalid_input': 'Invalid input. Please check your request.',
            'error_scheduling_failed': 'Failed to schedule event. Please try again.',
            'error_calendar_sync': 'Failed to sync with Google Calendar',
            'error_no_connection': 'No internet connection',
            'error_api_key': 'Invalid or missing API key',

            # First run setup
            'setup_welcome': 'Welcome to AI Schedule Agent!',
            'setup_instructions': 'Let\'s set up your preferences',
            'setup_complete': 'Setup complete! You can now start scheduling.',
        },

        'zh_TW': {
            # Application
            'app_name': 'AI 行程助理',
            'app_title': 'AI 行程助理 - 智能個人行程管理',

            # Common UI
            'ok': '確定',
            'cancel': '取消',
            'close': '關閉',
            'save': '儲存',
            'delete': '刪除',
            'edit': '編輯',
            'add': '新增',
            'remove': '移除',
            'yes': '是',
            'no': '否',
            'loading': '載入中...',
            'ready': '就緒',
            'error': '錯誤',
            'success': '成功',
            'warning': '警告',

            # Tabs
            'tab_quick_schedule': '快速排程',
            'tab_calendar_view': '行事曆檢視',
            'tab_settings': '設定',
            'tab_insights': '深入分析',

            # Quick Schedule Tab
            'quick_schedule_title': '快速活動排程',
            'enter_request': '輸入您的排程請求：',
            'request_placeholder': '例如：「明天下午兩點與 John 開會」',
            'schedule_button': '排程',
            'clear_button': '清除',
            'processing': '處理中...',
            'event_details': '活動詳情',
            'confirm_schedule': '確認並排程',

            # Event fields
            'event_title': '標題',
            'event_type': '類型',
            'event_date': '日期',
            'event_time': '時間',
            'event_duration': '持續時間',
            'event_location': '地點',
            'event_participants': '參與者',
            'event_priority': '優先順序',
            'event_description': '描述',

            # Event types
            'event_type_meeting': '會議',
            'event_type_focus': '專注時間',
            'event_type_break': '休息',
            'event_type_personal': '個人事項',
            'event_type_task': '任務',

            # Priority levels
            'priority_low': '低',
            'priority_medium': '中',
            'priority_high': '高',
            'priority_critical': '緊急',

            # Calendar View
            'calendar_title': '您的行程',
            'today': '今天',
            'week_view': '週檢視',
            'month_view': '月檢視',
            'refresh': '重新整理',
            'no_events': '尚無排定活動',

            # Settings Tab
            'settings_title': '應用程式設定',
            'general_settings': '一般設定',
            'language_setting': '語言',
            'language_english': 'English (英文)',
            'language_chinese': '繁體中文 (Traditional Chinese)',
            'working_hours': '工作時間',
            'monday': '星期一',
            'tuesday': '星期二',
            'wednesday': '星期三',
            'thursday': '星期四',
            'friday': '星期五',
            'saturday': '星期六',
            'sunday': '星期日',
            'start_time': '開始時間',
            'end_time': '結束時間',
            'notifications': '通知',
            'enable_notifications': '啟用桌面通知',
            'email_notifications': '電子郵件通知',
            'llm_settings': 'AI 設定',
            'llm_provider': 'LLM 提供者',
            'api_key': 'API 金鑰',
            'save_settings': '儲存設定',
            'settings_saved': '設定已成功儲存',

            # Insights Tab
            'insights_title': '行程深入分析與統計',
            'loading_analytics': '載入分析中...（這可能需要一點時間）',
            'generate_insights': '產生分析',
            'productivity_patterns': '生產力模式',
            'time_distribution': '時間分配',
            'suggestions': '建議',
            'no_data': '資料不足，無法進行分析',

            # Status messages
            'status_ready': '就緒',
            'status_processing': '正在處理您的請求...',
            'status_scheduling': '正在排程活動...',
            'status_loading': '載入中...',

            # Success messages
            'event_scheduled': '活動「{title}」已成功排程！',
            'event_updated': '活動已成功更新',
            'event_deleted': '活動已成功刪除',

            # Error messages
            'error_invalid_input': '輸入無效，請檢查您的請求。',
            'error_scheduling_failed': '無法排程活動，請重試。',
            'error_calendar_sync': '無法與 Google 日曆同步',
            'error_no_connection': '無網路連線',
            'error_api_key': 'API 金鑰無效或遺失',

            # First run setup
            'setup_welcome': '歡迎使用 AI 行程助理！',
            'setup_instructions': '讓我們設定您的偏好',
            'setup_complete': '設定完成！您現在可以開始排程了。',
        }
    }

    def __init__(self, config: Optional[ConfigManager] = None):
        """Initialize i18n manager

        Args:
            config: Configuration manager instance
        """
        self.config = config or ConfigManager()
        self._current_language = self._load_language()
        logger.info(f"I18n initialized with language: {self._current_language}")

    def _load_language(self) -> str:
        """Load language preference from config

        Returns:
            Language code (e.g., 'en', 'zh_TW')
        """
        language = self.config.get_setting('ui', 'language', default='en')

        # Validate language is supported
        if language not in self.TRANSLATIONS:
            logger.warning(f"Unsupported language '{language}', falling back to 'en'")
            language = 'en'

        return language

    def set_language(self, language: str):
        """Set current language and save to config

        Args:
            language: Language code (e.g., 'en', 'zh_TW')
        """
        if language not in self.TRANSLATIONS:
            logger.error(f"Cannot set unsupported language: {language}")
            return False

        self._current_language = language
        self.config.set_setting('ui', 'language', language)
        logger.info(f"Language changed to: {language}")
        return True

    def get_language(self) -> str:
        """Get current language code

        Returns:
            Current language code
        """
        return self._current_language

    def t(self, key: str, **kwargs) -> str:
        """Translate a key to current language

        Args:
            key: Translation key
            **kwargs: Format parameters for string formatting

        Returns:
            Translated string
        """
        translations = self.TRANSLATIONS.get(self._current_language, self.TRANSLATIONS['en'])
        text = translations.get(key, key)

        # Apply string formatting if kwargs provided
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing format parameter in translation '{key}': {e}")

        return text

    def get_available_languages(self) -> Dict[str, str]:
        """Get list of available languages

        Returns:
            Dictionary mapping language codes to display names
        """
        return {
            'en': 'English',
            'zh_TW': '繁體中文'
        }


# Global i18n instance
_i18n_instance = None


def get_i18n(config: Optional[ConfigManager] = None) -> I18n:
    """Get global i18n instance (singleton pattern)

    Args:
        config: Optional configuration manager

    Returns:
        Global I18n instance
    """
    global _i18n_instance

    if _i18n_instance is None:
        _i18n_instance = I18n(config)

    return _i18n_instance


def t(key: str, **kwargs) -> str:
    """Convenience function for translation

    Args:
        key: Translation key
        **kwargs: Format parameters

    Returns:
        Translated string
    """
    return get_i18n().t(key, **kwargs)
