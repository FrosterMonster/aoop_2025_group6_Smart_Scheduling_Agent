# Configuration Directory

This directory stores your personal settings for the AI Schedule Agent.

## Quick Setup (First Time)

Run the setup script from the project root:

```bash
./setup_config.sh
```

This creates your config files from templates.

## Required: Google Calendar Credentials

### Step 1: Get Credentials from Google

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google Calendar API**
4. Create **OAuth 2.0 Client ID** (Desktop app)
5. Download the JSON file

### Step 2: Add to Config

Copy your downloaded file to:
```
.config/credentials.json
```

That's it! The app will guide you through Google login on first run.

## Optional: Customize Settings

Edit `.config/settings.json` to change:

**Window Size:**
```json
"ui": {
  "window_width": 1200,
  "window_height": 800
}
```

**Email Notifications:**
```json
"smtp": {
  "server": "smtp.gmail.com",
  "port": 587,
  "username": "your-email@gmail.com",
  "password": "your-app-password"
}
```
*Note: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.*

**Reminder Times:**
```json
"notifications": {
  "default_reminder_minutes": 15,
  "high_priority_reminder_minutes": 30
}
```

## Files Explained

| File | What It Does | Need to Edit? |
|------|-------------|---------------|
| `credentials.json` | Google API access | **YES** - Required |
| `settings.json` | App preferences | Optional |
| `paths.json` | File locations | Rarely |
| `token.pickle` | Auto-generated | No (auto-created) |
| `user_profile.json` | Your schedule preferences | No (created by setup wizard) |

## Template Files

Files ending in `.example` or `.template` are:
- **Committed to git** - Shared with team
- **Templates only** - Copy and customize them
- **Safe to commit** - No sensitive data

Actual config files (without `.example`/`.template`) are:
- **Ignored by git** - Your personal settings
- **Never committed** - Keep credentials private

## Troubleshooting

**"Configuration file not found"**
- Run `./setup_config.sh` to create config files

**"credentials.json not found"**
- Follow the "Google Calendar Credentials" section above

**"Failed to connect to Google"**
- Check your `credentials.json` is valid
- Make sure you downloaded the correct JSON file (OAuth Client ID, not Service Account)

**Email notifications not working**
- For Gmail: Enable 2FA and create an App Password
- Update `smtp` settings in `settings.json`
- Set `"email_enabled": true` in notifications

## For Team Members

When you clone this repo:

1. Run `./setup_config.sh`
2. Get your own Google Calendar credentials
3. Copy to `.config/credentials.json`
4. Run `./run.sh`

Your teammates' config files won't interfere with yours because they're git-ignored!
