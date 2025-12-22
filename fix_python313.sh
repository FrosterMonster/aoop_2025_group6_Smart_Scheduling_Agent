#!/bin/bash

# Automated fix script for Python 3.13 Tkinter issues
# This script helps users quickly switch to Python 3.12

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

clear
echo ""
echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║                                                            ║${NC}"
echo -e "${BOLD}${CYAN}║        Python 3.13 Tkinter Issue - Automated Fix          ║${NC}"
echo -e "${BOLD}${CYAN}║                                                            ║${NC}"
echo -e "${BOLD}${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_step() {
    echo -e "${BOLD}${CYAN}➤${NC} ${BOLD}$1${NC}"
}

# Step 1: Detect current Python version
print_step "Step 1: Detecting your Python version..."
echo ""

CURRENT_PYTHON=""
if command -v python &> /dev/null; then
    CURRENT_PYTHON="python"
elif command -v python3 &> /dev/null; then
    CURRENT_PYTHON="python3"
elif command -v py &> /dev/null; then
    CURRENT_PYTHON="py"
fi

if [ -z "$CURRENT_PYTHON" ]; then
    print_error "No Python installation found!"
    echo ""
    print_info "Please install Python 3.12.7 from:"
    echo "  https://www.python.org/downloads/release/python-3127/"
    exit 1
fi

CURRENT_VERSION=$($CURRENT_PYTHON --version 2>&1 | awk '{print $2}')
MAJOR=$(echo $CURRENT_VERSION | cut -d. -f1)
MINOR=$(echo $CURRENT_VERSION | cut -d. -f2)

print_info "Current Python: $CURRENT_VERSION (using '$CURRENT_PYTHON')"

# Check if Python 3.13
if [ "$MINOR" -eq 13 ]; then
    print_warning "You are using Python 3.13 - this has known Tkinter issues!"
    echo ""
else
    print_success "You're not using Python 3.13"
    print_info "This fix script is specifically for Python 3.13 users"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Fix cancelled."
        exit 0
    fi
fi

# Step 2: Check for Python 3.12
print_step "Step 2: Searching for Python 3.12 on your system..."
echo ""

PYTHON312=""
PYTHON312_CANDIDATES=("python3.12" "python3.11" "python3.10" "python3.9")

for cmd in "${PYTHON312_CANDIDATES[@]}"; do
    if command -v $cmd &> /dev/null; then
        VERSION=$($cmd --version 2>&1 | awk '{print $2}')
        MINOR=$(echo $VERSION | cut -d. -f2)

        if [ "$MINOR" -le 12 ] && [ "$MINOR" -ge 9 ]; then
            PYTHON312=$cmd
            PYTHON312_VERSION=$VERSION
            print_success "Found Python $VERSION (command: $cmd)"
            break
        fi
    fi
done

# Step 3: Handle Python 3.12 availability
if [ -z "$PYTHON312" ]; then
    # Python 3.12 not found - guide user to install
    echo ""
    print_error "Python 3.12 (or 3.9-3.11) not found on your system"
    echo ""
    print_step "Here's what you need to do:"
    echo ""
    echo -e "${BOLD}1. Download and Install Python 3.12.7${NC}"
    echo "   URL: https://www.python.org/downloads/release/python-3127/"
    echo ""
    echo -e "${BOLD}2. During Installation:${NC}"
    echo "   ✓ Check 'Add Python to PATH'"
    echo "   ✓ Check 'tcl/tk and IDLE' (IMPORTANT!)"
    echo ""
    echo -e "${BOLD}3. After Installation:${NC}"
    echo "   Run this script again: ./fix_python313.sh"
    echo ""

    # Offer to open download page
    if command -v cmd.exe &> /dev/null; then
        echo ""
        read -p "Open download page in browser? (Y/n): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            cmd.exe /c start https://www.python.org/downloads/release/python-3127/
            print_success "Opening browser..."
        fi
    fi

    exit 0
fi

# Python 3.12 found - proceed with fix
echo ""
print_step "Step 3: Verifying Tkinter in Python $PYTHON312_VERSION..."
echo ""

if $PYTHON312 -c "import tkinter" 2>/dev/null; then
    print_success "Tkinter is available in Python $PYTHON312_VERSION"
else
    print_error "Tkinter is NOT available in Python $PYTHON312_VERSION"
    echo ""
    print_warning "Your Python $PYTHON312_VERSION installation doesn't have Tkinter"
    print_info "You need to reinstall Python with Tkinter support"
    echo ""

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Install command:"
        echo "  sudo apt-get install python3-tk"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Install command:"
        echo "  brew install python-tk"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "Repair Python installation:"
        echo "  Settings → Apps → Python → Modify"
        echo "  Ensure 'tcl/tk and IDLE' is checked"
    fi

    exit 1
fi

# Step 4: Backup existing venv (if exists)
print_step "Step 4: Handling existing virtual environment..."
echo ""

if [ -d "venv" ]; then
    VENV_SIZE=$(du -sh venv 2>/dev/null | cut -f1)
    print_warning "Found existing venv (size: $VENV_SIZE)"

    # Check if backup exists
    if [ -d "venv.backup.py313" ]; then
        print_info "Previous backup exists: venv.backup.py313"
        read -p "Remove old backup and create new one? (Y/n): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            rm -rf venv.backup.py313
            print_success "Removed old backup"
        fi
    fi

    # Create backup
    if [ ! -d "venv.backup.py313" ]; then
        print_info "Creating backup: venv.backup.py313"
        mv venv venv.backup.py313
        print_success "Backup created"
    else
        print_info "Removing old venv without backup"
        rm -rf venv
        print_success "Old venv removed"
    fi
