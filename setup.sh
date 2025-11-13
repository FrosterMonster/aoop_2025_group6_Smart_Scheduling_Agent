#!/bin/bash

# Complete setup script for AI Schedule Agent
# This script sets up everything you need to run the application

set -e  # Exit on error

echo "========================================"
echo "  AI Schedule Agent - Complete Setup"
echo "========================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "ℹ $1"
}

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
if ! command -v python &> /dev/null; then
    print_error "Python not found! Please install Python 3.9-3.12"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

print_info "Found Python $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MINOR" -lt 9 ]; then
    print_error "Python 3.9 or higher is required. You have Python $PYTHON_VERSION"
    exit 1
elif [ "$PYTHON_MINOR" -gt 12 ]; then
    print_warning "Python 3.12 or lower is recommended. You have Python $PYTHON_VERSION"
    print_warning "The application might work, but hasn't been tested with this version"
else
    print_success "Python version is compatible"
fi

echo ""

# Step 2: Remove old venv if exists
echo "Step 2: Setting up virtual environment..."
if [ -d "venv" ]; then
    print_warning "Existing venv found. Removing..."
    rm -rf venv
    print_success "Old venv removed"
fi

# Create new venv
print_info "Creating new virtual environment..."
python -m venv venv

if [ ! -d "venv" ]; then
    print_error "Failed to create virtual environment"
    exit 1
fi

print_success "Virtual environment created"
echo ""

# Step 3: Determine the correct Python path
if [ -f "venv/Scripts/python.exe" ]; then
    VENV_PYTHON="./venv/Scripts/python.exe"
elif [ -f "venv/bin/python" ]; then
    VENV_PYTHON="./venv/bin/python"
else
    print_error "Cannot find Python in venv"
    exit 1
fi

# Step 4: Upgrade pip
echo "Step 3: Upgrading pip..."
$VENV_PYTHON -m pip install --upgrade pip --quiet
print_success "Pip upgraded"
echo ""

# Step 5: Install dependencies
echo "Step 4: Installing Python packages..."
print_info "This may take a few minutes..."
$VENV_PYTHON -m pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    print_success "All packages installed successfully"
else
    print_error "Package installation failed"
    exit 1
fi
echo ""

# Step 6: Download spacy model
echo "Step 5: Downloading NLP language model..."
$VENV_PYTHON -m spacy download en_core_web_sm --quiet

if [ $? -eq 0 ]; then
    print_success "Language model downloaded"
else
    print_error "Failed to download language model"
    print_info "You can try manually: $VENV_PYTHON -m spacy download en_core_web_sm"
fi
echo ""

# Step 7: Setup configuration
echo "Step 6: Setting up configuration files..."
bash setup_config.sh

echo ""

# Step 8: Final instructions
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
print_success "Python environment is ready"
print_success "Configuration files created"
echo ""
print_warning "IMPORTANT: You still need to add Google Calendar credentials!"
echo ""
echo "Next steps:"
echo "  1. Get Google OAuth credentials from:"
echo "     https://console.cloud.google.com/"
echo ""
echo "  2. Copy credentials to:"
echo "     .config/credentials.json"
echo ""
echo "  3. Run the application:"
echo "     ./run.sh"
echo ""
echo "For detailed instructions, see:"
echo "  - NEW_USER_SETUP.md (step-by-step guide)"
echo "  - WHAT_TO_MODIFY.md (what files to edit)"
echo ""
print_success "Ready to go! Happy scheduling! 🚀"
