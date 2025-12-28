# AI Schedule Agent - Setup Checklist

Use this checklist to ensure a smooth installation.

---

## ✅ Pre-Installation Checklist

### Step 1: System Requirements

- [ ] **Python 3.9+ installed**
  ```bash
  python3 --version
  # Should show: Python 3.9.x or higher
  ```

- [ ] **Operating System**: Windows, Linux, or macOS
  ```bash
  uname -a   # Linux/macOS
  ver        # Windows
  ```

### Step 2: Install tkinter (GUI Library)

**⚠️ IMPORTANT**: Install tkinter BEFORE creating virtual environment!

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

#### Linux (Fedora/RHEL)
```bash
sudo dnf install python3-tkinter
```

#### Linux (Arch)
```bash
sudo pacman -S tk
```

#### macOS
```bash
brew install python-tk
# Usually included with Python from Homebrew
```

#### Windows
- tkinter is usually included
- If missing, repair Python installation:
  1. Settings → Apps → Python → Modify
  2. Check "tcl/tk and IDLE"
  3. Install

#### Verify tkinter
```bash
python3 -m tkinter
# Should show a small test window
```

- [ ] **tkinter test window appeared** ✓

**Troubleshooting**: See [TKINTER_INSTALLATION.md](docs/guides/TKINTER_INSTALLATION.md)

---

## ✅ Installation Checklist

### Step 3: Clone Repository

```bash
git clone <repository-url>
cd group_6
```

- [ ] **Repository cloned** ✓

### Step 4: Create Virtual Environment

```bash
python3 -m venv venv
```

- [ ] **Virtual environment created** (`venv/` folder exists) ✓

### Step 5: Activate Virtual Environment

**Linux/macOS**:
```bash
source venv/bin/activate
```

**Windows**:
```bash
venv\Scripts\activate
```

- [ ] **Virtual environment activated** (prompt shows `(venv)`) ✓

### Step 6: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

- [ ] **Dependencies installed** (no errors) ✓

### Step 7: Run Test Scripts

#### Test 1: Tkinter
```bash
python test_tkinter.py
```

Expected output:
```
✓ tkinter module found
✓ tkinter window creation successful
✓✓✓ ALL TESTS PASSED
```

- [ ] **Tkinter test passed** ✓

#### Test 2: Basic imports
```bash
python -c "import ai_schedule_agent; print('✓ Package imports OK')"
```

- [ ] **Package imports successful** ✓

---

## ✅ Configuration Checklist

### Step 8: Create Configuration Directory

```bash
mkdir -p .config
```

- [ ] **`.config/` directory exists** ✓

### Step 9: Configure LLM Provider

**Choose ONE provider**:

#### Option A: Google Gemini (Free tier available)
```bash
echo "GEMINI_API_KEY=your-key-here" >> .env
echo "LLM_PROVIDER=gemini" >> .env
```

Get key from: https://makersuite.google.com/app/apikey

- [ ] **Gemini API key set** ✓

#### Option B: Claude (Anthropic)
```bash
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
echo "LLM_PROVIDER=claude" >> .env
```

Get key from: https://console.anthropic.com/

- [ ] **Claude API key set** ✓

#### Option C: OpenAI
```bash
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
echo "LLM_PROVIDER=openai" >> .env
```

Get key from: https://platform.openai.com/api-keys

- [ ] **OpenAI API key set** ✓

### Step 10: Configure Google Calendar

1. **Get OAuth Credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create project (or use existing)
   - Enable "Google Calendar API"
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials JSON

2. **Save credentials**:
   ```bash
   # Save downloaded file as:
   cp ~/Downloads/client_secret_*.json .config/credentials.json
   ```

- [ ] **`.config/credentials.json` exists** ✓

### Step 11: Verify Configuration

```bash
# Check .env file
cat .env

# Should show:
# GEMINI_API_KEY=...
# LLM_PROVIDER=gemini

# Check credentials
ls -la .config/credentials.json
```

