# Quick Start: Using Traditional Chinese (繁體中文)

## For Users - 使用者指南

### How to Change Language - 如何更改語言

1. **Run the application** - 執行應用程式
   ```bash
   ./run.sh
   ```

2. **Go to Settings tab** - 前往「設定」分頁
   - Click on "Settings" / "設定" tab

3. **Select your language** - 選擇您的語言
   - Find "Language" / "語言" dropdown
   - Choose "繁體中文 (Traditional Chinese)" or "English"

4. **Save and restart** - 儲存並重新啟動
   - Click "Save Settings" / "儲存設定"
   - Restart the application

### Language Options - 語言選項

| Language | Code | Display Name |
|----------|------|--------------|
| English | `en` | English |
| Traditional Chinese | `zh_TW` | 繁體中文 |

## UI Features - UI 功能

### What's Translated - 已翻譯內容

✅ **All Tab Names** - 所有分頁名稱
- Quick Schedule → 快速排程
- Calendar View → 行事曆檢視
- Settings → 設定
- Insights → 深入分析

✅ **All Buttons** - 所有按鈕
- Schedule → 排程
- Clear → 清除
- Save → 儲存
- Delete → 刪除

✅ **All Status Messages** - 所有狀態訊息
- Ready → 就緒
- Loading... → 載入中...
- Processing... → 處理中...

✅ **Event Types** - 活動類型
- Meeting → 會議
- Focus Time → 專注時間
- Break → 休息
- Personal → 個人事項
- Task → 任務

✅ **Priority Levels** - 優先順序
- Low → 低
- Medium → 中
- High → 高
- Critical → 緊急

✅ **Days of Week** - 星期
- Monday → 星期一
- Tuesday → 星期二
- ...and so on

### Chinese Font Support - 中文字型支援

The app automatically uses Chinese-compatible fonts:
- **Windows:** Microsoft YaHei (微軟正黑體)
- **macOS:** PingFang TC
- **Linux:** System Chinese fonts

All Chinese characters display correctly! ✓

## For Developers - 開發者指南

### Using i18n in Your Code

```python
from ai_schedule_agent.utils.i18n import get_i18n

# Get instance
i18n = get_i18n()

# Translate
text = i18n.t('app_name')
# Returns: "AI Schedule Agent" (en) or "AI 行程助理" (zh_TW)

# With parameters
text = i18n.t('event_scheduled', title='Meeting')
# Returns formatted string in current language
```

### Adding Translations

Edit `ai_schedule_agent/utils/i18n.py`:

```python
TRANSLATIONS = {
    'en': {
        'my_new_feature': 'My New Feature',
    },
    'zh_TW': {
        'my_new_feature': '我的新功能',
    }
}
```

### Using in UI Components

```python
class MyTab:
    def __init__(self, parent, i18n):
        self.i18n = i18n

        # Create widgets with translations
        ttk.Label(parent, text=self.i18n.t('label_key'))
        ttk.Button(parent, text=self.i18n.t('button_key'))
```

## Examples - 範例

### English Interface
```
┌──────────────────────────────────────────┐
│ AI Schedule Agent                         │
├──────────────────────────────────────────┤
│ Quick Schedule │ Calendar │ Settings     │
├──────────────────────────────────────────┤
│ Enter your scheduling request:           │
│ [Schedule Meeting with John tomorrow 2pm]│
│ [Schedule] [Clear]                        │
│ Ready                                     │
└──────────────────────────────────────────┘
```

### Chinese Interface - 繁體中文介面
```
┌──────────────────────────────────────────┐
│ AI 行程助理                                │
├──────────────────────────────────────────┤
│ 快速排程 │ 行事曆 │ 設定                   │
├──────────────────────────────────────────┤
│ 輸入您的排程請求：                          │
│ [明天下午兩點與 John 開會]                  │
│ [排程] [清除]                              │
│ 就緒                                       │
└──────────────────────────────────────────┘
```

## Testing - 測試

### Quick Test
```bash
# Run app
./run.sh

# Check current language in Settings tab
# Try switching between English and 繁體中文
# Restart and verify UI displays correctly
```

### Verify Chinese Display
- Open any tab
- All Chinese characters should be clear (not boxes □)
- Font should be readable
- No mojibake (亂碼)

## Files Modified - 修改的檔案

```
ai_schedule_agent/
├── utils/
│   └── i18n.py              # NEW - i18n system
├── ui/
│   └── main_window.py        # UPDATED - i18n + styling
└── config/
    └── settings.json         # UPDATED - language setting
```

## Summary - 總結

**English:**
The AI Schedule Agent now fully supports Traditional Chinese (繁體中文) with a modern, improved UI. Switch between languages in Settings tab.

**繁體中文：**
AI 行程助理現在完全支援繁體中文，並具有現代化的改進介面。在設定分頁中切換語言。

**Ready to use! 準備就緒！ 🚀**
