# How to Remove venv from Git Repository

This guide shows how to remove the `venv/` directory from git history so each user creates their own.

## Why Remove venv?

**Problem:** Different users have different Python versions and operating systems.
- User A has Python 3.12 on Windows
- User B has Python 3.11 on Windows
- User C has Python 3.11 on Linux

**Solution:** Each user creates their own `venv/` with their Python version.

## Steps to Remove venv from Git

### Option 1: Simple Removal (Recommended)

If the venv was recently added and you haven't pushed yet:

```bash
# 1. Remove venv from git tracking
git rm -r --cached venv/

# 2. Verify .gitignore has venv/ listed
cat .gitignore | grep venv

# 3. Commit the removal
git add .gitignore
git commit -m "Remove venv from git tracking - users create their own

Each user must create their own venv with:
  ./setup.sh

This ensures Python package compatibility across different systems."

# 4. Push to remote
git push origin main
```

### Option 2: Complete History Cleanup

If venv was committed long ago and you want to remove it from history:

**⚠️ Warning:** This rewrites git history. Coordinate with team first!

```bash
# 1. Remove venv from all history
git filter-branch --force --index-filter \
  "git rm -r --cached --ignore-unmatch venv/" \
  --prune-empty --tag-name-filter cat -- --all

# 2. Force push (dangerous - warn team first!)
git push origin --force --all
```

### Option 3: Using BFG Repo-Cleaner (Fastest for large repos)

```bash
# 1. Install BFG
# Download from: https://rtyley.github.io/bfg-repo-cleaner/

# 2. Clean the repo
java -jar bfg.jar --delete-folders venv

# 3. Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. Force push
git push --force
```

## After Removal

### For You (Person who removed it):

```bash
# 1. Recreate your venv
./setup.sh

# 2. Continue working
./run.sh
```

### For Team Members:

Tell them to:

```bash
# 1. Pull latest changes
git pull

# 2. Remove their old venv if it exists
rm -rf venv

# 3. Create their own venv
./setup.sh

# 4. Run the app
./run.sh
```

## Verification

After removal, check:

```bash
# venv should NOT be tracked
git ls-files | grep venv
# (should show nothing)

# venv should be in .gitignore
cat .gitignore | grep venv
# (should show: venv/)

# venv can still exist locally
ls -la | grep venv
# (can exist locally, but won't be committed)
```

## Important Notes

1. **Communicate with team** before removing from history
2. **Everyone must recreate venv** after pulling changes
3. **setup.sh handles this automatically** - just run it!
4. **Never commit venv again** - it's in .gitignore now

## Team Communication Template

Send this to your team:

---

**Subject: Action Required - Recreate Virtual Environment**

Hi team,

I've removed the `venv/` directory from git because it was causing compatibility issues between different Python versions.

**What you need to do:**

```bash
# 1. Pull latest changes
git pull

# 2. Recreate your virtual environment
./setup.sh

# 3. Run the app as usual
./run.sh
```

**Why this change:**
- Each user now creates their own venv with their Python version
- Fixes NumPy and other compatibility errors
- Cleaner git history (no more venv commits)

The setup script (`./setup.sh`) handles everything automatically.

Questions? See [NEW_USER_SETUP.md](NEW_USER_SETUP.md)

Thanks!

---

## For Future Reference

**Never commit these directories:**
```
venv/
env/
.venv/
Include/
Lib/
Scripts/
__pycache__/
```

They're all in `.gitignore` now!

**Always create venv with:**
```bash
./setup.sh
```

This ensures everyone has compatible packages for their system.
