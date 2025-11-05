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

print_detail() {
    echo -e "  ${NC}→ $1${NC}"
}

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
print_detail "Searching for Python installation..."

# Find Python command (try python, python3, py)
PYTHON_CMD=""
if command -v python &> /dev/null && python --version &> /dev/null; then
    PYTHON_CMD="python"
    print_detail "Found 'python' command: $(which python)"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    print_detail "Found 'python3' command: $(which python3)"
elif command -v py &> /dev/null; then
    PYTHON_CMD="py"
    print_detail "Found 'py' launcher: $(which py)"
fi

if [ -z "$PYTHON_CMD" ]; then
    print_error "Python not found! Please install Python 3.9-3.12"
    print_info "Download from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
PYTHON_PATCH=$(echo $PYTHON_VERSION | cut -d. -f3)

print_info "Found Python $PYTHON_VERSION (using '$PYTHON_CMD' command)"
print_detail "Python executable: $($PYTHON_CMD -c 'import sys; print(sys.executable)')"
print_detail "Python version: $PYTHON_MAJOR.$PYTHON_MINOR.$PYTHON_PATCH"

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
print_detail "Checking for existing virtual environment..."
if [ -d "venv" ]; then
    VENV_SIZE=$(du -sh venv 2>/dev/null | cut -f1)
    print_warning "Existing venv found (size: $VENV_SIZE)"
    print_detail "Removing old virtual environment..."
    rm -rf venv
    print_success "Old venv removed"
else
    print_detail "No existing venv found"
fi

# Create new venv
print_info "Creating new virtual environment..."
print_detail "Running: $PYTHON_CMD -m venv venv"
$PYTHON_CMD -m venv venv

if [ ! -d "venv" ]; then
    print_error "Failed to create virtual environment"
    exit 1
fi

print_success "Virtual environment created"
VENV_SIZE=$(du -sh venv 2>/dev/null | cut -f1)
print_detail "Virtual environment size: $VENV_SIZE"
echo ""

# Step 3: Determine the correct Python path
print_detail "Locating Python in virtual environment..."
if [ -f "venv/Scripts/python.exe" ]; then
    VENV_PYTHON="./venv/Scripts/python.exe"
    print_detail "Windows venv detected: $VENV_PYTHON"
elif [ -f "venv/bin/python" ]; then
    VENV_PYTHON="./venv/bin/python"
    print_detail "Unix/Linux venv detected: $VENV_PYTHON"
else
    print_error "Cannot find Python in venv"
    exit 1
fi
VENV_PYTHON_VERSION=$($VENV_PYTHON --version 2>&1 | awk '{print $2}')
print_detail "Virtual environment Python version: $VENV_PYTHON_VERSION"

# Step 4: Upgrade pip
echo "Step 3: Upgrading pip..."
print_detail "Getting current pip version..."
OLD_PIP_VERSION=$($VENV_PYTHON -m pip --version 2>&1 | awk '{print $2}')
print_detail "Current pip version: $OLD_PIP_VERSION"
print_detail "Upgrading pip to latest version..."
$VENV_PYTHON -m pip install --upgrade pip --quiet
NEW_PIP_VERSION=$($VENV_PYTHON -m pip --version 2>&1 | awk '{print $2}')
print_success "Pip upgraded: $OLD_PIP_VERSION → $NEW_PIP_VERSION"
echo ""

# Step 5: Install dependencies
echo "Step 4: Installing Python packages..."
print_info "This may take a few minutes..."
print_detail "Reading requirements from: requirements.txt"

# Count packages to install
PACKAGE_COUNT=$(grep -v '^#' requirements.txt | grep -v '^$' | wc -l)
print_detail "Found $PACKAGE_COUNT package requirements"

# Show what packages will be installed
echo ""
print_detail "Key packages to install:"
print_detail "  • Google Calendar API (google-auth, google-api-python-client)"
print_detail "  • LLM Integration (openai, anthropic, python-dotenv)"
print_detail "  • NLP Processing (spacy, dateparser)"
print_detail "  • Timezone Support (pytz)"
print_detail "  • Scientific Computing (numpy, scikit-learn)"
echo ""

print_detail "Installing packages (this will take 2-5 minutes)..."
$VENV_PYTHON -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    print_success "All packages installed successfully"
    INSTALLED_COUNT=$($VENV_PYTHON -m pip list | wc -l)
    print_detail "Total packages in environment: $INSTALLED_COUNT"