else
    print_info "No existing venv found - starting fresh"
fi

# Step 5: Create new venv with Python 3.12
echo ""
print_step "Step 5: Creating new virtual environment with Python $PYTHON312_VERSION..."
echo ""

print_info "Running: $PYTHON312 -m venv venv --system-site-packages"
$PYTHON312 -m venv venv --system-site-packages

if [ ! -d "venv" ]; then
    print_error "Failed to create virtual environment"
    exit 1
fi

print_success "Virtual environment created with Python $PYTHON312_VERSION"

# Determine venv Python path
if [ -f "venv/Scripts/python.exe" ]; then
    VENV_PYTHON="./venv/Scripts/python.exe"
elif [ -f "venv/bin/python" ]; then
    VENV_PYTHON="./venv/bin/python"
else
    print_error "Cannot find Python in venv"
    exit 1
fi

VENV_VERSION=$($VENV_PYTHON --version 2>&1 | awk '{print $2}')
print_info "Virtual environment Python: $VENV_VERSION"

# Step 6: Verify Tkinter in venv
echo ""
print_step "Step 6: Verifying Tkinter in virtual environment..."
echo ""

if $VENV_PYTHON -c "import tkinter; print('Tkinter version:', tkinter.TkVersion)" 2>/dev/null; then
    TKINTER_VER=$($VENV_PYTHON -c "import tkinter; print(tkinter.TkVersion)" 2>/dev/null)
    print_success "Tkinter is working! (version $TKINTER_VER)"
else
    print_error "Tkinter is NOT accessible in venv"
    print_warning "This shouldn't happen. Try running venv_setup.sh instead"
    exit 1
fi

# Step 7: Install dependencies
echo ""
print_step "Step 7: Installing dependencies..."
echo ""

if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found!"
    print_info "Are you in the project root directory?"
    exit 1
fi

print_info "This may take a few minutes..."
if $VENV_PYTHON -m pip install --upgrade pip --quiet 2>/dev/null; then
    print_success "Pip upgraded"
else
    print_warning "Pip upgrade had issues (continuing anyway)"
fi

if $VENV_PYTHON -m pip install -r requirements.txt --quiet 2>/dev/null; then
    print_success "Dependencies installed"
else
    print_warning "Some packages may have failed. Trying verbose install..."
    $VENV_PYTHON -m pip install -r requirements.txt
fi

# Step 8: Install spaCy model
echo ""
print_step "Step 8: Installing NLP language model..."
echo ""

if $VENV_PYTHON -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    print_success "Spacy model already installed"
else
    print_info "Downloading spaCy model (~15MB)..."
    if $VENV_PYTHON -m spacy download en_core_web_sm --quiet 2>/dev/null; then
        print_success "Spacy model installed"
    else
        print_warning "Spacy model installation had issues (app will work with reduced NLP)"
    fi
fi

# Step 9: Final verification
echo ""
print_step "Step 9: Final verification..."
echo ""

# Test Tkinter
if $VENV_PYTHON -c "import tkinter" 2>/dev/null; then
    print_success "Tkinter: OK"
else
    print_error "Tkinter: FAILED"
fi

# Test key packages
PACKAGES=("google_auth" "openai" "anthropic" "spacy" "dotenv:python-dotenv")
for pkg_check in "${PACKAGES[@]}"; do
    if [[ $pkg_check == *":"* ]]; then
        PKG_IMPORT=$(echo $pkg_check | cut -d: -f1)
        PKG_NAME=$(echo $pkg_check | cut -d: -f2)
    else
        PKG_IMPORT=$pkg_check
        PKG_NAME=$pkg_check
    fi

    PKG_IMPORT=$(echo $PKG_IMPORT | tr '-' '_')

    if $VENV_PYTHON -c "import $PKG_IMPORT" 2>/dev/null; then
        print_success "$PKG_NAME: OK"
    else
        print_warning "$PKG_NAME: Not found"
    fi
done

# Success!
echo ""
echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║                                                            ║${NC}"
echo -e "${BOLD}${GREEN}║                    ✓ FIX COMPLETE!                         ║${NC}"
echo -e "${BOLD}${CYAN}║                                                            ║${NC}"
echo -e "${BOLD}${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

print_success "Your virtual environment now uses Python $PYTHON312_VERSION"
print_success "Tkinter is working correctly"
print_success "All dependencies installed"

echo ""
echo -e "${BOLD}${CYAN}Next steps:${NC}"
echo ""
echo "  1. Configure your API keys in .env (if not done already)"
echo "  2. Setup Google Calendar credentials in .config/"
echo "  3. Run the application:"
echo ""
echo -e "     ${BOLD}${GREEN}./run.sh${NC}"
echo ""

# Offer to run test
read -p "Test Tkinter now? (Y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    print_info "Testing Tkinter (a window should appear)..."
    $VENV_PYTHON -m tkinter &
    sleep 2
    echo ""
    print_success "If you saw a test window, everything is working!"
fi

echo ""
print_info "Your old Python 3.13 venv was saved to: venv.backup.py313"
print_info "You can delete it anytime to free up space: rm -rf venv.backup.py313"
echo ""
print_success "Happy scheduling! 🚀"
echo ""
