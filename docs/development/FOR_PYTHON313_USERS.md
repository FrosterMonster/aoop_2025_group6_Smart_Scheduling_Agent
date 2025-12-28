# 🚨 For Users Getting the Python 3.13 Tkinter Error

## You Saw This Error:

```
_tkinter.TclError: Can't find a usable init.tcl in the following directories:
    C:/Users/.../Python313/lib/tcl8.6 ...

This probably means that Tcl wasn't installed properly.
```

---

## ⚡ THE FIX (One Command!)

### If you have Git Bash:
```bash
./fix_python313.sh
```

### If you have Windows CMD:
```cmd
fix_python313.bat
```

### Then run:
```bash
./run.sh
```

**That's it!** ✅ Problem solved!

---

## 🤔 What Does the Fix Do?

The automated script:

1. ✅ Checks your Python versions
2. ✅ If Python 3.12 not found → guides you to download it
3. ✅ If Python 3.12 found → uses it automatically
4. ✅ Backs up your old virtual environment (just in case)
5. ✅ Creates a new venv with Python 3.12
6. ✅ Installs all dependencies
7. ✅ Verifies Tkinter works
8. ✅ Shows you a success message!

**Time**: ~2-5 minutes (depending on download speed)

---

## 🎯 Step-by-Step (Visual Guide)

```
┌─────────────────────────────────────────┐
│  1. Open Terminal (Git Bash/CMD)       │
├─────────────────────────────────────────┤
│  2. Go to project directory             │
│     cd path/to/group_6                  │
├─────────────────────────────────────────┤
│  3. Run the fix script                  │
│     ./fix_python313.sh                  │
│     (or fix_python313.bat on CMD)       │
├─────────────────────────────────────────┤
│  4. Follow any prompts                  │
│     - May ask to download Python 3.12   │
│     - May ask for confirmations         │
├─────────────────────────────────────────┤
│  5. Wait for completion                 │
│     Script shows progress with ✓ marks  │
├─────────────────────────────────────────┤
│  6. Run the app                         │
│     ./run.sh                            │
└─────────────────────────────────────────┘
           ↓
    🎉 SUCCESS!
```

---

## 📥 If Python 3.12 Not Installed

The script will detect this and show:

```
[ERROR] Python 3.12 not found on your system

Please install Python 3.12.7:

1. Download from: https://www.python.org/downloads/release/python-3127/
2. During installation:
   - Check "Add Python to PATH"
   - Check "tcl/tk and IDLE" (IMPORTANT!)
3. Run this script again after installation

Open download page in browser? (Y/n):
```

Just press `Y` and it opens the download page for you!

### After Installing Python 3.12:

Run the fix script again:
```bash
./fix_python313.sh
```

It will now find Python 3.12 and complete the setup automatically.

---

## 🔍 Want to Check Your Setup First?

Before running the fix, check your Python:

```bash
./check_python.sh
```

This shows:
- ✅ All Python versions found
- ✅ Which have Tkinter
- ✅ What the script recommends

**Example output:**
```
Python Environment Diagnostics
================================

System Python Installations:

  python
    Version: 3.13.0
    Tkinter: ✗ Not available
    ⚠ WARNING: Python 3.13 has Tkinter issues on Windows!

Recommendations:
  ⚠ You're using Python 3.13
    Solution: ./fix_python313.sh
```

---

## ❓ FAQ

### Q: Will this delete my work?
**A:** No! The script:
- Backs up your old venv to `venv.backup.py313`
- Only touches the `venv` folder (not your code)
- You can delete the backup later: `rm -rf venv.backup.py313`

### Q: What if I want to keep Python 3.13?
**A:** The script creates a virtual environment with Python 3.12, but doesn't uninstall Python 3.13. Both can coexist on your system.

### Q: Do I need to configure anything after the fix?
**A:** The script installs all dependencies. You just need to:
1. Add your API key to `.env` (if not done already)
2. Add Google Calendar credentials to `.config/` (optional)

### Q: What if the fix script doesn't work?
**A:**
1. Check if you have permissions: `chmod +x fix_python313.sh`
2. Check the detailed guide: [FIX_PYTHON_313_TKINTER_ERROR.md](FIX_PYTHON_313_TKINTER_ERROR.md)
3. Try manual fix (see the guide)

### Q: Can I use this on Linux/Mac?
**A:** Yes! The script works on:
- ✅ Windows (Git Bash)
- ✅ Windows (CMD - use .bat version)
- ✅ Linux
- ✅ macOS

---

## 🎓 What You'll Learn

By running the fix script, you'll see:
- How to detect Python versions
- How virtual environments work
- How to install packages
- How to verify Tkinter

The script shows each step with clear messages!

---

## 📚 More Information

- **[QUICK_START.md](QUICK_START.md)** - Quick start guide
- **[FIX_PYTHON_313_TKINTER_ERROR.md](FIX_PYTHON_313_TKINTER_ERROR.md)** - Detailed fix guide
- **[PYTHON_VERSION_GUIDE.md](PYTHON_VERSION_GUIDE.md)** - Version guide
- **[SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md)** - All helper scripts

---

## 🆘 Still Need Help?

1. **Run diagnostics**:
   ```bash
   ./check_python.sh
   ```

2. **Check the guides** (links above)

3. **Ask the team** - Share the output from `check_python.sh`

---

## ✅ Summary

```bash
# One command to fix everything:
./fix_python313.sh

# Then run the app:
./run.sh
```

**It's that simple!** 🚀

---

**Made with ❤️ by NYCU AOOP Group 6**

*This fix was created to make your life easier. Enjoy using the AI Schedule Agent!* 😊