else
    print_error "Package installation failed"
    exit 1
fi
echo ""

# Step 6: Download spacy model
echo "Step 5: Downloading NLP language model..."
print_detail "Checking if spacy model 'en_core_web_sm' is already installed..."
if $VENV_PYTHON -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    print_info "Model 'en_core_web_sm' already installed, skipping download"
else
    print_detail "Downloading spaCy model: en_core_web_sm (~15MB)"
    print_detail "This includes: tokenizer, parser, NER, word vectors"
    $VENV_PYTHON -m spacy download en_core_web_sm
fi

if [ $? -eq 0 ]; then
    print_success "Language model downloaded"
    MODEL_INFO=$($VENV_PYTHON -m spacy info en_core_web_sm 2>/dev/null | grep -E "lang|name|version" | head -3)
    print_detail "Model info: $(echo $MODEL_INFO | tr '\n' ' ')"
else
    print_error "Failed to download language model"
    print_info "You can try manually: $VENV_PYTHON -m spacy download en_core_web_sm"
fi
echo ""

# Step 7: Setup configuration
echo "Step 6: Setting up configuration files..."
print_detail "Running setup_config.sh..."
bash setup_config.sh

echo ""

# Step 8: Setup .env file
echo "Step 7: Setting up .env file..."
print_detail "Checking for .env file..."
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        print_detail "Creating .env from .env.template..."
        cp .env.template .env
        print_success ".env file created from template"
        ENV_SIZE=$(wc -l < .env.template)
        print_detail "Copied $ENV_SIZE lines from template"
        print_warning "Please edit .env and add your API keys"
    else
        print_warning ".env.template not found, skipping .env creation"
    fi
else
    ENV_SIZE=$(wc -l < .env)
    print_info ".env file already exists (not overwriting)"
    print_detail ".env file has $ENV_SIZE lines"
fi
echo ""

# Step 9: Final verification and summary
echo ""
print_detail "Verifying installation..."
print_detail "Checking key packages:"

# Verify critical packages
VERIFY_PACKAGES=("google-auth" "google-api-python-client" "openai" "anthropic" "spacy" "python-dotenv" "pytz")
for package in "${VERIFY_PACKAGES[@]}"; do
    if $VENV_PYTHON -c "import ${package//-/_}" 2>/dev/null; then
        VERSION=$($VENV_PYTHON -m pip show $package 2>/dev/null | grep Version | awk '{print $2}')
        print_detail "  ✓ $package ($VERSION)"
    else
        print_detail "  ✗ $package (not found)"
    fi
done

echo ""
FINAL_VENV_SIZE=$(du -sh venv 2>/dev/null | cut -f1)
print_detail "Final virtual environment size: $FINAL_VENV_SIZE"
print_detail "Installation location: $(pwd)/venv"

# Step 10: Final instructions
echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
print_success "Python environment is ready"
print_success "Configuration files created"
print_success ".env file initialized"
echo ""
print_warning "IMPORTANT: You still need to configure API keys and credentials!"
echo ""
echo "Next steps:"
echo ""
echo "  1. Choose your LLM provider and add API key to .env:"
echo "     Edit: .env"
echo ""
echo "     For Claude (Anthropic) - RECOMMENDED:"
echo "       LLM_PROVIDER=claude"
echo "       ANTHROPIC_API_KEY=sk-ant-your-key-here"
echo "       Get key: https://console.anthropic.com/settings/keys"
echo ""
echo "     For OpenAI:"
echo "       LLM_PROVIDER=openai"
echo "       OPENAI_API_KEY=sk-your-key-here"
echo "       Get key: https://platform.openai.com/api-keys"
echo ""
echo "  2. Get Google OAuth credentials:"
echo "     Visit: https://console.cloud.google.com/"
echo "     Save to: .config/credentials.json"
echo ""
echo "  3. Test in DRY_RUN mode (safe, no real calendar changes):"
echo "     In .env, set: DRY_RUN=1"
echo ""
echo "  4. Run the application:"
echo "     ./run.sh"
echo ""
echo "Documentation:"
echo "  - .env.template (configuration options)"
echo "  - .config/README.md (setup instructions)"
echo "  - README.md (project overview)"
echo ""
print_success "Ready to go! Happy scheduling! 🚀"
echo ""
print_info "Tip: Start with DRY_RUN=1 to test without affecting your calendar"
