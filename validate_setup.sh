#!/bin/bash

# Comprehensive setup validation script
# Verifies all components are correctly installed

set -e

echo "========================================"
echo "  Setup Validation for AI Schedule Agent"
echo "========================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Counters
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

print_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS_COUNT++))
}

print_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL_COUNT++))
}

print_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARN_COUNT++))
}

# 1. Check Python
echo "[1/10] Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ] && [ "$PYTHON_MINOR" -le 13 ]; then
        print_pass "Python $PYTHON_VERSION (compatible)"
    else
        print_fail "Python $PYTHON_VERSION (need 3.9-3.13)"
    fi
else
    print_fail "Python 3 not found"
fi
echo ""

# 2. Check tkinter
echo "[2/10] Checking tkinter (GUI library)..."
if python3 -c "import tkinter" 2>/dev/null; then
    TKINTER_VERSION=$(python3 -c "import tkinter; print(tkinter.TkVersion)" 2>/dev/null)
    print_pass "tkinter $TKINTER_VERSION installed"
else
    print_fail "tkinter NOT installed - GUI will not work!"
    echo "      Install: sudo apt-get install python3-tk (Ubuntu/Debian)"
fi
echo ""

# 3. Check virtual environment
echo "[3/10] Checking virtual environment..."
if [ -d "venv" ]; then
    if [ -f "venv/bin/python" ] || [ -f "venv/Scripts/python.exe" ]; then
        print_pass "Virtual environment exists"

        # Find venv python
        if [ -f "venv/bin/python" ]; then
            VENV_PYTHON="./venv/bin/python"
        else
            VENV_PYTHON="./venv/Scripts/python.exe"
        fi

        # Check venv Python version
        VENV_PY_VERSION=$($VENV_PYTHON --version 2>&1 | awk '{print $2}')
        print_pass "venv Python $VENV_PY_VERSION"
    else
        print_fail "Virtual environment is broken"
    fi
else
    print_fail "Virtual environment not found"
    echo "      Run: ./venv_setup.sh"
    VENV_PYTHON="python3"  # Fallback for remaining checks
fi
echo ""

# 4. Check pip
echo "[4/10] Checking pip..."
if $VENV_PYTHON -m pip --version &>/dev/null; then
    PIP_VERSION=$($VENV_PYTHON -m pip --version 2>&1 | awk '{print $2}')
    print_pass "pip $PIP_VERSION installed"
else
    print_fail "pip not found in venv"
fi
echo ""

# 5. Check required packages
echo "[5/10] Checking required Python packages..."
PACKAGES=("google.auth:google-auth" "googleapiclient:google-api-python-client" "openai:openai" "anthropic:anthropic" "spacy:spacy" "dateparser:dateparser" "dotenv:python-dotenv" "pytz:pytz" "numpy:numpy" "sklearn:scikit-learn")

for pkg_pair in "${PACKAGES[@]}"; do
    IFS=: read -r import_name package_name <<< "$pkg_pair"
    if $VENV_PYTHON -c "import $import_name" 2>/dev/null; then
        VERSION=$($VENV_PYTHON -m pip show $package_name 2>/dev/null | grep Version | awk '{print $2}')
        print_pass "$package_name ($VERSION)"
    else
        print_fail "$package_name not installed"
    fi
done
echo ""

# 6. Check spaCy model
echo "[6/10] Checking spaCy NLP model..."
if $VENV_PYTHON -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    print_pass "en_core_web_sm model installed"
else
    print_warn "en_core_web_sm model not found"
    echo "      Install: $VENV_PYTHON -m spacy download en_core_web_sm"
fi
echo ""

# 7. Check configuration files
echo "[7/10] Checking configuration files..."
if [ -d ".config" ]; then
    print_pass ".config directory exists"

    if [ -f ".config/credentials.json" ]; then
        print_pass "credentials.json exists"
    else
        print_warn "credentials.json missing (Google Calendar won't work)"
        echo "      Get from: https://console.cloud.google.com/"
    fi

    if [ -f ".config/token.pickle" ]; then
        print_pass "token.pickle exists (already authenticated)"
    else
        print_warn "token.pickle missing (need to authenticate)"
        echo "      Run: python test_calendar_auth.py"
    fi

    if [ -f ".config/user_profile.json" ]; then
        print_pass "user_profile.json exists"
    else
        print_warn "user_profile.json missing (will be created on first run)"
    fi
else
    print_fail ".config directory not found"
fi
echo ""

# 8. Check .env file
echo "[8/10] Checking .env file..."
if [ -f ".env" ]; then
    print_pass ".env file exists"

    # Check for API key
    if grep -q "LLM_PROVIDER=" .env && grep -q "API_KEY=" .env; then
        PROVIDER=$(grep "LLM_PROVIDER=" .env | cut -d= -f2)
        print_pass "LLM provider configured: $PROVIDER"
    else
        print_warn "API keys not configured in .env"
        echo "      Add: LLM_PROVIDER and API key"
    fi
else
    print_fail ".env file missing"
    echo "      Copy: .env.template to .env and configure"
fi
echo ""

# 9. Check test scripts
echo "[9/10] Checking test scripts..."
for script in "test_tkinter.py" "test_calendar_auth.py" "test_energy_patterns.py"; do
    if [ -f "$script" ]; then
        print_pass "$script exists"
    else
        print_warn "$script missing"
    fi
done
echo ""

# 10. Check main app
echo "[10/10] Checking main application..."
if [ -d "ai_schedule_agent" ]; then
    print_pass "ai_schedule_agent package exists"

    if [ -f "ai_schedule_agent/ui/app.py" ]; then
        print_pass "app.py exists"
    else
        print_fail "app.py missing"
    fi
else
    print_fail "ai_schedule_agent package not found"
fi
echo ""

# Summary
echo "========================================"
echo "  Validation Summary"
echo "========================================"
echo ""
echo -e "${GREEN}Passed:${NC}  $PASS_COUNT"
echo -e "${YELLOW}Warnings:${NC} $WARN_COUNT"
echo -e "${RED}Failed:${NC}  $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ] && [ $WARN_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓✓✓ ALL CHECKS PASSED!${NC}"
    echo "Your setup is complete and ready to use."
    echo ""
    echo "To run the application:"
    echo "  ./run.sh"
elif [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${YELLOW}⚠ SETUP MOSTLY COMPLETE${NC}"
    echo "Some optional components are missing."
    echo "The app will work, but some features may be limited."
    echo ""
    echo "To run the application:"
    echo "  ./run.sh"
else
    echo -e "${RED}✗ SETUP INCOMPLETE${NC}"
    echo "Critical components are missing."
    echo ""
    echo "To fix issues:"
    echo "  1. Review failed checks above"
    echo "  2. Run: ./venv_setup.sh"
    echo "  3. Configure .env file"
    echo "  4. Run this validation again"
fi
echo ""
