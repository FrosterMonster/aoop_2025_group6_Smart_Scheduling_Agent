# Setup Instructions for New Users

## TL;DR - Just Run This

```bash
./setup.sh
```

Then add your Google credentials to `.config/credentials.json` and run:

```bash
./run.sh
```

Done! 🎉

---

## What `setup.sh` Does

The setup script automatically:

1. ✓ Checks your Python version (requires 3.9-3.12)
2. ✓ Removes old venv if it exists
3. ✓ Creates NEW venv with YOUR Python
4. ✓ Upgrades pip
5. ✓ Installs all packages from requirements.txt
6. ✓ Downloads NLP language model
7. ✓ Creates configuration files from templates

**Everything is automated!** No manual steps needed (except Google credentials).

---

## Prerequisites

### 1. Python Version

Check your Python:
```bash
python --version
```

**Supported:** Python 3.9, 3.10, 3.11, or 3.12

**Recommended:** Python 3.11

If you don't have Python, install from: https://python.org

### 2. Git (for cloning the repo)

```bash
git --version
```

### 3. Google Account

You'll need this for Calendar integration (setup later).

---

## Step-by-Step Guide

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd group_6
```

### Step 2: Run Setup Script

```bash
./setup.sh
```

**What happens:**
- Creates `venv/` directory with your Python
- Installs all packages
- Creates `.config/` files from templates
- Downloads NLP model

**Takes:** 2-5 minutes depending on internet speed

**Output:** You'll see green checkmarks ✓ for each step

### Step 3: Get Google Calendar Credentials

#### 3.1. Go to Google Cloud Console

Visit: https://console.cloud.google.com/

#### 3.2. Create Project

1. Click "Select a project" → "New Project"
2. Project name: "AI Schedule Agent" (or anything)
3. Click "Create"

#### 3.3. Enable Google Calendar API

1. In the search bar, type "Google Calendar API"
2. Click on it
3. Click "Enable"

#### 3.4. Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Configure Consent Screen"
   - User Type: **External**
   - App name: "AI Schedule Agent"
   - User support email: your email
   - Developer contact: your email
   - Click "Save and Continue" (skip optional fields)
3. Go back to "Credentials"
4. Click "Create Credentials" → "OAuth client ID"
5. Application type: **Desktop app**
6. Name: "Desktop Client 1"
7. Click "Create"
8. Click "Download JSON" button

#### 3.5. Add Credentials to Config

```bash
# Copy the downloaded file
cp ~/Downloads/client_secret_*.json .config/credentials.json

# On Windows you might need to drag-drop the file to .config/
```

### Step 4: Run the Application

```bash
./run.sh
```

**First run:**
1. Browser opens automatically
2. Sign in to your Google account
3. Click "Allow" to grant calendar access
4. Browser shows "Authentication successful"
5. Setup wizard appears in the app
6. Configure your preferences
7. Start using the app!

---

## Troubleshooting

### "Python not found"

Install Python 3.9-3.12 from https://python.org

### "setup.sh: command not found"

Make it executable:
```bash
chmod +x setup.sh
./setup.sh
```

### "Permission denied"

On Windows with Git Bash, try:
```bash
bash setup.sh
```

### NumPy Import Error

The setup.sh script handles this automatically! Just run:
```bash
rm -rf venv
./setup.sh
```

### "credentials.json not found"

You forgot Step 3! Get credentials from Google Cloud Console and copy to `.config/credentials.json`

---

## For Different Operating Systems

### Windows (Git Bash)

```bash
./setup.sh
./run.sh
```

### Windows (CMD)

```bash
bash setup.sh
bash run.sh
```

### Linux / Mac

```bash
chmod +x setup.sh run.sh
./setup.sh
./run.sh
```

---

## What Gets Created

After running `./setup.sh`:

```
your-project/
├── venv/                   ← Your virtual environment (created)
│   ├── Scripts/            ← Windows
│   └── bin/                ← Linux/Mac
│
├── .config/                ← Your configuration (created)
│   ├── paths.json          ← Auto-created from template
│   ├── settings.json       ← Auto-created from template
│   ├── credentials.json    ← YOU add this (from Google)
│   └── ...
│
└── ... (other project files)
```

---

## Important Notes

### ⚠️ Never Commit venv/

The `venv/` directory is personal to you. It's in `.gitignore` and should never be committed to git.

**Each team member creates their own venv!**

### ⚠️ Never Commit Credentials

Your `.config/credentials.json` contains sensitive Google API keys. It's in `.gitignore` and should never be committed.

**Each team member gets their own credentials!**

### ⚠️ Always Use ./run.sh

Don't run `python tmp.py` directly. Always use:
```bash
./run.sh
```

This ensures the correct Python from `venv/` is used.

---

## For Team Members

If someone else already set up the project and you're cloning it:

```bash
# 1. Clone
git clone <repo-url>
cd group_6

# 2. Setup (creates YOUR venv)
./setup.sh

# 3. Get YOUR Google credentials
# (from Google Cloud Console)
cp ~/Downloads/your-credentials.json .config/credentials.json

# 4. Run
./run.sh
```

**Each person's setup is independent!** Your venv and config won't conflict with others.

---

## Verifying Setup

After setup, verify everything:

```bash
# Check Python version in venv
./venv/Scripts/python.exe --version
# Should match your system Python

# Check packages installed
./venv/Scripts/python.exe -m pip list | grep numpy
# Should show numpy 1.x for Python 3.11, or 2.x for Python 3.12

# Check config files exist
ls .config/
# Should show: paths.json, settings.json, credentials.json (if added)

# Test import
./venv/Scripts/python.exe -c "import spacy; print('✓ OK')"
# Should print: ✓ OK
```

---

## Getting Help

If setup fails:

1. **Check Python version:** Must be 3.9-3.12
2. **Check internet connection:** Needs to download packages
3. **Try clean setup:**
   ```bash
   rm -rf venv .config
   ./setup.sh
   ```

4. **Check logs:** Setup script shows which step failed

---

## What Files Do I Modify?

**Only ONE file:** `.config/credentials.json`

Everything else is either auto-generated or has good defaults!

See [README.md](README.md) for more details.

---

## Next Steps After Setup

1. **Run the app:** `./run.sh`
2. **Complete setup wizard:** Configure your preferences
3. **Start scheduling:** Use the app!

---

**Questions?** Check [README.md](README.md) for documentation links.

**Problems?** See [REMOVE_VENV_FROM_GIT.md](REMOVE_VENV_FROM_GIT.md) if you had the old venv.

**Happy scheduling!** 🚀
