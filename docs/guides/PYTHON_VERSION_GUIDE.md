# Python Version Guide

## Recommended Python Version

**Python 3.12.7** is the recommended version for this application.

## Known Issues

### Python 3.13 - Tkinter/Tcl Error on Windows

**Issue**: Users running Python 3.13 on Windows may encounter this error:

```
_tkinter.TclError: Can't find a usable init.tcl in the following directories:
    C:/Users/.../Python313/lib/tcl8.6 ...

This probably means that Tcl wasn't installed properly.
```

**Cause**: Python 3.13 has known compatibility issues with Tkinter on Windows. The Tcl/Tk libraries may not be properly configured even when Python is installed correctly.

**Status**: This is a known issue with Python 3.13. This application has been tested and works reliably with Python 3.9 through 3.12.

---

## Solutions

### Solution 1: Install Python 3.12 (RECOMMENDED)

This is the most reliable solution:

1. **Download Python 3.12.7**:
   - Visit: https://www.python.org/downloads/release/python-3127/
   - Windows: Download "Windows installer (64-bit)"
   - During installation, check "Add Python to PATH"
   - **IMPORTANT**: Ensure "tcl/tk and IDLE" is checked

2. **Remove the old virtual environment**:
   ```bash
   rm -rf venv
   ```

3. **Run the setup script** (it will automatically detect Python 3.12):
   ```bash
   ./venv_setup.sh
   ```

4. **Run the application**:
   ```bash
   ./run.sh
   ```

---

### Solution 2: Fix Python 3.13 Installation (Advanced)

If you must use Python 3.13:

1. **Repair Python 3.13 Installation**:
   - Windows Settings → Apps → Apps & Features
   - Find "Python 3.13"
   - Click "Modify"
   - Click "Modify" again in the installer
   - **Ensure "tcl/tk and IDLE" is checked**
   - Complete the modification

2. **Test Tkinter**:
   ```bash
   python -m tkinter
   ```
   This should open a small Tkinter test window. If it works, proceed.

3. **Recreate virtual environment**:
   ```bash
   rm -rf venv
   ./venv_setup.sh
   ```

4. **Run the application**:
   ```bash
   ./run.sh
   ```

**Note**: Even with proper installation, Python 3.13 may have intermittent Tkinter issues on Windows. Python 3.12 is strongly recommended.

---

## Automatic Version Detection

The `venv_setup.sh` script has been updated to:

1. **Prioritize Python 3.12** over other versions
2. **Search for compatible versions** in this order:
   - python3.12
   - python3.11
   - python3.10
   - python3.9
   - python3, python, py (generic commands)

3. **Warn about Python 3.13** and ask for confirmation before proceeding
4. **Provide clear error messages** if Tkinter issues are detected

---

## Checking Your Python Version

To check which Python version you're currently using:

```bash
python --version
```

Or:

```bash
python3 --version
```

To see all Python versions on your system:

```bash
# Windows (Git Bash)
where python python3 python3.12 python3.13

# Linux/Mac
which -a python python3 python3.12 python3.13
```

---

## Testing Tkinter

After installation, always test Tkinter:

```bash
python -m tkinter
```

This should open a small test window. If you see the window, Tkinter is working correctly.

---

## Support

If you continue to experience issues:

1. **Check Python installation**: Ensure Tcl/Tk is installed
2. **Use Python 3.12**: Most reliable version for this application
3. **Check documentation**: See `docs/guides/TKINTER_INSTALLATION.md`
4. **Run diagnostics**: `python test_tkinter.py`

---

## Version Compatibility Matrix

| Python Version | Status | Notes |
|---------------|--------|-------|
| 3.9 - 3.12 | ✅ Fully Supported | Recommended versions |
| 3.12.7 | ⭐ Best Choice | Most tested, most stable |
| 3.13 | ⚠️ Known Issues | Tkinter errors on Windows |
| 3.14+ | ❓ Untested | May work but not tested |
| < 3.9 | ❌ Not Supported | Too old |

---

## Quick Reference

### Install Python 3.12
- Download: https://www.python.org/downloads/release/python-3127/

### Setup Commands
```bash
# Remove old environment
rm -rf venv

# Create new environment (will auto-detect Python 3.12)
./venv_setup.sh

# Run application
./run.sh
```

### Test Tkinter
```bash
python -m tkinter
```
