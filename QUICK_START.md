# Quick Start Guide

## 🚨 Got the "Can't find a usable init.tcl" Error?

**You're using Python 3.13 on Windows. Here's the ONE-COMMAND FIX:**

### Git Bash Users
```bash
./fix_python313.sh
```

### Windows CMD Users
```cmd
fix_python313.bat
```

**That's it!** The script automatically:
- ✅ Finds or installs Python 3.12
- ✅ Creates a new virtual environment
- ✅ Installs all dependencies
- ✅ Fixes Tkinter issues

Then just run:
```bash
./run.sh
```

---

## 🔍 Not Sure If You Have Issues?

Check your Python setup:

```bash
./check_python.sh
```

This will show you:
- Your Python version
- Whether Tkinter works
- Specific recommendations

---

## 📋 First Time Setup (Normal Installation)

If you DON'T have Python 3.13 issues, follow these steps:

### 1. Install Python 3.12

**Recommended Version**: Python 3.12.7

- **Download**: https://www.python.org/downloads/release/python-3127/
- **During installation**: Check "Add to PATH" and "tcl/tk and IDLE"

### 2. Run Setup Script

```bash
./venv_setup.sh
```

This automatically:
- Creates virtual environment
- Installs all dependencies
- Downloads NLP models
- Sets up configuration

### 3. Configure API Keys

Edit `.env` file and add your API key:

```bash
# For Claude (Recommended)
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-key-here

# OR for OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# OR for Gemini (Free tier available)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key-here
```

### 4. Setup Google Calendar (Optional)

1. Get OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/)
2. Save to `.config/credentials.json`

### 5. Run the Application

```bash
./run.sh
```

---

## 🛠️ Available Tools

| Command | Purpose |
|---------|---------|
| `./check_python.sh` | Check Python setup and diagnose issues |
| `./fix_python313.sh` | Automatically fix Python 3.13 Tkinter issues |
| `./venv_setup.sh` | Create/update virtual environment |
| `./run.sh` | Run the application |
| `python test_tkinter.py` | Test if Tkinter works |

---

## ❓ Common Issues

### Issue 1: "Can't find a usable init.tcl"

**Cause**: Python 3.13 Tkinter bug on Windows

**Solution**: Run the automated fix
```bash
./fix_python313.sh
```

### Issue 2: "No module named 'tkinter'"

**Cause**: Tkinter not installed

**Solution**:
- **Windows**: Reinstall Python, check "tcl/tk and IDLE"
- **Linux**: `sudo apt-get install python3-tk`
- **macOS**: `brew install python-tk`

### Issue 3: Virtual environment uses wrong Python

**Cause**: Multiple Python versions installed

**Solution**: The fix script handles this automatically
```bash
./fix_python313.sh
```

---

## 📚 More Documentation

- **[FIX_PYTHON_313_TKINTER_ERROR.md](FIX_PYTHON_313_TKINTER_ERROR.md)** - Detailed fix guide
- **[PYTHON_VERSION_GUIDE.md](PYTHON_VERSION_GUIDE.md)** - Python version compatibility
- **[README.md](README.md)** - Full project documentation
- **[docs/](docs/)** - Complete documentation

---

## 🎯 TL;DR (Too Long; Didn't Read)

### If you have Python 3.13 error:
```bash
./fix_python313.sh    # Run this ONE command
./run.sh              # Then run the app
```

### If you're setting up for the first time:
```bash
./check_python.sh     # Check your Python
./venv_setup.sh       # Setup environment
./run.sh              # Run the app
```

### Need help?
```bash
./check_python.sh     # Diagnose issues
```

---

**Made with ❤️ by NYCU AOOP Group 6**

*Questions? See [FIX_PYTHON_313_TKINTER_ERROR.md](FIX_PYTHON_313_TKINTER_ERROR.md) or [README.md](README.md)*
