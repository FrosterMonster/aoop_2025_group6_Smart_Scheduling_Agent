# AI Schedule Agent Package

This directory contains the refactored modular package structure for the AI Schedule Agent application.

## Package Structure

```
ai_schedule_agent/
├── __init__.py                 # Package initialization
├── __main__.py                 # Entry point (python -m ai_schedule_agent)
│
├── config/                     # Configuration management
│   ├── __init__.py
│   └── manager.py              # ConfigManager singleton
│
├── models/                     # Data models
│   ├── __init__.py
│   ├── enums.py                # EventType, Priority enums
│   ├── user_profile.py         # UserProfile dataclass
│   └── event.py                # Event dataclass
│
├── core/                       # Business logic
│   ├── __init__.py
│   ├── pattern_learner.py      # ML pattern recognition
│   ├── scheduling_engine.py    # Core scheduling algorithms
│   └── nlp_processor.py        # Natural language processing
│
├── integrations/               # External service integrations
│   ├── __init__.py
│   ├── google_calendar.py      # Google Calendar API
│   └── notifications.py        # Notification management
│
├── ui/                         # User interface components
│   ├── __init__.py
│   ├── main_window.py          # Main application window
│   ├── setup_wizard.py         # First-time setup wizard
│   ├── tabs/                   # Tab modules
│   │   ├── __init__.py
│   │   ├── quick_schedule_tab.py
│   │   ├── calendar_view_tab.py
│   │   ├── settings_tab.py
│   │   └── insights_tab.py
│   └── components/             # Reusable UI components
│       └── __init__.py
│
└── utils/                      # Utility modules
    ├── __init__.py
    └── logging.py              # Logging configuration
```

## Module Responsibilities

### Configuration Layer (`config/`)
- **manager.py**: Singleton ConfigManager for centralized configuration
  - Loads paths.json and settings.json
  - Auto-creates config files from templates
  - Provides get_path() and get_setting() methods

### Data Models (`models/`)
- **enums.py**: EventType and Priority enumerations
- **user_profile.py**: User preferences, working hours, energy patterns
- **event.py**: Event data with Google Calendar serialization

### Core Business Logic (`core/`)
- **pattern_learner.py**: Machine learning for scheduling patterns using K-Means clustering
- **scheduling_engine.py**: Optimal time slot finding, conflict detection, scoring algorithms
- **nlp_processor.py**: Natural language parsing using spaCy and dateparser

### Integrations (`integrations/`)
- **google_calendar.py**: OAuth 2.0 authentication, event CRUD, FreeBusy API
- **notifications.py**: Desktop notifications (plyer) and email (SMTP)

### User Interface (`ui/`)
- **main_window.py**: Main orchestrator, initializes all components and tabs
- **setup_wizard.py**: First-time user onboarding (5-step wizard)
- **tabs/**: Individual tab modules for modularity
  - Each tab is self-contained with its own UI logic
  - Communicates with main_window via callbacks

### Utilities (`utils/`)
- **logging.py**: Centralized logging configuration

## Running the Application

```bash
# From project root
python -m ai_schedule_agent

# Or using the run script
./run.sh
```

## Benefits of This Structure

1. **Separation of Concerns**: Clear boundaries between UI, business logic, and data
2. **Testability**: Each module can be unit tested independently
3. **Maintainability**: ~120 LOC per file vs. 2019 LOC monolith
4. **Scalability**: Easy to add new features without conflicts
5. **Reusability**: Core logic can be reused without UI dependencies
6. **Type Safety**: Clear interfaces with type hints throughout

## Development Guidelines

### Adding a New Feature

1. **Determine the layer**: Is it UI, business logic, or integration?
2. **Create/modify appropriate module**: Keep modules focused and cohesive
3. **Update imports**: Use absolute imports (`from ai_schedule_agent.models import Event`)
4. **Add tests**: Create corresponding test file in tests/ directory
5. **Update documentation**: Keep this README current

### Coding Standards

- Use type hints for all function signatures
- Follow PEP 8 naming conventions
- Keep functions under 50 lines
- Document classes and complex functions with docstrings
- Use absolute imports, not relative

## Dependencies Between Modules

```
config.manager (standalone)
    ↓
models.* (use config)
    ↓
core.* (use models)
    ↓
integrations.* (use models, config)
    ↓
ui.* (orchestrates all layers)
```

## Migration from Original main.py

The original monolithic [main.py](main.py) (2019 lines) has been refactored into:
- **17 focused modules** (~100-150 LOC each)
- **5 architectural layers** (config, models, core, integrations, ui)
- **Clear dependency hierarchy**

All functionality remains the same, but now with:
- Better organization
- Easier testing
- Clearer dependencies
- More maintainable codebase
