# 🤖 AI Schedule Agent

> Intelligent Personal Scheduling Assistant with Google Calendar integration and AI-powered pattern learning.

---

## 🚨 **Got Python 3.13 Error? → [ONE-COMMAND FIX](QUICK_START.md#-got-the-cant-find-a-usable-inittcl-error)**

```bash
./fix_python313.sh  # Automatically fixes Python 3.13 Tkinter issues
```

See **[QUICK_START.md](QUICK_START.md)** for the fastest way to get running!

---

## ✨ Features

- 🗣️ **Natural Language Processing** - Schedule events using plain English
- 📅 **Google Calendar Sync** - Seamless two-way integration
- 🧠 **AI Pattern Learning** - Learns from your scheduling habits
- 📊 **Insights & Analytics** - Understand your time usage
- 🎨 **Modern UI** - Beautiful sidebar interface with glassmorphism
- 🌍 **Multi-language** - English & Traditional Chinese (繁體中文)
- ⚡ **Fast** - 3-second startup with lazy loading

## 🚀 Quick Start

### 1. Setup (One Command)

**IMPORTANT**: Before running setup, ensure tkinter is installed on your system Python:
```bash
python -m tkinter  # Should show a test window
```

If not installed, see [Prerequisites](#-installing-prerequisites) below first.

```bash
./venv_setup.sh
```

This installs dependencies, downloads NLP models, and creates config files. The virtual environment will automatically inherit tkinter from your system Python.

### 2. Configure API Keys

**LLM Provider** (choose one):
```bash
# Option A: Claude (Anthropic) - Recommended
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
echo "LLM_PROVIDER=claude" >> .env

# Option B: OpenAI
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
echo "LLM_PROVIDER=openai" >> .env

# Option C: Google Gemini (Free tier available)
echo "GEMINI_API_KEY=your-gemini-key-here" >> .env
echo "LLM_PROVIDER=gemini" >> .env

# Option D: Groq (Fast & Free tier available)
echo "GROQ_API_KEY=your-groq-key-here" >> .env
echo "LLM_PROVIDER=groq" >> .env
```

**Google Calendar**:
1. Get OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/)
2. Save to `.config/credentials.json`

### 3. Run

```bash
./run.sh
```

**That's it!** 🎉

## 📚 Documentation

- **[Complete Documentation](docs/)** - All guides and references
- **[Setup Guide](docs/guides/SETUP_INSTRUCTIONS.md)** - Detailed setup instructions
- **[Modern UI Guide](docs/guides/MODERN_UI_GUIDE.md)** - Learn the new interface
- **[LLM Setup](docs/guides/LLM_SETUP_GUIDE.md)** - Configure AI providers

## 🎨 Modern UI

The app features a beautiful, modern sidebar interface:

<img src="https://via.placeholder.com/800x500?text=AI+Schedule+Agent+Screenshot" alt="App Screenshot" width="600"/>

**Key Features:**
- 🤖 Sidebar navigation with AI branding
- 📱 Glassmorphism design (2024 trends)
- 🎯 Color-coded event filters
- ⚡ Instant tab switching
- 🌙 Calming blue color scheme

**Switch UI modes:**
```bash
<<<<<<< HEAD
./setup.sh
```

This ensures everyone uses compatible Python packages for their system.

### ⚠️ Do NOT Commit Credentials

Your personal credentials in `.config/` are git-ignored:
- `credentials.json` - Your Google API credentials
- `token.pickle` - Your auth token
- `user_profile.json` - Your preferences
- `settings.json`, `paths.json` - Your config

Only `.example` and `.template` files are shared via git.

---

## Project Structure

```
.
├── setup.sh                # Complete setup script (run this first!)
├── run.sh                  # Run the application
├── main.py                 # Main application code
├── requirements.txt        # Python dependencies
│
├── .config/                # Configuration (user-specific, git-ignored)
│   ├── README.md           # Config documentation
│   ├── *.example           # Templates (shared via git)
│   ├── credentials.json    # YOUR Google credentials (not in git)
│   └── settings.json       # YOUR settings (not in git)
│
├── Documentation files:
│   ├── QUICKSTART.md       # Fast setup guide
│   ├── NEW_USER_SETUP.md   # Detailed setup guide
│   ├── WHAT_TO_MODIFY.md   # What files to edit
│   └── TROUBLESHOOTING.md  # Common issues
│
└── venv/                   # YOUR virtual env (not in git, create with setup.sh)
```

---

## For Team Members

When you clone this repo:

```bash
# 1. Run setup
./setup.sh

# 2. Add your credentials
cp ~/Downloads/your-credentials.json .config/credentials.json

# 3. Run
=======
# Modern UI (default)
>>>>>>> 2646380e138663d85d680e6d33fad2a7caaede3a
./run.sh

# Classic UI
USE_MODERN_UI=false ./run.sh
```

## 💡 Usage Examples

### Natural Language Scheduling

```
"Team meeting tomorrow at 2pm for 1 hour"
"Coffee with John next Friday morning"
"Weekly standup every Monday at 9am"
```

### Quick Actions

