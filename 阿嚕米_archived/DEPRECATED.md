# 阿嚕米 - ARCHIVED

⚠️ **This codebase has been merged into ai_schedule_agent on 2025-12-22**

## What Was Merged

The following unique features from 阿嚕米 have been integrated into ai_schedule_agent:

### 1. Chinese Regex Fallback Patterns
- **Location**: `ai_schedule_agent/core/nlp_processor.py`
- **Method**: `_extract_with_chinese_patterns()`
- **Features**:
  - Chinese bracket extraction: 「」 "" 『』
  - Time range parsing with '到' (to)
  - Relative date patterns: 今天/明天/後天
  - Automatic duration calculation

### 2. Unit Tests
- **Location**: `tests/test_time_parser.py` and `tests/test_nlp_processor.py`
- **Coverage**:
  - Chinese and English time parsing
  - Natural language pattern extraction
  - Edge cases and known limitations

### 3. Retry Logic with Exponential Backoff
- **Location**: `ai_schedule_agent/core/llm_agent.py`
- **Decorator**: `@retry_with_exponential_backoff(max_retries=2)`
- **Applied to**: All LLM providers (Claude, OpenAI, Gemini)
- **Behavior**: 1s → 2s → 4s retry delays

## What Was NOT Merged (Already in ai_schedule_agent)

The following features were already present in ai_schedule_agent in superior form:

- **DRY_RUN mode** - ASA has better implementation in ConfigManager
- **plan_week_schedule** - ASA uses FreeBusy API with advanced scoring
- **Chinese time parsing** - ASA's `utils/time_parser.py` is a superset
- **OAuth handling** - ASA has better error recovery
- **Multi-provider LLM** - ASA supports 3 providers vs 阿嚕米's 1

## Migration Guide

### Old Code (阿嚕米)
```python
from calendar_tools import create_calendar_event
create_calendar_event("Meeting", "desc", "2025-12-23 14:00:00", "2025-12-23 15:00:00")
```

### New Code (ai_schedule_agent)
```python
from ai_schedule_agent.integrations.google_calendar import CalendarIntegration
from ai_schedule_agent.models.event import Event
from datetime import datetime

cal = CalendarIntegration()
event = Event(
    title="Meeting",
    description="desc",
    start_time=datetime(2025, 12, 23, 14, 0),
    end_time=datetime(2025, 12, 23, 15, 0)
)
cal.create_event(event)
```

## How to Use ai_schedule_agent Instead

```bash
cd ..
python -m ai_schedule_agent
```

Or for testing with DRY_RUN:
```bash
export DRY_RUN=1
python -m ai_schedule_agent
```

## File Mapping

| 阿嚕米 File | ai_schedule_agent Equivalent | Status |
|------------|----------------------------|---------|
| agent_main.py | core/llm_agent.py | ✅ Replaced (multi-provider) |
| calendar_service.py | integrations/google_calendar.py | ✅ Replaced (better auth) |
| calendar_tools.py | core/scheduling_engine.py | ✅ Enhanced |
| calendar_time_parser.py | utils/time_parser.py | ✅ Superset |
| web_app.py | (not ported) | ❌ Desktop UI only |
| test_time_parser.py | tests/test_time_parser.py | ✅ Enhanced |

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=ai_schedule_agent --cov-report=html
```

## Important Notes

1. **DO NOT use this archived code for new development**
2. **All new features should be added to ai_schedule_agent**
3. **This archive is for reference only**
4. **Git history preserves all阿嚕米 changes**

## Questions?

See the main project README or `MIGRATION_FROM_ARUMI.md` for detailed migration instructions.

---

**Archived on**: 2025-12-22
**Reason**: Consolidated into ai_schedule_agent for better maintainability and feature completeness
