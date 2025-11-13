# Documentation Index

Complete documentation for the AI Schedule Agent project.

## 📚 Quick Links

### Getting Started
- **[Setup Instructions](guides/SETUP_INSTRUCTIONS.md)** - Complete setup guide
- **[LLM Setup Guide](guides/LLM_SETUP_GUIDE.md)** - Configure AI providers (Claude/OpenAI)

### User Guides
- **[Modern UI Guide](guides/MODERN_UI_GUIDE.md)** - Complete modern UI documentation
- **[Modern UI Quick Start](guides/MODERN_UI_QUICK_START.md)** - Quick reference for new UI
- **[Internationalization (i18n) Guide](guides/I18N_QUICK_START.md)** - Multi-language support

### Development Documentation
- **[Performance Optimizations](development/PERFORMANCE_OPTIMIZATIONS.md)** - Performance improvements
- **[Startup Optimization](development/STARTUP_OPTIMIZATION_SUMMARY.md)** - Fast startup implementation
- **[Refactoring Summary](development/REFACTORING_SUMMARY.md)** - Code refactoring details
- **[Before/After Comparison](development/BEFORE_AFTER_COMPARISON.md)** - Architecture evolution

---

## 📖 Documentation Structure

```
docs/
├── README.md                          # This file
├── guides/                            # User guides and how-tos
│   ├── SETUP_INSTRUCTIONS.md         # Complete setup guide
│   ├── LLM_SETUP_GUIDE.md            # AI provider configuration
│   ├── MODERN_UI_GUIDE.md            # Modern UI documentation
│   ├── MODERN_UI_QUICK_START.md      # Quick UI reference
│   ├── MODERN_UI_REDESIGN.md         # UI redesign details
│   ├── MODERN_UI_STATUS.md           # UI implementation status
│   ├── MODERN_UI_SUMMARY.md          # UI summary
│   ├── I18N_QUICK_START.md           # i18n guide
│   ├── UI_I18N_STATUS.md             # i18n implementation status
│   └── UI_IMPROVEMENTS.md            # UI improvement history
├── development/                       # Developer documentation
│   ├── PERFORMANCE_OPTIMIZATIONS.md  # Performance details
│   ├── STARTUP_OPTIMIZATION_SUMMARY.md # Startup optimization
│   ├── REFACTORING_SUMMARY.md        # Refactoring history
│   └── BEFORE_AFTER_COMPARISON.md    # Architecture comparison
└── archive/                           # Archived documentation
    └── REMOVE_VENV_FROM_GIT.md       # Historical reference
```

---

## 🚀 Most Important Documents

### For New Users
1. **[Setup Instructions](guides/SETUP_INSTRUCTIONS.md)** - Start here!
2. **[LLM Setup Guide](guides/LLM_SETUP_GUIDE.md)** - Configure AI features
3. **[Modern UI Guide](guides/MODERN_UI_GUIDE.md)** - Learn the interface

### For Developers
1. **[Refactoring Summary](development/REFACTORING_SUMMARY.md)** - Understand the codebase
2. **[Performance Optimizations](development/PERFORMANCE_OPTIMIZATIONS.md)** - Performance details
3. **[Before/After Comparison](development/BEFORE_AFTER_COMPARISON.md)** - Architecture evolution

---

## 🎨 UI Documentation

The application features a modern, sidebar-based interface:

- **[Modern UI Guide](guides/MODERN_UI_GUIDE.md)** - Complete UI documentation
- **[Modern UI Quick Start](guides/MODERN_UI_QUICK_START.md)** - Quick reference
- **[Modern UI Redesign](guides/MODERN_UI_REDESIGN.md)** - Design decisions
- **[Modern UI Status](guides/MODERN_UI_STATUS.md)** - Implementation status

### Key Features
- 🤖 AI-branded sidebar with navigation
- 📱 Modern glassmorphism design
- 🎨 Color-coded event filters
- ⚡ Fast, responsive interface
- 🌍 Multi-language support (English & 繁體中文)

---

## 🌍 Internationalization

The app supports multiple languages:

- **[i18n Quick Start](guides/I18N_QUICK_START.md)** - How to use translations
- **[i18n Status](guides/UI_I18N_STATUS.md)** - Implementation status

**Supported Languages:**
- English (en)
- Traditional Chinese (zh_TW / 繁體中文)

---

## ⚡ Performance

The application is optimized for speed:

- **Startup Time**: ~3-4 seconds
- **Lazy Loading**: Heavy components load on demand
- **Fast Navigation**: Instant tab switching

See [Performance Optimizations](development/PERFORMANCE_OPTIMIZATIONS.md) for details.

---

## 🛠️ Development

### Architecture
- **Modular package structure** - Clean separation of concerns
- **Lazy loading** - Deferred imports for fast startup
- **Pattern learning** - AI-powered scheduling
- **Google Calendar integration** - Seamless sync

### Code Quality
- **Type hints** - Better IDE support
- **Logging** - Comprehensive logging system
- **Error handling** - Robust error management
- **Testing ready** - Structure supports testing

---

## 📝 Contributing

When adding documentation:

1. **User guides** → `docs/guides/`
2. **Development docs** → `docs/development/`
3. **Archived docs** → `docs/archive/`

Keep the main `README.md` in the project root concise and link to detailed docs here.

---

## 🔗 External Resources

- [Google Calendar API Documentation](https://developers.google.com/calendar)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [spaCy NLP Documentation](https://spacy.io/)

---

**Last Updated**: 2025-11-05
