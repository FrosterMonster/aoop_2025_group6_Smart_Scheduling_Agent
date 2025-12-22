#!/bin/bash

# Quick Python version checker
# Helps diagnose Python-related issues

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

echo ""
echo -e "${BOLD}${CYAN}Python Environment Diagnostics${NC}"
echo -e "${CYAN}================================${NC}"
echo ""

# Function to check a Python command
check_python_cmd() {
    local cmd=$1
    if command -v $cmd &> /dev/null; then
        local version=$($cmd --version 2>&1 | awk '{print $2}')
        local path=$(which $cmd)
        local major=$(echo $version | cut -d. -f1)
        local minor=$(echo $version | cut -d. -f2)

        # Check Tkinter
        local tkinter_status="N/A"
        if $cmd -c "import tkinter" 2>/dev/null; then
            local tk_ver=$($cmd -c "import tkinter; print(tkinter.TkVersion)" 2>/dev/null)
            tkinter_status="${GREEN}✓${NC} (v$tk_ver)"
        else
            tkinter_status="${RED}✗${NC} Not available"
        fi

        # Color code version based on compatibility
        local version_color=$GREEN
        if [ "$minor" -eq 13 ]; then
            version_color=$RED
        elif [ "$minor" -ge 9 ] && [ "$minor" -le 12 ]; then
            version_color=$GREEN
        else
            version_color=$YELLOW
        fi

        echo -e "  ${BOLD}$cmd${NC}"
        echo -e "    Path:    $path"
        echo -e "    Version: ${version_color}$version${NC}"
        echo -e "    Tkinter: $tkinter_status"

        # Warnings
        if [ "$minor" -eq 13 ]; then
            echo -e "    ${RED}⚠ WARNING: Python 3.13 has Tkinter issues on Windows!${NC}"
        elif [ "$minor" -ge 9 ] && [ "$minor" -le 12 ]; then
            echo -e "    ${GREEN}✓ Compatible version${NC}"
        fi

        echo ""
        return 0
    fi
    return 1
}

# Check system Python installations
echo -e "${BOLD}System Python Installations:${NC}"
echo ""

FOUND_ANY=false
for cmd in python python3 python3.12 python3.11 python3.10 python3.9 python3.13 py; do
    if check_python_cmd $cmd; then
        FOUND_ANY=true
    fi
done

if [ "$FOUND_ANY" = false ]; then
    echo -e "  ${RED}✗ No Python installations found${NC}"
    echo ""
fi

# Check virtual environment
echo -e "${BOLD}Virtual Environment:${NC}"
echo ""

if [ -d "venv" ]; then
    if [ -f "venv/Scripts/python.exe" ]; then
        VENV_PYTHON="./venv/Scripts/python.exe"
    elif [ -f "venv/bin/python" ]; then
        VENV_PYTHON="./venv/bin/python"
    else
        echo -e "  ${RED}✗ venv exists but Python not found${NC}"
        VENV_PYTHON=""
    fi

    if [ -n "$VENV_PYTHON" ]; then
        VENV_VERSION=$($VENV_PYTHON --version 2>&1 | awk '{print $2}')
        VENV_MAJOR=$(echo $VENV_VERSION | cut -d. -f1)
        VENV_MINOR=$(echo $VENV_VERSION | cut -d. -f2)

        # Check Tkinter in venv
        VENV_TKINTER="N/A"
        if $VENV_PYTHON -c "import tkinter" 2>/dev/null; then
            VENV_TK_VER=$($VENV_PYTHON -c "import tkinter; print(tkinter.TkVersion)" 2>/dev/null)
            VENV_TKINTER="${GREEN}✓${NC} (v$VENV_TK_VER)"
        else
            VENV_TKINTER="${RED}✗${NC} Not available"
        fi

        echo -e "  ${BOLD}Virtual Environment Python${NC}"
        echo -e "    Version: $VENV_VERSION"
        echo -e "    Tkinter: $VENV_TKINTER"

        if [ "$VENV_MINOR" -eq 13 ]; then
            echo -e "    ${RED}⚠ Using Python 3.13 - this may cause issues!${NC}"
        fi
    fi
else
    echo -e "  ${YELLOW}⚠ No virtual environment found${NC}"
    echo -e "    Run: ./venv_setup.sh"
fi

echo ""
echo -e "${CYAN}================================${NC}"
echo ""

# Recommendations
echo -e "${BOLD}Recommendations:${NC}"
echo ""

# Check for Python 3.13
USING_313=false
if command -v python &> /dev/null; then
    VERSION=$(python --version 2>&1 | awk '{print $2}')
    MINOR=$(echo $VERSION | cut -d. -f2)
    if [ "$MINOR" -eq 13 ]; then
        USING_313=true
    fi
fi

if [ "$USING_313" = true ]; then
    echo -e "  ${RED}⚠ You're using Python 3.13${NC}"
    echo -e "    This has known Tkinter issues on Windows"
    echo ""
    echo -e "  ${GREEN}✓ Solution:${NC}"
    echo -e "    Run the automated fix: ${BOLD}./fix_python313.sh${NC}"
    echo ""
else
    # Check if venv exists and has correct Python
    if [ -d "venv" ] && [ -n "$VENV_PYTHON" ]; then
        if $VENV_PYTHON -c "import tkinter" 2>/dev/null; then
            echo -e "  ${GREEN}✓ Everything looks good!${NC}"
            echo -e "    Run the app: ${BOLD}./run.sh${NC}"
        else
            echo -e "  ${YELLOW}⚠ Tkinter not available in venv${NC}"
            echo -e "    Recreate venv: ${BOLD}./venv_setup.sh${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠ No virtual environment${NC}"
        echo -e "    Create one: ${BOLD}./venv_setup.sh${NC}"
    fi
fi

echo ""
echo -e "${BOLD}Quick Reference:${NC}"
echo ""
echo -e "  Check Python:     ${BOLD}./check_python.sh${NC} (this script)"
echo -e "  Fix Python 3.13:  ${BOLD}./fix_python313.sh${NC}"
echo -e "  Setup venv:       ${BOLD}./venv_setup.sh${NC}"
echo -e "  Run app:          ${BOLD}./run.sh${NC}"
echo ""
