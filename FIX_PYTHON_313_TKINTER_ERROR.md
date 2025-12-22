# Fix for Python 3.13 Tkinter Error

## Error You're Seeing

```
_tkinter.TclError: Can't find a usable init.tcl in the following directories:
    C:/Users/.../Python313/lib/tcl8.6 ...

This probably means that Tcl wasn't installed properly.
```

## What Happened

You're experiencing a **known issue with Python 3.13 on Windows**. The Tkinter/Tcl libraries don't work properly even when Python is correctly installed.

## Quick Fix (Recommended)

### Step 1: Install Python 3.12.7

1. **Download Python 3.12.7**:
   - Visit: https://www.python.org/downloads/release/python-3127/
   - Download "Windows installer (64-bit)"

2. **Install Python 3.12.7**:
   - Run the installer
   - ✅ Check "Add Python to PATH"
   - ✅ **IMPORTANT**: Ensure "tcl/tk and IDLE" is checked
   - Complete installation

### Step 2: Remove Old Virtual Environment

Open Git Bash (or Command Prompt) in your project directory:

```bash
rm -rf venv
```

Or on Windows CMD:
```cmd
rmdir /s venv
```

### Step 3: Recreate Virtual Environment

The setup script has been updated to automatically detect and prefer Python 3.12:

```bash
./venv_setup.sh
```

**What the script will do**:
- Search for Python 3.12 first (prioritized)
- Warn you if only Python 3.13 is found
- Ask for confirmation before using Python 3.13
- Create the virtual environment with the correct Python version

### Step 4: Run the Application

```bash
./run.sh
```

**Done!** 🎉 The application should now start without errors.

---

## What Changed (Technical Details)

The following improvements have been made to prevent this issue:

### 1. Updated `venv_setup.sh`
- **Prioritizes Python 3.12** over other versions
- Searches for Python versions in this order:
  1. `python3.12` (highest priority)
  2. `python3.11`
  3. `python3.10`
  4. `python3.9`
  5. `python3`, `python`, `py` (fallbacks)
- **Detects Python 3.13** and warns users with clear instructions
- **Asks for confirmation** before proceeding with Python 3.13
- Exits setup if user chooses not to continue

### 2. Updated `ai_schedule_agent/__main__.py`
- **Better error handling** for Tkinter initialization
- **Specific error messages** for the "init.tcl" error
- **Clear instructions** pointing users to install Python 3.12
- Catches Tkinter errors at multiple stages:
  - Initial import
  - GUI component initialization
  - Setup wizard launch
  - Main application launch

### 3. New Documentation
- **[PYTHON_VERSION_GUIDE.md](PYTHON_VERSION_GUIDE.md)** - Comprehensive Python version guide
- **README.md** updated with Python 3.13 warnings
- This fix guide (FIX_PYTHON_313_TKINTER_ERROR.md)

---

## Verification Steps

After following the fix, verify everything is working:

### 1. Check Python Version
```bash
python --version
```
Should show: `Python 3.12.x`

### 2. Test Tkinter
```bash
python -m tkinter
```
Should open a small test window with "This is Tcl/Tk version X.X"

### 3. Run the Application
```bash
./run.sh
```
Should start the setup wizard without errors.

---

## Alternative: Fix Python 3.13 (Not Recommended)

If you absolutely must use Python 3.13, you can try:

1. **Repair Python 3.13**:
   - Settings → Apps → Apps & Features
   - Find "Python 3.13"
   - Click "Modify"
   - Ensure "tcl/tk and IDLE" is checked
   - Complete modification

2. **Test Tkinter**:
   ```bash
   python -m tkinter
   ```

3. **Recreate venv** (if tkinter works):
   ```bash
   rm -rf venv
   ./venv_setup.sh
   ```

**Warning**: Even with proper configuration, Python 3.13 may have intermittent Tkinter issues. **Python 3.12.7 is strongly recommended**.

---

## Why Python 3.13 Has Issues

Python 3.13 is the latest release but has known compatibility issues:
- Tkinter/Tcl libraries may not be properly bundled on Windows
- Path configuration issues with tcl8.6 libraries
- The issue affects many GUI applications, not just ours

The development team tested with **Python 3.9 - 3.12** and all work reliably.

---

## Support

If you continue to have issues:

1. **Verify Python 3.12 installation**:
   ```bash
   python --version
   python -m tkinter
   ```

2. **Check the guides**:
   - [PYTHON_VERSION_GUIDE.md](PYTHON_VERSION_GUIDE.md)
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

3. **Check which Python the script is using**:
   ```bash
   ./venv_setup.sh
   ```
   The script will show which Python version it found and is using.

---

## Summary

✅ **Install Python 3.12.7**
✅ **Remove old venv**: `rm -rf venv`
✅ **Run setup**: `./venv_setup.sh`
✅ **Test**: `python -m tkinter`
✅ **Run app**: `./run.sh`

**That's it!** The issue should be completely resolved. 🚀

---

*Last updated: 2025-12-22*
*Issue: Python 3.13 Tkinter compatibility on Windows*
*Solution: Use Python 3.12.7 instead*
