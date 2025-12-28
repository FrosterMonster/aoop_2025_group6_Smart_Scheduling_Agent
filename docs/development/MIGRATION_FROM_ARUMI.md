# Migration Guide: 阿嚕米 → ai_schedule_agent

This document guides you through migrating from the archived 阿嚕米 codebase to the ai_schedule_agent platform.

## Overview

On December 22, 2025, the阿嚕米 prototype was merged into ai_schedule_agent to consolidate features and improve maintainability. All unique features have been ported, and 阿嚕米 has been archived for reference.

---

## Feature Mapping

| 阿嚕米 Feature | ai_schedule_agent Location | Enhancement |
|--------------|---------------------------|-------------|
| **LLM Agent** (agent_main.py) | `core/llm_agent.py` | Multi-provider support (Claude, OpenAI, Gemini) |
| **Calendar Integration** (calendar_tools.py) | `core/scheduling_engine.py` + `integrations/google_calendar.py` | Advanced scoring, conflict detection |
| **Time Parsing** (calendar_time_parser.py) | `utils/time_parser.py` | Superset of patterns, better English support |
| **Chinese Regex Patterns** (agent_main.py mock_handle) | `core/nlp_processor.py::_extract_with_chinese_patterns()` | Integrated as fallback |
| **DRY_RUN Mode** | `config/manager.py::is_dry_run()` | Configuration-driven |
| **Retry Logic** | `core/llm_agent.py::@retry_with_exponential_backoff` | Applied to all providers |
| **Unit Tests** (test_time_parser.py) | `tests/test_time_parser.py` + `tests/test_nlp_processor.py` | Enhanced coverage |

---

## API Migration

### Calendar Event Creation

**Before (阿嚕米)**:
```python
from calendar_tools import create_calendar_event

result = create_calendar_event(
    summary="Team Meeting",
    description="Quarterly review",
    start_time_str="2025-12-23 14:00:00",
    end_time_str="2025-12-23 15:00:00",
    calendar_id='primary'
)
```

**After (ai_schedule_agent)**:
```python
from ai_schedule_agent.integrations.google_calendar import CalendarIntegration
from ai_schedule_agent.models.event import Event
from datetime import datetime

cal = CalendarIntegration()
event = Event(
    title="Team Meeting",
    description="Quarterly review",
    start_time=datetime(2025, 12, 23, 14, 0),
    end_time=datetime(2025, 12, 23, 15, 0),
    event_type=EventType.MEETING,
    priority=Priority.HIGH
)
result = cal.create_event(event)
```

### Time Parsing

**Before (阿嚕米)**:
```python
from calendar_time_parser import parse_nl_time

dt = parse_nl_time("明天下午2點")
```

**After (ai_schedule_agent)**:
```python
from ai_schedule_agent.utils.time_parser import parse_nl_time

dt = parse_nl_time("明天下午2點", prefer_future=True)
# Returns timezone-aware datetime
```

### Week Planning

**Before (阿嚕米)**:
```python
from calendar_tools import plan_week_schedule

events = plan_week_schedule(
    summary="Study",
    total_hours=10.0,
    chunk_hours=2.0,
    daily_window=(9, 18)
)
```

**After (ai_schedule_agent)**:
```python
from ai_schedule_agent.core.scheduling_engine import SchedulingEngine
from ai_schedule_agent.models.user_profile import UserProfile

engine = SchedulingEngine()
profile = UserProfile()  # Load from config

events = engine.plan_week_schedule(
    title="Study",
    total_hours=10.0,
    chunk_size_hours=2.0,
    user_profile=profile
)
```

---

## Configuration Migration

### Environment Variables

**Before (.env)**:
```bash
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AI...
DRY_RUN=1
```

**After (.env + .config/settings.json)**:

