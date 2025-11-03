# AI Schedule Agent

Intelligent Personal Scheduling Assistant that integrates with Google Calendar and learns from user patterns.

## Quick Start

### 1. One-Command Setup

```bash
./setup.sh
```

This will:
- ✓ Create your own virtual environment
- ✓ Install all dependencies
- ✓ Download NLP model
- ✓ Create configuration files

### 2. Add Google Credentials

Get OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/):
1. Create project → Enable Google Calendar API
2. Create OAuth 2.0 Client ID (Desktop app)
3. Download JSON file

```bash
cp ~/Downloads/client_secret_*.json .config/credentials.json
```

### 3. Run the Application

```bash
./run.sh
```

**That's it!** 🚀

---

## System Requirements

- **Python:** 3.9, 3.10, 3.11, or 3.12 (3.11 recommended)
- **OS:** Windows, Linux, or macOS
- **Google Account:** For Calendar integration

---

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Fast setup guide
- **[NEW_USER_SETUP.md](NEW_USER_SETUP.md)** - Detailed setup instructions
- **[WHAT_TO_MODIFY.md](WHAT_TO_MODIFY.md)** - What files to edit
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[.config/README.md](.config/README.md)** - Configuration details

---

## Important Notes

### ⚠️ Do NOT Commit `venv/`

**Each user must create their own virtual environment!**

The `venv/` directory is git-ignored. Never commit it. Always run:
```bash
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
./run.sh
```

Your setup won't conflict with other team members because:
- Each user creates their own `venv/`
- Each user has their own `.config/` files
- Everything personal is git-ignored

---

## Features

- **Smart Scheduling:** AI-powered event scheduling
- **Google Calendar Integration:** Seamless sync with your calendar
- **Natural Language Processing:** Schedule events with natural language
- **Pattern Learning:** Learns from your scheduling habits
- **Conflict Detection:** Automatically detects scheduling conflicts
- **Priority Management:** Handles urgent vs. flexible events
- **Desktop Notifications:** Reminders for upcoming events
- **Email Notifications:** Optional email reminders

---

## Troubleshooting

### NumPy Import Error

If you see `ModuleNotFoundError: No module named 'numpy._core'`:

```bash
rm -rf venv
./setup.sh
```

See [FIX_NUMPY_ERROR.md](FIX_NUMPY_ERROR.md) for details.

### Python Version Issues

The app requires Python 3.9-3.12. Check your version:

```bash
python --version
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more solutions.

---

## Getting Help

1. **Check documentation:**
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
   - [NEW_USER_SETUP.md](NEW_USER_SETUP.md) - Setup help

2. **Verify your setup:**
   ```bash
   python --version  # Should be 3.9-3.12
   ./venv/Scripts/python.exe --version  # Should match
   ```

3. **Clean reinstall:**
   ```bash
   rm -rf venv
   ./setup.sh
   ```

---

## Contributing

When contributing:
1. **Never commit `venv/`** - Each user creates their own
2. **Never commit personal config** - Only commit `.example`/`.template` files
3. **Test with different Python versions** - Support 3.9-3.12
4. **Update documentation** - Keep guides current

---

## License

[Add your license here]

---

## Credits

Developed by [Your Team Name] - NYCU AOOP 2025 Group 6

---

**Ready to schedule smarter?** Run `./setup.sh` to begin! 🚀
