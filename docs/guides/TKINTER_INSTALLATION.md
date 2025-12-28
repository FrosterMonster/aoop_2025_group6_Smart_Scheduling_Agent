# Fixing "No module named 'tkinter'" Error

## 🐛 Error

```
ModuleNotFoundError: No module named 'tkinter'
```

or

```
ModuleNotFoundError: No module named '_tkinter'
```

This occurs when Python's tkinter GUI library is not installed.

---

## 🔍 Understanding the Issue

**Tkinter** is Python's standard GUI library, used for the application's user interface.

**Why it's missing**:
- Linux: tkinter is often **not** included with Python by default
- Windows: Usually included, but may be missing in minimal installations
- macOS: Usually included with Python 3
- Virtual environments: May not inherit system tkinter

---

## ✅ Solutions by Operating System

### 🐧 Linux (Ubuntu/Debian)

```bash
# For Python 3
sudo apt-get update
sudo apt-get install python3-tk

# Verify installation
python3 -m tkinter
# A small window should appear
```

### 🐧 Linux (Fedora/RHEL/CentOS)

```bash
# For Python 3
sudo dnf install python3-tkinter
# or
sudo yum install python3-tkinter

# Verify installation
python3 -m tkinter
```

### 🐧 Linux (Arch/Manjaro)

```bash
sudo pacman -S tk

# Verify installation
python3 -m tkinter
```

### 🪟 Windows

Tkinter should be included by default. If missing:

**Option 1: Repair Python Installation**
1. Go to "Add or Remove Programs"
2. Find Python 3.x
3. Click "Modify"
4. Ensure "tcl/tk and IDLE" is checked
5. Click "Next" → "Install"

**Option 2: Reinstall Python**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer
3. Ensure "tcl/tk and IDLE" is selected
4. Complete installation

**Verify**:
```powershell
python -m tkinter
# A small window should appear
```

### 🍎 macOS

Tkinter should be included with Python 3. If missing:

**Option 1: Using Homebrew**
```bash
brew install python-tk@3.12  # Replace 3.12 with your Python version

# Verify installation
python3 -m tkinter
```

**Option 2: Reinstall Python**
```bash
brew reinstall python@3.12
```

---

## 🔧 Virtual Environment Setup

### Problem: Virtual env doesn't have tkinter access

**Solution**: Virtual environments inherit tkinter from system Python. Ensure:

1. **System Python has tkinter installed** (see above)

2. **Create venv with system packages access**:
   ```bash
   # Option 1: Create new venv with system packages
   python3 -m venv venv --system-site-packages

   # Option 2: Recreate existing venv
   rm -rf venv  # or: rmdir /s venv (Windows)
   python3 -m venv venv --system-site-packages
   ```

3. **Activate and verify**:
   ```bash
   # Linux/macOS
   source venv/bin/activate

   # Windows
   venv\Scripts\activate

   # Test tkinter
   python -m tkinter
   ```

---

## 🧪 Verification

### Test if tkinter is installed:

**Method 1: Import test**
```bash
python3 -c "import tkinter; print('tkinter OK')"
```

**Expected output**:
```
tkinter OK
```

**Method 2: Visual test**
```bash
python3 -m tkinter
```

A small window with "Click me!" button should appear.

**Method 3: Full test script**

Create `test_tkinter.py`:
```python
#!/usr/bin/env python3
import sys

def test_tkinter():
    """Test tkinter installation"""
    print("Testing tkinter installation...")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")

    try:
        import tkinter
        print("\n✓ tkinter module found")
        print(f"  tkinter version: {tkinter.TkVersion}")
        print(f"  tcl version: {tkinter.TclVersion}")

        # Try creating a window
        try:
            root = tkinter.Tk()
            root.withdraw()  # Don't show window
            print("✓ tkinter window creation successful")
            root.destroy()
        except Exception as e:
            print(f"✗ Window creation failed: {e}")
            return False

        print("\n✓✓✓ ALL TESTS PASSED")
        print("Tkinter is properly installed!")
        return True

    except ImportError as e:
        print(f"\n✗✗✗ TKINTER NOT FOUND")
        print(f"Error: {e}")
        print("\nPlease install tkinter:")

        if sys.platform.startswith('linux'):
            print("  sudo apt-get install python3-tk")
        elif sys.platform == 'darwin':
            print("  brew install python-tk")
        elif sys.platform == 'win32':
            print("  Reinstall Python with 'tcl/tk' option enabled")

        return False

if __name__ == "__main__":
    success = test_tkinter()
    sys.exit(0 if success else 1)
```

Run it:
```bash
python test_tkinter.py
```

---

## 📝 Installation Guide for Different Scenarios