- [ ] **`.env` file configured** ✓
- [ ] **`credentials.json` exists** ✓

---

## ✅ First Run Checklist

### Step 12: Test Calendar Authentication

```bash
python test_calendar_auth.py
```

**Expected**:
1. Browser opens for Google OAuth
2. Sign in to Google account
3. Grant calendar access permissions
4. Browser shows "Authentication successful"
5. Script shows "✓✓✓ ALL TESTS PASSED"

- [ ] **Calendar authentication successful** ✓
- [ ] **`.config/token.pickle` created** ✓

### Step 13: Run Application

```bash
python -m ai_schedule_agent.ui.app
```

**Expected**:
- Application window opens
- No errors in console
- UI loads completely

- [ ] **Application runs without errors** ✓

### Step 14: Test Basic Functionality

1. **Open Settings Tab**
   - [ ] Settings tab loads ✓

2. **Configure Working Hours**
   - [ ] Can edit working hours ✓
   - [ ] Changes auto-save ✓

3. **Test Quick Schedule**
   - [ ] Can enter event description ✓
   - [ ] LLM responds (no API errors) ✓

4. **Check Calendar View**
   - [ ] Calendar displays current month ✓
   - [ ] Can navigate months ✓

- [ ] **All basic features working** ✓

---

## 🚨 Troubleshooting

### Common Issues

| Issue | Solution | Doc Link |
|-------|----------|----------|
| `No module named 'tkinter'` | Install system tkinter | [TKINTER_INSTALLATION.md](docs/guides/TKINTER_INSTALLATION.md) |
| `Invalid grant token expired` | Delete `.config/token.pickle` and re-auth | [CALENDAR_AUTH_FIX.md](docs/guides/CALENDAR_AUTH_FIX.md) |
| `API key not found` | Check `.env` file exists and has key | [LLM_SETUP_GUIDE.md](docs/guides/LLM_SETUP_GUIDE.md) |
| App won't start | Check Python version (3.9+) | - |
| Calendar won't load | Re-run `test_calendar_auth.py` | [CALENDAR_AUTH_FIX.md](docs/guides/CALENDAR_AUTH_FIX.md) |

### Get Help

1. Check relevant documentation in `docs/guides/`
2. Run test scripts to isolate issues:
   - `python test_tkinter.py`
   - `python test_calendar_auth.py`
   - `python test_energy_patterns.py`
3. Check logs in console output
4. Open an issue with error details

---

## ✅ Final Checklist

Before considering setup complete:

- [ ] **All dependencies installed** ✓
- [ ] **Tkinter working** ✓
- [ ] **LLM API key configured** ✓
- [ ] **Google Calendar authenticated** ✓
- [ ] **Application starts without errors** ✓
- [ ] **Can create test event** ✓
- [ ] **Settings auto-save** ✓

**Setup Status**:
- [ ] ❌ Incomplete (issues remaining)
- [ ] ⚠️ Partial (some features not working)
- [ ] ✅ Complete (everything working!)

---

## 🎉 Success!

If all items are checked, you're ready to use AI Schedule Agent!

**Next Steps**:
1. Explore the Settings tab to customize your preferences
2. Try scheduling an event with natural language
3. Check out the Insights tab for analytics
4. Read the [Modern UI Guide](docs/guides/MODERN_UI_GUIDE.md)

**Enjoy your AI scheduling assistant!** 🚀

---

## 📚 Additional Resources

- [Complete Setup Guide](docs/guides/SETUP_INSTRUCTIONS.md)
- [Modern UI Guide](docs/guides/MODERN_UI_GUIDE.md)
- [LLM Configuration](docs/guides/LLM_SETUP_GUIDE.md)
- [Calendar Authentication](docs/guides/CALENDAR_AUTH_FIX.md)
- [Tkinter Installation](docs/guides/TKINTER_INSTALLATION.md)

---

**Last Updated**: November 13, 2025
**Version**: 1.2.1
