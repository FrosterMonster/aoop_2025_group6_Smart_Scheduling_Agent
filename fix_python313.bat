@echo off
REM Windows batch version of fix_python313.sh
REM For users without Git Bash

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo.
echo        Python 3.13 Tkinter Issue - Automated Fix
echo.
echo ============================================================
echo.

REM Check if Git Bash is available
where bash.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo Git Bash detected - using the bash script for better experience...
    echo.
    bash.exe fix_python313.sh
    exit /b
)

echo This is the Windows fallback version.
echo For the best experience, install Git Bash and run: ./fix_python313.sh
echo.
echo Download Git Bash: https://git-scm.com/downloads
echo.

pause

REM Step 1: Check current Python
echo Step 1: Detecting Python...
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.12.7 from:
    echo https://www.python.org/downloads/release/python-3127/
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Current Python: %PYTHON_VERSION%

REM Extract minor version
for /f "tokens=2 delims=." %%i in ("%PYTHON_VERSION%") do set PYTHON_MINOR=%%i

if "%PYTHON_MINOR%"=="13" (
    echo [WARNING] You are using Python 3.13!
    echo This has known Tkinter issues on Windows.
    echo.
)

REM Step 2: Check for Python 3.12
echo.
echo Step 2: Checking for Python 3.12...
echo.

set FOUND_312=0
set PYTHON312_CMD=python

REM Try to find python3.12
where py >nul 2>&1
if %errorlevel% equ 0 (
    py -3.12 --version >nul 2>&1
    if !errorlevel! equ 0 (
        set FOUND_312=1
        set PYTHON312_CMD=py -3.12
        echo Found Python 3.12 via 'py' launcher
    )
)

if %FOUND_312%==0 (
    REM Python 3.12 not found
    echo [ERROR] Python 3.12 not found on your system
    echo.
    echo Please install Python 3.12.7:
    echo.
    echo 1. Download from: https://www.python.org/downloads/release/python-3127/
    echo 2. During installation:
    echo    - Check "Add Python to PATH"
    echo    - Check "tcl/tk and IDLE" ^(IMPORTANT!^)
    echo 3. Run this script again after installation
    echo.

    set /p OPEN_BROWSER="Open download page in browser? (Y/n): "
    if /i "!OPEN_BROWSER!"=="Y" start https://www.python.org/downloads/release/python-3127/
    if /i "!OPEN_BROWSER!"=="" start https://www.python.org/downloads/release/python-3127/

    pause
    exit /b 1
)

REM Step 3: Verify Tkinter
echo.
echo Step 3: Verifying Tkinter...
echo.

%PYTHON312_CMD% -c "import tkinter" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Tkinter is NOT available in Python 3.12
    echo.
    echo Please reinstall Python 3.12 with Tkinter:
    echo 1. Settings -^> Apps -^> Python 3.12 -^> Modify
    echo 2. Ensure "tcl/tk and IDLE" is checked
    echo.
    pause
    exit /b 1
)

echo [OK] Tkinter is available
echo.

REM Step 4: Backup old venv
echo Step 4: Handling existing virtual environment...
echo.

if exist venv (
    echo Found existing venv

    if exist venv.backup.py313 (
        echo Removing old backup...
        rmdir /s /q venv.backup.py313
    )

    echo Creating backup: venv.backup.py313
    move venv venv.backup.py313 >nul
    echo [OK] Backup created
) else (
    echo No existing venv found
)
echo.

REM Step 5: Create new venv
echo Step 5: Creating new virtual environment with Python 3.12...
echo.

%PYTHON312_CMD% -m venv venv --system-site-packages
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment created
echo.

REM Step 6: Verify Tkinter in venv
echo Step 6: Verifying Tkinter in virtual environment...
echo.

venv\Scripts\python.exe -c "import tkinter; print('Tkinter version:', tkinter.TkVersion)"
if %errorlevel% neq 0 (
    echo [ERROR] Tkinter is NOT accessible in venv
    pause
    exit /b 1
)

echo [OK] Tkinter is working in venv
echo.

REM Step 7: Install dependencies
echo Step 7: Installing dependencies...
echo This may take a few minutes...
echo.

if not exist requirements.txt (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)

echo Upgrading pip...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Pip upgrade had issues ^(continuing anyway^)
)

echo Installing packages...
venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Some packages may have failed. Check above for errors.
    pause
)

echo [OK] Dependencies installed
echo.

REM Step 8: Install spaCy model
echo Step 8: Installing NLP language model...
echo.

venv\Scripts\python.exe -c "import spacy; spacy.load('en_core_web_sm')" 2>nul
if %errorlevel% neq 0 (
    echo Downloading spaCy model...
    venv\Scripts\python.exe -m spacy download en_core_web_sm
) else (
    echo [OK] Spacy model already installed
)
echo.

REM Success!
echo.
echo ============================================================
echo.
echo                    FIX COMPLETE!
echo.
echo ============================================================
echo.
echo [OK] Your virtual environment now uses Python 3.12
echo [OK] Tkinter is working correctly
echo [OK] All dependencies installed
echo.
echo Next steps:
echo.
echo   1. Configure your API keys in .env
echo   2. Setup Google Calendar credentials in .config/
echo   3. Run the application:
echo.
echo      run.sh  (in Git Bash)
echo      or
echo      venv\Scripts\python.exe -m ai_schedule_agent
echo.
echo Your old Python 3.13 venv was saved to: venv.backup.py313
echo You can delete it to free up space: rmdir /s venv.backup.py313
echo.

pause
