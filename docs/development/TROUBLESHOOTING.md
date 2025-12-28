# Troubleshooting Guide - Quick Reference

Common issues and instant solutions.

---

## 🐛 "No module named 'tkinter'"

**Cause**: tkinter GUI library not installed

**Quick Fix**:

```bash
# Linux (Ubuntu/Debian)
sudo apt-get install python3-tk

# Linux (Fedora)
sudo dnf install python3-tkinter

# macOS
brew install python-tk

# Windows: Repair Python installation
# Settings → Apps → Python → Modify → Check "tcl/tk"
```

**Verify**:
```bash
python3 -m tkinter  # Should show window
```

📚 **Full Guide**: [TKINTER_INSTALLATION.md](docs/guides/TKINTER_INSTALLATION.md)

---

## 🔐 "Invalid grant token expired"

**Cause**: Google Calendar OAuth token expired

**Quick Fix**:

```bash
# Delete expired token
rm .config/token.pickle

# Re-authenticate (browser will open)
python test_calendar_auth.py
```

**What happens**: Browser opens → Sign in → Grant permissions → Done!

📚 **Full Guide**: [CALENDAR_AUTH_FIX.md](docs/guides/CALENDAR_AUTH_FIX.md)

---

## ⚠️ "Energy patterns not saved"

**Cause**: Fixed in v1.2.1

**Quick Fix**:

```bash
# Pull latest code
git pull origin main

# Test fix
python test_energy_patterns.py
```

**Expected**: `✓✓✓ SUCCESS: Energy patterns persist reliably`

📚 **Full Guide**: [ENERGY_PATTERNS_FIX.md](docs/guides/ENERGY_PATTERNS_FIX.md)

---

## 🔑 "API key not found"

**Cause**: Missing or incorrect `.env` file

**Quick Fix**:

```bash
# Create .env file
touch .env

# Add API key (choose one provider)
echo "GEMINI_API_KEY=your-key-here" >> .env
echo "LLM_PROVIDER=gemini" >> .env

# Verify
cat .env
```

**Get API Keys**:
- Gemini: https://makersuite.google.com/app/apikey
- Claude: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/api-keys

📚 **Full Guide**: [LLM_SETUP_GUIDE.md](docs/guides/LLM_SETUP_GUIDE.md)

---

## 📁 "credentials.json not found"

**Cause**: Google Calendar credentials missing

**Quick Fix**:

1. **Get credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create OAuth 2.0 credentials (Desktop app)
   - Download JSON file

2. **Save to project**:
   ```bash
   cp ~/Downloads/client_secret_*.json .config/credentials.json
   ```

3. **Verify**:
   ```bash
   ls -la .config/credentials.json
   ```

📚 **Full Guide**: [CALENDAR_AUTH_FIX.md](docs/guides/CALENDAR_AUTH_FIX.md)

---

## 💥 App crashes on startup

**Possible causes**:
1. Missing dependencies
2. Wrong Python version
3. Import errors

**Quick Fix**:

```bash
# Check Python version (need 3.9+)
python3 --version

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run with verbose output
python -m ai_schedule_agent.ui.app --verbose
```

**Check each test**:
```bash
python test_tkinter.py           # GUI library
python test_calendar_auth.py     # Calendar access
python test_energy_patterns.py   # Settings persistence
```

---

## 🌐 "Cannot connect to calendar"

**Cause**: Network or authentication issue

**Quick Fix**:

1. **Check internet connection**:
   ```bash
   ping google.com
   ```

2. **Re-authenticate**:
   ```bash
   rm .config/token.pickle
   python test_calendar_auth.py
   ```

3. **Check credentials file**:
   ```bash
   cat .config/credentials.json | jq .
   ```

---

## 🖥️ Virtual environment issues

**Issue**: `venv` doesn't have tkinter

**Quick Fix**:

```bash
# Install tkinter at SYSTEM level first
sudo apt-get install python3-tk  # Linux

# Recreate venv WITH system packages
rm -rf venv
python3 -m venv venv --system-site-packages
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt

# Test
python test_tkinter.py
```

---

## 🎨 UI looks broken / not loading

**Possible causes**:
1. Tkinter version incompatible
2. Missing fonts
3. Display server issues (Linux)

**Quick Fix**:

```bash
# Check tkinter version
python -c "import tkinter; print(tkinter.TkVersion)"
# Should be >= 8.6

# Linux: Check display
echo $DISPLAY
# Should show :0 or similar

# If empty, set it:
export DISPLAY=:0

# Test UI
python -m ai_schedule_agent.ui.app
```

---

## 📊 Settings not persisting

