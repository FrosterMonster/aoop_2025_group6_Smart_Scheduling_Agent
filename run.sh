<<<<<<< HEAD
./venv/Scripts/python.exe main.py
=======
#!/bin/bash

# Run script for AI Schedule Agent
# This script activates the venv and runs the application

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "ℹ $1"
}

# Check if venv exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found!"
    print_info "Please run ./venv_setup.sh first to set up your environment"
    exit 1
fi

# Determine the correct Python path (check bin first for Git Bash on Windows)
if [ -f "venv/bin/python" ]; then
    VENV_PYTHON="./venv/bin/python"
    print_info "Using Unix/Linux venv: $VENV_PYTHON"
elif [ -f "venv/Scripts/python.exe" ]; then
    VENV_PYTHON="./venv/Scripts/python.exe"
    print_info "Using Windows venv: $VENV_PYTHON"
else
    print_error "Cannot find Python in venv"
    print_info "Please run ./venv_setup.sh to recreate your environment"
    exit 1
fi

# Check if Python works
if ! $VENV_PYTHON --version &> /dev/null; then
    print_error "Python in venv is not working properly"
    print_info "Please run ./venv_setup.sh to recreate your environment"
    exit 1
fi

PYTHON_VERSION=$($VENV_PYTHON --version 2>&1 | awk '{print $2}')
print_success "Found Python $PYTHON_VERSION in virtual environment"

# Check if main module exists
if [ ! -d "ai_schedule_agent" ]; then
    print_error "ai_schedule_agent module not found in current directory"
    exit 1
fi

# Run the application
echo ""
print_info "Starting AI Schedule Agent..."
echo ""
$VENV_PYTHON -m ai_schedule_agent

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    print_success "Application exited successfully"
else
    echo ""
    print_error "Application exited with error code: $EXIT_CODE"
fi

exit $EXIT_CODE
>>>>>>> 2646380e138663d85d680e6d33fad2a7caaede3a