`.env`:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AI...
DRY_RUN=1
```

`.config/settings.json`:
```json
{
  "llm": {
    "use_llm": true,
    "provider": "openai",
    "model": "gpt-4"
  },
  "calendar": {
    "default_duration": 60,
    "timezone": "Asia/Taipei"
  }
}
```

### OAuth Credentials

阿嚕米 and ai_schedule_agent use the same OAuth flow:
- `credentials.json` - Download from Google Cloud Console
- `token.pickle` - Auto-generated on first auth

**No migration needed** - credentials are compatible.

---

## Breaking Changes

### 1. Module Structure

| Old Import | New Import |
|-----------|-----------|
| `from calendar_tools import *` | `from ai_schedule_agent.integrations.google_calendar import *` |
| `from calendar_time_parser import *` | `from ai_schedule_agent.utils.time_parser import *` |
| `from agent_main import run_agent` | `from ai_schedule_agent.core.llm_agent import LLMAgent` |

### 2. Function Signatures

**create_calendar_event**:
- Old: `create_calendar_event(summary, description, start_str, end_str, calendar_id)`
- New: `CalendarIntegration().create_event(Event(...))` - Uses Event dataclass

**parse_nl_time**:
- Old: `parse_nl_time(text)` - Returns naive datetime
- New: `parse_nl_time(text, prefer_future=True)` - Returns timezone-aware datetime

### 3. Return Types

- Event creation now returns `Event` object instead of string message
- Time parsing always returns timezone-aware `datetime` (not naive)

---

## Configuration Paths

### File Locations

| Component | 阿嚕米 | ai_schedule_agent |
|-----------|-------|------------------|
| Credentials | `./credentials.json` | `./.config/credentials.json` or `./credentials.json` |
| Token | `./token.pickle` | `./.config/token.pickle` or `./token.pickle` |
| Logs | `./logs/agent.log` | `./.config/logs/app.log` |
| State | N/A | `./.state/app_state.json` |

### Config Templates

ai_schedule_agent provides templates:
```bash
ls .config/*.example
# paths.json.example
# settings.json.example
```

Copy and customize:
```bash
cp .config/settings.json.example .config/settings.json
# Edit .config/settings.json
```

---

## Running the Application

### Command Line

**阿嚕米**:
```bash
cd 阿嚕米
python agent_main.py
# or
python schedule_task.py --summary "Study" --hours 4
```

**ai_schedule_agent**:
```bash
python -m ai_schedule_agent
# Desktop GUI launches
```

### DRY_RUN Mode

Both support DRY_RUN:
```bash
export DRY_RUN=1  # Unix/Mac
set DRY_RUN=1     # Windows CMD
$env:DRY_RUN='1'  # Windows PowerShell

python -m ai_schedule_agent
```

---

## Testing

### Unit Tests

**阿嚕米**:
```bash
pytest test_time_parser.py -v
```

**ai_schedule_agent**:
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Specific test files
pytest tests/test_time_parser.py -v
pytest tests/test_nlp_processor.py -v

# With coverage
pytest tests/ --cov=ai_schedule_agent --cov-report=html
open htmlcov/index.html
```

---

## New Features in ai_schedule_agent

Features NOT available in 阿嚕米:

1. **Multi-Provider LLM Support**
   - Claude (Anthropic)
   - OpenAI (GPT-3.5/4)
   - Gemini (Google)

2. **Desktop GUI**
   - Modern UI with setup wizard
   - Calendar visualization
   - Settings management
   - Real-time insights

3. **Machine Learning**
   - Pattern learning from user behavior
   - Energy pattern analysis
   - Optimal time slot suggestions

4. **Advanced Scheduling**
   - Priority-based scheduling
   - Conflict detection & resolution
   - Buffer time management
   - Multi-week planning

5. **State Management**
   - Persistent state across sessions
   - Conversation history
   - Learned patterns cache

---

## Troubleshooting

### Issue: Import Error

**Error**: `ModuleNotFoundError: No module named 'calendar_tools'`

**Solution**: Update imports to use ai_schedule_agent package:
```python
# Old
from calendar_tools import create_calendar_event

# New
from ai_schedule_agent.integrations.google_calendar import CalendarIntegration
```

### Issue: Timezone Naive Datetime

**Error**: `TypeError: can't compare offset-naive and offset-aware datetimes`

**Solution**: ai_schedule_agent returns timezone-aware datetimes:
```python
from ai_schedule_agent.utils.time_parser import parse_nl_time
import pytz

dt = parse_nl_time("明天2點")
# dt is already timezone-aware (Asia/Taipei)
```

### Issue: OAuth Token Invalid

**Error**: `google.auth.exceptions.RefreshError: invalid_grant`

**Solution**: Delete old token and re-authenticate:
```bash
rm token.pickle
rm .config/token.pickle
python -m ai_schedule_agent
# Browser auth flow will start
```

---

## Rollback Instructions

If you need to temporarily use 阿嚕米:

```bash
cd 阿嚕米_archived
python agent_main.py
```

**Warning**: 阿嚕米_archived is deprecated and won't receive updates.

---

## Support & Questions

- **Issues**: Open a GitHub issue in the ai_schedule_agent repository
- **Documentation**: See `ai_schedule_agent/README.md`
- **阿嚕米 Archive**: See `阿嚕米_archived/DEPRECATED.md`

---

## Summary Checklist

- [ ] Update imports to use `ai_schedule_agent.*`
- [ ] Replace function calls with new API (Event dataclass, CalendarIntegration)
- [ ] Update configuration to use `.config/` directory
- [ ] Handle timezone-aware datetimes
- [ ] Install new dependencies: `pip install -r requirements.txt`
- [ ] Run tests to verify: `pytest tests/ -v`
- [ ] Delete old阿嚕米 imports from your code

---

**Migration completed on**: 2025-12-22
**阿嚕米 archived in**: `阿嚕米_archived/`
**Active codebase**: `ai_schedule_agent/`