### Scenario 1: Fresh Linux System

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv python3-tk

# 2. Clone repository
git clone <repository-url>
cd group_6

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate
source venv/bin/activate

# 5. Install requirements
pip install -r requirements.txt

# 6. Verify tkinter
python -m tkinter

# 7. Run app
python -m ai_schedule_agent.ui.app
```

### Scenario 2: Windows System

```powershell
# 1. Ensure Python has tkinter (repair if needed)
python -m tkinter

# 2. Clone repository
git clone <repository-url>
cd group_6

# 3. Create virtual environment
python -m venv venv

# 4. Activate
venv\Scripts\activate

# 5. Install requirements
pip install -r requirements.txt

# 6. Run app
python -m ai_schedule_agent.ui.app
```

### Scenario 3: macOS System

```bash
# 1. Install Python via Homebrew (includes tkinter)
brew install python@3.12

# 2. Clone repository
git clone <repository-url>
cd group_6

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate
source venv/bin/activate

# 5. Install requirements
pip install -r requirements.txt

# 6. Verify tkinter
python -m tkinter

# 7. Run app
python -m ai_schedule_agent.ui.app
```

---

## 🚨 Common Issues and Solutions

### Issue 1: "tkinter imports but app crashes"

**Symptom**: Import works, but app shows blank window or crashes

**Cause**: Incompatible Tk version or missing display server

**Solution**:
```bash
# Linux: Check display server
echo $DISPLAY

# If empty, set it:
export DISPLAY=:0

# Or install xvfb for headless:
sudo apt-get install xvfb
xvfb-run python -m ai_schedule_agent.ui.app
```

### Issue 2: "ImportError: libTk.so"

**Symptom**: `ImportError: libTk.so.8.6: cannot open shared object file`

**Cause**: Tk library files not found

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install tk8.6

# Fedora
sudo dnf install tk
```

### Issue 3: Virtual env doesn't see tkinter

**Symptom**: System Python has tkinter, but venv doesn't

**Solution**:
```bash
# Recreate venv with system packages
rm -rf venv
python3 -m venv venv --system-site-packages
source venv/bin/activate
```

### Issue 4: Multiple Python versions

**Symptom**: `python3.12 -m tkinter` works, but `python -m tkinter` fails

**Cause**: Different Python versions installed

**Solution**:
```bash
# Use specific Python version
python3.12 -m venv venv
source venv/bin/activate

# Verify version
python --version
python -m tkinter
```

---

## 📚 Adding to Setup Documentation

I recommend adding this to your project's setup instructions:

### Quick Setup (Add to README.md)

```markdown
## Prerequisites

### Linux
```bash
sudo apt-get install python3 python3-pip python3-venv python3-tk
```

### Windows
- Python 3.9+ with "tcl/tk and IDLE" option enabled
- Download from [python.org](https://www.python.org/downloads/)

### macOS
```bash
brew install python@3.12
```

## Installation

1. Clone repository:
   ```bash
   git clone <repository-url>
   cd group_6
   ```

2. Verify tkinter:
   ```bash
   python3 -m tkinter  # Should show a test window
   ```

3. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run application:
   ```bash
   python -m ai_schedule_agent.ui.app
   ```

## Troubleshooting

If you see "No module named 'tkinter'", see [TKINTER_INSTALLATION.md](docs/guides/TKINTER_INSTALLATION.md)
```

---

## 🎯 Summary

| OS | Installation Command | Notes |
|----|---------------------|-------|
| **Ubuntu/Debian** | `sudo apt-get install python3-tk` | Required before venv |
| **Fedora/RHEL** | `sudo dnf install python3-tkinter` | Required before venv |
| **Arch** | `sudo pacman -S tk` | Required before venv |
| **Windows** | Enable during Python install | Usually included |
| **macOS** | `brew install python-tk` | Usually included |

**Key Points**:
1. Install tkinter at **system level** (not via pip)
2. Install **before** creating virtual environment
3. Verify with: `python3 -m tkinter`
4. Virtual envs inherit system tkinter

---

## 📋 Checklist for New Users

- [ ] Python 3.9+ installed
- [ ] Tkinter installed (system-level)
- [ ] Test: `python3 -m tkinter` shows window
- [ ] Virtual environment created
- [ ] Requirements installed: `pip install -r requirements.txt`
- [ ] Test: `python test_tkinter.py` passes
- [ ] App runs: `python -m ai_schedule_agent.ui.app`

---

**Last Updated**: November 13, 2025
**Issue**: ModuleNotFoundError: No module named 'tkinter'
**Solution**: Install python3-tk at system level
**Status**: ✅ Complete installation guide provided