**Cause**: Fixed in v1.1.1+

**Quick Fix**:

```bash
# Ensure on latest version
git pull origin main

# Check if files exist
ls -la .config/user_profile.json

# Test save/load
python -c "
from ai_schedule_agent.ui.modern_main_window import ModernSchedulerUI
from ai_schedule_agent.config.manager import ConfigManager
# App should save settings on close
"
```

📚 **Full Guide**: [SETTINGS_SAVE_FIX.md](docs/guides/SETTINGS_SAVE_FIX.md)

---

## 🔄 Calendar events shake on hover

**Cause**: Fixed in v1.0.0+

**Quick Fix**:

```bash
# Update to latest
git pull origin main

# Should no longer shake
python -m ai_schedule_agent.ui.app
```

📚 **Full Guide**: [HOVER_EFFECTS_WITHOUT_SHAKING.md](docs/guides/HOVER_EFFECTS_WITHOUT_SHAKING.md)

---

## 🐍 Python version issues

**Issue**: Using wrong Python version

**Quick Fix**:

```bash
# Check version
python3 --version  # Need 3.9+

# Use specific version if multiple installed
python3.11 -m venv venv
source venv/bin/activate
python --version  # Should show 3.11 now
```

**Install correct Python**:

```bash
# Ubuntu
sudo apt-get install python3.11

# macOS
brew install python@3.11

# Windows: Download from python.org
```

---

## 📦 "pip: command not found"

**Quick Fix**:

```bash
# Linux
sudo apt-get install python3-pip

# macOS
python3 -m ensurepip --upgrade

# Windows: Reinstall Python with pip enabled
```

---

## 🚀 Quick Diagnostic Commands

Run these to check system status:

```bash
# System info
python3 --version      # Python version
pip --version          # pip version
which python3          # Python location

# Test components
python3 -m tkinter     # GUI (should show window)
python test_tkinter.py # Full tkinter test

# Test imports
python -c "import tkinter; print('tkinter OK')"
python -c "import google.auth; print('google-auth OK')"
python -c "import ai_schedule_agent; print('package OK')"

# Check files
ls -la .env                        # API keys
ls -la .config/credentials.json    # Google credentials
ls -la .config/token.pickle        # Auth token
ls -la .config/user_profile.json   # User settings
```

---

## 📋 Test Suite

Run all tests to diagnose issues:

```bash
# 1. Tkinter
python test_tkinter.py
# Expected: ✓✓✓ ALL TESTS PASSED

# 2. Calendar auth
python test_calendar_auth.py
# Expected: ✓✓✓ ALL TESTS PASSED

# 3. Energy patterns
python test_energy_patterns.py
# Expected: ✓✓✓ SUCCESS

# 4. Basic import
python -c "from ai_schedule_agent.ui.app import main; print('Import OK')"
```

---

## 🆘 Still Having Issues?

### Step 1: Check Logs

```bash
# Run with verbose logging
python -m ai_schedule_agent.ui.app --verbose 2>&1 | tee app.log

# Check error in logs
cat app.log | grep -i error
```

### Step 2: Clean Install

```bash
# Remove everything
rm -rf venv .config/token.pickle

# Start fresh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python test_tkinter.py
python test_calendar_auth.py
```

### Step 3: Get Help

1. Check [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)
2. Read relevant guide in `docs/guides/`
3. Open an issue with:
   - Error message (full traceback)
   - Python version (`python3 --version`)
   - OS (`uname -a` or `ver`)
   - Output of diagnostic commands above

---

## 📚 Documentation Index

| Issue | Guide |
|-------|-------|
| Tkinter not found | [TKINTER_INSTALLATION.md](docs/guides/TKINTER_INSTALLATION.md) |
| Calendar auth errors | [CALENDAR_AUTH_FIX.md](docs/guides/CALENDAR_AUTH_FIX.md) |
| Settings not saving | [SETTINGS_SAVE_FIX.md](docs/guides/SETTINGS_SAVE_FIX.md) |
| Energy patterns issue | [ENERGY_PATTERNS_FIX.md](docs/guides/ENERGY_PATTERNS_FIX.md) |
| LLM API setup | [LLM_SETUP_GUIDE.md](docs/guides/LLM_SETUP_GUIDE.md) |
| Complete setup | [SETUP_INSTRUCTIONS.md](docs/guides/SETUP_INSTRUCTIONS.md) |
| UI guide | [MODERN_UI_GUIDE.md](docs/guides/MODERN_UI_GUIDE.md) |

---

**Last Updated**: November 13, 2025
**Status**: Active troubleshooting guide
