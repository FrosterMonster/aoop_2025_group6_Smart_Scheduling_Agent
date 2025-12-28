# Helper Scripts Guide

This project includes several helper scripts to make setup and troubleshooting easier.

---

## 🚀 Setup Scripts

### `venv_setup.sh` - Main Setup Script
**Purpose**: Set up your development environment

**When to use**:
- First time setup
- After updating dependencies
- When recreating virtual environment

**What it does**:
- ✅ Detects best Python version (prioritizes 3.12)
- ✅ Warns if Python 3.13 detected
- ✅ Creates virtual environment
- ✅ Installs all Python packages
- ✅ Downloads NLP models
- ✅ Sets up config files
- ✅ Verifies Tkinter availability

**Usage**:
```bash
./venv_setup.sh
```

---

### `run.sh` - Run the Application
**Purpose**: Start the AI Schedule Agent

**When to use**:
- Running the application
- After setup is complete

**What it does**:
- ✅ Activates virtual environment
- ✅ Runs the application
- ✅ Shows clear error messages if issues occur

**Usage**:
```bash
./run.sh
```

---

## 🔧 Fix & Diagnostic Scripts

### `fix_python313.sh` - **⚡ Python 3.13 Auto-Fixer**
**Purpose**: Automatically fix Python 3.13 Tkinter issues

**When to use**:
- When you see "Can't find a usable init.tcl" error
- When you have Python 3.13 and want to switch to 3.12
- When setup fails due to Tkinter issues

**What it does**:
- ✅ Detects your Python versions
- ✅ Finds or guides you to install Python 3.12
- ✅ Backs up old virtual environment
- ✅ Creates new venv with Python 3.12
- ✅ Installs all dependencies
- ✅ Verifies Tkinter works
- ✅ Tests the setup

**Usage**:
```bash
./fix_python313.sh
```

**Windows CMD**:
```cmd
fix_python313.bat
```

**Output**: Beautiful colored progress display

---

### `check_python.sh` - Python Diagnostics
**Purpose**: Check your Python setup and diagnose issues

**When to use**:
- Before setup to verify Python is installed correctly
- When troubleshooting issues
- To see all Python versions on your system
- To check if Tkinter is working

**What it shows**:
- 📋 All Python installations found
- 📋 Python versions
- 📋 Tkinter availability for each version
- 📋 Virtual environment status
- 📋 Specific recommendations based on your setup

**Usage**:
```bash
./check_python.sh
```

**Example Output**:
```
Python Environment Diagnostics
================================

System Python Installations:

  python3.12
    Path:    /usr/bin/python3.12
    Version: 3.12.7
    Tkinter: ✓ (v8.6)
    ✓ Compatible version

  python3.13
    Path:    /usr/bin/python3.13
    Version: 3.13.0
    Tkinter: ✓ (v8.6)
    ⚠ WARNING: Python 3.13 has Tkinter issues on Windows!

Virtual Environment:
  Virtual Environment Python
    Version: 3.12.7
    Tkinter: ✓ (v8.6)

Recommendations:
  ✓ Everything looks good!
    Run the app: ./run.sh
```

---

## 🧪 Test Scripts

### `test_tkinter.py` - Test Tkinter Installation
**Purpose**: Quick test to verify Tkinter works

**When to use**:
- After installing Python
- After fixing Tkinter issues
- To verify Tkinter is working

**What it does**:
- Opens a small test window
- Shows Tkinter version
- Confirms GUI will work

**Usage**:
```bash
python test_tkinter.py
```

---

### `test_calendar_auth.py` - Test Google Calendar
**Purpose**: Test Google Calendar authentication

**When to use**:
- After setting up Google Calendar credentials
- When troubleshooting calendar sync

**Usage**:
```bash
python test_calendar_auth.py
```

---

## 🗂️ Other Scripts

### `setup_config.sh` - Setup Configuration
**Purpose**: Create configuration directories and template files

**When to use**:
- Usually run automatically by `venv_setup.sh`
- Manual setup of config files

**Usage**:
```bash
./setup_config.sh
```

---

### `validate_setup.sh` - Validate Installation
**Purpose**: Comprehensive validation of entire setup

**When to use**:
- After setup to verify everything
- Before deployment
- Troubleshooting

**Usage**:
```bash
./validate_setup.sh
```

---

## 📋 Quick Reference

| Issue | Solution | Command |
|-------|----------|---------|
| Python 3.13 error | Auto-fix script | `./fix_python313.sh` |
| Don't know Python version | Check setup | `./check_python.sh` |
| First time setup | Run setup | `./venv_setup.sh` |
| Run the app | Start app | `./run.sh` |
| Test Tkinter | Test GUI | `python test_tkinter.py` |
| Verify everything | Validate | `./validate_setup.sh` |

---

## 🎯 Common Workflows

### First Time Setup (Normal)
```bash
./check_python.sh      # Check your Python
./venv_setup.sh        # Setup environment
./run.sh               # Run the app
```

### First Time Setup (Have Python 3.13 Error)
```bash
./fix_python313.sh     # One-command fix
./run.sh               # Run the app
```

### After Updating Dependencies
```bash
./venv_setup.sh        # Reinstall packages
```

### Troubleshooting
```bash
./check_python.sh      # Diagnose issues
# If Python 3.13 issue detected:
./fix_python313.sh     # Fix it
# Otherwise:
./venv_setup.sh        # Recreate environment
```

### Testing
```bash
python test_tkinter.py          # Test GUI
python test_calendar_auth.py    # Test Calendar
./validate_setup.sh             # Test everything
```

---

## 🔐 Permissions

All `.sh` scripts need execute permissions:

```bash
chmod +x *.sh
```

This is already done for:
- `venv_setup.sh`
- `run.sh`
- `fix_python313.sh`
- `check_python.sh`
- `setup_config.sh`
- `validate_setup.sh`

---

## 🪟 Windows Users

### Git Bash (Recommended)
All `.sh` scripts work in Git Bash:
```bash
./fix_python313.sh
./check_python.sh
./venv_setup.sh
./run.sh
```

### Windows CMD
Use the `.bat` version when available:
```cmd
fix_python313.bat
```

Or run Python directly:
```cmd
venv\Scripts\python.exe -m ai_schedule_agent
```

---

## 💡 Tips

1. **Always check Python first**: Run `./check_python.sh` before setup
2. **Use the automated fix**: If you have Python 3.13, use `./fix_python313.sh`
3. **Keep scripts updated**: Pull latest changes for bug fixes
4. **Check permissions**: If script won't run, check `chmod +x script.sh`
5. **Read error messages**: Scripts provide clear next steps

---

## 📚 More Help

- **[QUICK_START.md](QUICK_START.md)** - Fastest way to get started
- **[FIX_PYTHON_313_TKINTER_ERROR.md](FIX_PYTHON_313_TKINTER_ERROR.md)** - Python 3.13 fix details
- **[PYTHON_VERSION_GUIDE.md](PYTHON_VERSION_GUIDE.md)** - Version compatibility
- **[README.md](README.md)** - Full project documentation

---

**Questions?** Check the docs above or run `./check_python.sh` for diagnostics!
