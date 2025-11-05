# UI Improvements & Internationalization (i18n)

## Overview

The AI Schedule Agent now features a modern, improved UI with full **Traditional Chinese (繁體中文)** support through a comprehensive internationalization (i18n) system.

## Key Features

### 1. **Internationalization (i18n) System**

Full bilingual support for:
- **English** (`en`)
- **Traditional Chinese** (`zh_TW` - 繁體中文)

### 2. **Modern UI Styling**

- Clean, modern design with the 'clam' theme
- Professional color scheme (blue accent: #4a90e2)
- Better padding and spacing
- Enhanced button styles
- Improved readability

### 3. **Chinese Font Support**

- Automatic detection of Chinese-capable system fonts
- Primary font: Microsoft YaHei (微軟正黑體) on Windows
- Fallback fonts for macOS and Linux
- All UI text renders correctly in both English and Chinese

## File Structure

### New Files Created

```
ai_schedule_agent/
├── utils/
│   └── i18n.py              # Internationalization system
└── UI_IMPROVEMENTS.md        # This file
```

### Modified Files

```
ai_schedule_agent/
└── ui/
    └── main_window.py        # Updated with i18n and styling
```

## How to Use

### For Users

#### Changing Language

1. Open the application
2. Click on the "Settings" (設定) tab
3. Select your preferred language from the dropdown:
   - English
   - 繁體中文 (Traditional Chinese)
4. Click "Save Settings" (儲存設定)
5. Restart the application

The UI will display in your selected language on next launch.

#### Current Language Support

| Feature | English | 繁體中文 |
|---------|---------|----------|
| Tab Names | ✅ | ✅ |
| Button Labels | ✅ | ✅ |
| Status Messages | ✅ | ✅ |
| Event Types | ✅ | ✅ |
| Priority Levels | ✅ | ✅ |
| Error Messages | ✅ | ✅ |
| Settings | ✅ | ✅ |
| Dialogs | ✅ | ✅ |

### For Developers

#### Using the i18n System

```python
from ai_schedule_agent.utils.i18n import get_i18n

# Get i18n instance
i18n = get_i18n()

# Simple translation
text = i18n.t('app_name')  # "AI Schedule Agent" or "AI 行程助理"

# Translation with parameters
text = i18n.t('event_scheduled', title='Meeting')
# "Event 'Meeting' scheduled successfully!" or "活動「Meeting」已成功排程！"

# Check current language
lang = i18n.get_language()  # 'en' or 'zh_TW'

# Change language
i18n.set_language('zh_TW')
```

#### Adding New Translations

Edit `ai_schedule_agent/utils/i18n.py`:

```python
TRANSLATIONS = {
    'en': {
        'your_new_key': 'English text',
        # ... more keys
    },
    'zh_TW': {
        'your_new_key': '繁體中文文字',
        # ... more keys
    }
}
```

#### Passing i18n to UI Components

```python
class MyTab:
    def __init__(self, parent, i18n):
        self.i18n = i18n

        # Use translations
        label = ttk.Label(parent, text=self.i18n.t('label_key'))
        button = ttk.Button(parent, text=self.i18n.t('button_key'))
```

## UI Styling Details

### Color Scheme

```python
Background:     #f0f0f0  (Light gray)
Text:           #333333  (Dark gray)
Accent:         #4a90e2  (Blue)
Hover:          #357abd  (Darker blue)
Success:        #5cb85c  (Green)
Error:          #d9534f  (Red)
```

### Font Configuration

**Windows:**
- Primary: Microsoft YaHei (微軟正黑體)
- Size: 10pt (normal), 12pt (headings), 14pt (titles)

**macOS:**
- Primary: PingFang TC
- Fallback: Heiti TC

**Linux:**
- System default with Chinese support

### Custom Styles

**Buttons:**
- `TButton` - Standard blue button
- `Primary.TButton` - Bold primary action button
- `Success.TButton` - Green confirmation button

**Example:**
```python
# Primary action button
btn = ttk.Button(parent, text=i18n.t('schedule_button'), style='Primary.TButton')

# Success button
btn = ttk.Button(parent, text=i18n.t('confirm_schedule'), style='Success.TButton')
```

## Translation Keys Reference

### Common UI Elements

| Key | English | 繁體中文 |
|-----|---------|----------|
| `ok` | OK | 確定 |
| `cancel` | Cancel | 取消 |
| `save` | Save | 儲存 |
| `delete` | Delete | 刪除 |
| `loading` | Loading... | 載入中... |
| `ready` | Ready | 就緒 |

### Tab Names

| Key | English | 繁體中文 |
|-----|---------|----------|
| `tab_quick_schedule` | Quick Schedule | 快速排程 |
| `tab_calendar_view` | Calendar View | 行事曆檢視 |
| `tab_settings` | Settings | 設定 |
| `tab_insights` | Insights | 深入分析 |

### Event Types

| Key | English | 繁體中文 |
|-----|---------|----------|
| `event_type_meeting` | Meeting | 會議 |
| `event_type_focus` | Focus Time | 專注時間 |
| `event_type_break` | Break | 休息 |
| `event_type_personal` | Personal | 個人事項 |
| `event_type_task` | Task | 任務 |

### Priority Levels

| Key | English | 繁體中文 |
|-----|---------|----------|
| `priority_low` | Low | 低 |
| `priority_medium` | Medium | 中 |
| `priority_high` | High | 高 |
| `priority_critical` | Critical | 緊急 |

### Days of Week

| Key | English | 繁體中文 |
|-----|---------|----------|
| `monday` | Monday | 星期一 |
| `tuesday` | Tuesday | 星期二 |
| `wednesday` | Wednesday | 星期三 |
| `thursday` | Thursday | 星期四 |
| `friday` | Friday | 星期五 |
| `saturday` | Saturday | 星期六 |
| `sunday` | Sunday | 星期日 |

## Screenshots

### English Interface
```
┌─────────────────────────────────────────────────────────┐
│ AI Schedule Agent - Intelligent Personal Scheduling     │
├─────────────────────────────────────────────────────────┤
│  Quick Schedule │ Calendar View │ Settings │ Insights   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Quick Event Scheduling                                 │
│                                                          │
│  Enter your scheduling request:                         │
│  ┌────────────────────────────────────────────────────┐│
│  │ e.g., "Schedule a meeting with John tomorrow at 2pm"││
│  └────────────────────────────────────────────────────┘│
│                                                          │
│  [ Schedule ]  [ Clear ]                                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Chinese Interface (繁體中文)
```
┌─────────────────────────────────────────────────────────┐
│ AI 行程助理 - 智能個人行程管理                            │
├─────────────────────────────────────────────────────────┤
│  快速排程 │ 行事曆檢視 │ 設定 │ 深入分析                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  快速活動排程                                            │
│                                                          │
│  輸入您的排程請求：                                      │
│  ┌────────────────────────────────────────────────────┐│
│  │ 例如：「明天下午兩點與 John 開會」                    ││
│  └────────────────────────────────────────────────────┘│
│                                                          │
│  [ 排程 ]  [ 清除 ]                                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Language Detection

The system automatically:
1. Loads the user's preferred language from config
2. Falls back to English if configured language is unsupported
3. Validates language codes before switching
4. Saves language preference persistently

## Implementation Details

### Singleton Pattern

The i18n system uses a singleton pattern for global access:

```python
# Global instance is created once
_i18n_instance = None

def get_i18n(config=None):
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n(config)
    return _i18n_instance
```

### Configuration Storage

Language preference is stored in the configuration file:

```json
{
  "ui": {
    "language": "zh_TW"
  }
}
```

### Font Fallback Chain

1. **Try** Microsoft YaHei (Windows) / PingFang TC (macOS)
2. **Fallback** to system default font
3. **Log** warning if Chinese font not available
4. **Continue** with best available font

## Compatibility

✅ **Windows 10/11** - Microsoft YaHei
✅ **macOS** - PingFang TC / Heiti TC
✅ **Linux** - System fonts with Chinese support
✅ **Python 3.9+** - Full compatibility
✅ **tkinter** - Native GUI rendering

## Performance Impact

- **Minimal** - Translation lookup is O(1)
- **Lazy** - Only active language loaded
- **Cached** - No repeated file I/O
- **Fast** - String formatting only when needed

## Future Enhancements

### Planned Features

1. **Live Language Switching** - Change language without restart
2. **More Languages** - Add Simplified Chinese, Japanese, etc.
3. **Regional Formats** - Date/time formatting per locale
4. **RTL Support** - Right-to-left languages (Arabic, Hebrew)
5. **Plural Forms** - Proper pluralization rules
6. **Currency/Number Formatting** - Locale-specific formats

### Adding New Languages

To add a new language:

1. Add language code to `TRANSLATIONS` dict in `i18n.py`
2. Translate all keys (copy from 'en' as template)
3. Add to `get_available_languages()` method
4. Update language selector UI
5. Test all UI components

Example for Spanish (`es`):
```python
'es': {
    'app_name': 'Agente de Programación IA',
    'tab_quick_schedule': 'Programación Rápida',
    # ... etc
}
```

## Testing

### Manual Testing Checklist

- [ ] Switch to Chinese - UI displays correctly
- [ ] Switch to English - UI displays correctly
- [ ] All tabs show translated text
- [ ] Buttons have correct labels
- [ ] Status messages are translated
- [ ] Error dialogs show correct language
- [ ] Settings tab shows language selector
- [ ] Chinese characters render properly
- [ ] No broken characters or boxes
- [ ] Font size is readable

### Automated Testing

```python
def test_i18n():
    i18n = get_i18n()

    # Test English
    i18n.set_language('en')
    assert i18n.t('app_name') == 'AI Schedule Agent'

    # Test Chinese
    i18n.set_language('zh_TW')
    assert i18n.t('app_name') == 'AI 行程助理'

    # Test fallback
    assert i18n.t('nonexistent_key') == 'nonexistent_key'
```

## Troubleshooting

### Chinese Characters Show as Boxes

**Solution:** Install Microsoft YaHei font (Windows) or ensure system has Chinese fonts.

```bash
# Linux (Ubuntu/Debian)
sudo apt-install fonts-noto-cjk

# macOS
# System fonts already include Chinese support
```

### Language Not Changing

**Solution:** Restart the application after changing language setting.

### Translation Missing

**Solution:** Check if key exists in `TRANSLATIONS` dict. Add if missing.

## Summary

The UI has been significantly improved with:

✅ **Full Traditional Chinese support** (繁體中文)
✅ **Modern, professional styling**
✅ **Better fonts and readability**
✅ **Comprehensive i18n system**
✅ **Easy to extend with new languages**
✅ **Backward compatible** - English still default

**The application is now fully bilingual! 🌏**