- **⚡ Quick Schedule** - Create events with NLP
- **📅 Calendar View** - See your full schedule
- **⚙️ Settings** - Configure preferences
- **📊 Insights** - View analytics

## 🛠️ System Requirements

- **Python**: 3.9 - 3.12 (**3.12.7 recommended** - avoid 3.13 on Windows)
- **OS**: Windows, Linux, or macOS
- **GUI Library**: tkinter (see installation below)
- **Google Account**: For Calendar integration
- **API Key**: Claude (Anthropic), OpenAI, or Gemini

⚠️ **Important**: Python 3.13 has known Tkinter issues on Windows. Use Python 3.12.7 instead.
See [PYTHON_VERSION_GUIDE.md](PYTHON_VERSION_GUIDE.md) for details.

### 📦 Installing Prerequisites

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv python3-tk
```

#### Linux (Fedora/RHEL)
```bash
sudo dnf install python3 python3-pip python3-tkinter
```

#### macOS
```bash
brew install python@3.12  # Includes tkinter
```

#### Windows
- **Download Python 3.12.7** (recommended): https://www.python.org/downloads/release/python-3127/
- During installation, ensure "tcl/tk and IDLE" is checked
- **Avoid Python 3.13** - has known Tkinter compatibility issues
- If already installed, repair: Settings → Apps → Python → Modify → Ensure "tcl/tk and IDLE" is checked

#### Verify Installation
```bash
python -m tkinter  # Should show a test window
# OR
python -m tests.test_tkinter
```

**IMPORTANT**: If you get "Can't find a usable init.tcl" or "Tcl isn't installed" error:

⚡ **QUICK FIX** (Automated - Recommended):
```bash
./fix_python313.sh
```
This script automatically fixes Python 3.13 issues!

📋 **Manual Fix**:
1. **Most likely cause**: You're using Python 3.13 on Windows
2. **Solution**: Install Python 3.12.7 instead
3. Delete the venv folder: `rm -rf venv` (or `rmdir /s venv` on Windows CMD)
4. Run `./venv_setup.sh` again (will auto-detect Python 3.12)

🔍 **Check Your Setup**:
```bash
./check_python.sh  # Diagnose Python issues
```

**Troubleshooting Guides**:
- [FIX_PYTHON_313_TKINTER_ERROR.md](FIX_PYTHON_313_TKINTER_ERROR.md) - Quick fix guide
- [PYTHON_VERSION_GUIDE.md](PYTHON_VERSION_GUIDE.md) - Python version issues
- [TKINTER_INSTALLATION.md](docs/guides/TKINTER_INSTALLATION.md) - Tkinter installation

## 📦 Project Structure

```
ai_schedule_agent/
├── core/                 # Core scheduling logic
│   ├── scheduling_engine.py
│   ├── nlp_processor.py
│   └── pattern_learner.py
├── ui/                   # User interface
│   ├── modern_main_window.py  # Modern sidebar UI
│   ├── main_window.py         # Classic tabbed UI
│   ├── modern_theme.py        # Styling system
│   └── tabs/                  # Tab components
├── integrations/        # External services
│   ├── google_calendar.py
│   ├── llm_provider.py
│   └── notifications.py
├── models/              # Data models
└── utils/               # Utilities

docs/                    # Documentation
├── guides/              # User guides
├── development/         # Developer docs
└── archive/             # Historical docs

.config/                 # User configuration
└── *.example            # Template files
```

## ⚡ Performance

- **Startup**: ~3-4 seconds
- **Memory**: Lightweight (~50MB)
- **Lazy Loading**: Heavy components load on demand
- **Fast**: Optimized imports and caching

See [Performance Docs](docs/development/PERFORMANCE_OPTIMIZATIONS.md) for details.

## 🌍 Internationalization

Fully supports:
- 🇬🇧 **English** (en)
- 🇹🇼 **繁體中文** (zh_TW)

More languages can be added easily. See [i18n Guide](docs/guides/I18N_QUICK_START.md).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is for educational purposes.

## 🙏 Acknowledgments

- **spaCy** - Natural language processing
- **Google Calendar API** - Calendar integration
- **Anthropic Claude** - AI-powered scheduling
- **OpenAI** - Alternative LLM provider

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: [docs/](docs/)
- **Email**: Contact your team

---

## 📖 Quick Links

### For Users
- [Complete Setup Guide](docs/guides/SETUP_INSTRUCTIONS.md)
- [Modern UI Guide](docs/guides/MODERN_UI_GUIDE.md)
- [LLM Configuration](docs/guides/LLM_SETUP_GUIDE.md)

### For Developers
- [Architecture Overview](docs/development/REFACTORING_SUMMARY.md)
- [Performance Details](docs/development/PERFORMANCE_OPTIMIZATIONS.md)
- [Before/After Comparison](docs/development/BEFORE_AFTER_COMPARISON.md)

### Documentation Index
📚 **[Full Documentation Index](docs/README.md)** - All guides and references

---

**Made with ❤️ by NYCU AOOP Group 6**

*AI Schedule Agent - Your intelligent scheduling companion* 🚀
