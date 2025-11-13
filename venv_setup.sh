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
elif [ "$PYTHON_MINOR" -gt 13 ]; then
    print_warning "Python 3.13 or lower is recommended. You have Python $PYTHON_VERSION"
    print_warning "The application might work, but hasn't been tested with this version"
else
    print_success "Python version is compatible (3.9-3.13 supported)"
fi

echo ""

# Step 2: Check for tkinter (GUI library)
echo "Step 2: Checking tkinter (GUI library)..."
print_detail "Verifying tkinter installation..."

TKINTER_INSTALLED=false
if $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
    TKINTER_VERSION=$($PYTHON_CMD -c "import tkinter; print(tkinter.TkVersion)" 2>/dev/null)
    print_success "tkinter found (version $TKINTER_VERSION)"
    TKINTER_INSTALLED=true
else
    print_error "tkinter NOT found - GUI will not work!"
    echo ""
    print_warning "tkinter is required for the application UI"
    print_info "Install instructions:"
    echo ""

    # Detect OS and show appropriate install command
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            print_detail "Ubuntu/Debian:"
            echo "  sudo apt-get update"
            echo "  sudo apt-get install python3-tk"
        elif command -v dnf &> /dev/null; then
            print_detail "Fedora/RHEL:"
            echo "  sudo dnf install python3-tkinter"
        elif command -v pacman &> /dev/null; then
            print_detail "Arch Linux:"
            echo "  sudo pacman -S tk"
        else
            print_detail "Linux:"
            echo "  Install python3-tk using your package manager"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_detail "macOS:"
        echo "  brew install python-tk"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        print_detail "Windows:"
        echo "  Repair Python installation:"
        echo "  Settings → Apps → Python → Modify"
        echo "  Ensure 'tcl/tk and IDLE' is checked"
    fi

    echo ""
    print_info "After installing tkinter, run this script again"
    echo ""

    # Ask user if they want to continue
    read -p "Continue setup anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Setup cancelled. Please install tkinter and try again."
        print_detail "Test tkinter: python3 -m tkinter"
        print_detail "Full guide: docs/guides/TKINTER_INSTALLATION.md"
        exit 1
    fi
    print_warning "Continuing without tkinter (app will not run)"
fi

echo ""

# Step 3: Check or create virtual environment
echo "Step 3: Setting up virtual environment..."
print_detail "Checking for existing virtual environment..."

VENV_EXISTS=false
VENV_PYTHON=""

if [ -d "venv" ]; then
    VENV_SIZE=$(du -sh venv 2>/dev/null | cut -f1)
    print_info "Existing venv found (size: $VENV_SIZE)"

    # Locate Python in existing venv
    if [ -f "venv/Scripts/python.exe" ]; then
        VENV_PYTHON="./venv/Scripts/python.exe"
    elif [ -f "venv/bin/python" ]; then
        VENV_PYTHON="./venv/bin/python"
    fi

    # Check if venv is valid
    if [ -n "$VENV_PYTHON" ] && $VENV_PYTHON --version &> /dev/null; then
        VENV_EXISTS=true
        VENV_PYTHON_VERSION=$($VENV_PYTHON --version 2>&1 | awk '{print $2}')
        print_success "Valid venv found - Python $VENV_PYTHON_VERSION"
        print_detail "Skipping venv creation (will only update packages)"
    else
        print_warning "Existing venv is broken"
        print_detail "Removing and recreating..."
        rm -rf venv
    fi
fi

# Create new venv only if needed
if [ "$VENV_EXISTS" = false ]; then
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

    # Locate Python in new venv
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
fi

echo ""

# Step 4: Upgrade pip
echo "Step 4: Upgrading pip..."
print_detail "Getting current pip version..."
OLD_PIP_VERSION=$($VENV_PYTHON -m pip --version 2>&1 | awk '{print $2}')
print_detail "Current pip version: $OLD_PIP_VERSION"
print_detail "Upgrading pip to latest version..."

# Upgrade pip with error handling
if $VENV_PYTHON -m pip install --upgrade pip --quiet 2>/dev/null; then
    NEW_PIP_VERSION=$($VENV_PYTHON -m pip --version 2>&1 | awk '{print $2}')
    print_success "Pip upgraded: $OLD_PIP_VERSION → $NEW_PIP_VERSION"
else
    print_warning "Pip upgrade had issues, but continuing..."
    print_detail "This is usually not critical"
fi
echo ""

# Step 5: Install/Update dependencies
echo "Step 5: Checking and installing Python packages..."
print_detail "Reading requirements from: requirements.txt"

# Verify requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found!"
    print_info "Are you in the project root directory?"
    exit 1
fi

# Count packages in requirements
PACKAGE_COUNT=$(grep -v '^#' requirements.txt | grep -v '^$' | wc -l)
print_detail "Found $PACKAGE_COUNT package requirements"

# Check what's already installed
print_detail "Checking installed packages..."
INSTALLED_BEFORE=$($VENV_PYTHON -m pip list --format=freeze 2>/dev/null | wc -l)
print_detail "Currently installed: $INSTALLED_BEFORE packages"

# Check which required packages are missing
echo ""
print_detail "Analyzing required packages..."
MISSING_PACKAGES=()
REQUIRED_PACKAGES=("google-auth" "google-api-python-client" "openai" "anthropic" "spacy" "dateparser" "python-dotenv" "pytz" "numpy" "scikit-learn")

for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if ! $VENV_PYTHON -c "import ${pkg//-/_}" 2>/dev/null; then
        MISSING_PACKAGES+=("$pkg")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
    print_success "All required packages already installed!"
    print_info "Running upgrade check for outdated packages..."
    print_detail "Checking for package updates..."

    # Only check for updates, don't automatically upgrade unless needed
    OUTDATED=$($VENV_PYTHON -m pip list --outdated --format=columns 2>/dev/null | tail -n +3 | wc -l)

    if [ $OUTDATED -gt 0 ]; then
        print_info "$OUTDATED packages have updates available"
        print_detail "To update all: $VENV_PYTHON -m pip install -U -r requirements.txt"
    else
        print_success "All packages are up to date"
    fi
else
    print_info "Missing packages: ${#MISSING_PACKAGES[@]}"
    for pkg in "${MISSING_PACKAGES[@]}"; do
        print_detail "  • $pkg"
    done
    echo ""

    print_detail "Installing missing packages (this may take a few minutes)..."
    print_info "Installing packages for Python $PYTHON_VERSION..."

    # Try quiet install first
    if $VENV_PYTHON -m pip install -r requirements.txt --quiet 2>/dev/null; then
        print_success "Packages installed successfully"
        INSTALLED_AFTER=$($VENV_PYTHON -m pip list --format=freeze 2>/dev/null | wc -l)
        NEW_PACKAGES=$((INSTALLED_AFTER - INSTALLED_BEFORE))
        print_detail "Installed $NEW_PACKAGES new packages"
    else
        print_warning "Quiet install failed, trying with output..."
        print_detail "You will see detailed installation progress..."
        echo ""

        # Try verbose install
        if $VENV_PYTHON -m pip install -r requirements.txt; then
            print_success "Packages installed successfully"
        else
            print_error "Package installation failed!"
            echo ""
            print_info "Common issues and solutions:"
            print_detail "1. Network connection - check internet access"
            print_detail "2. Compiler missing (for source builds)"
            print_detail "   Ubuntu/Debian: sudo apt-get install build-essential"
            print_detail "   macOS: xcode-select --install"
            print_detail "3. Python headers missing"
            print_detail "   Ubuntu/Debian: sudo apt-get install python3-dev"
            echo ""
            print_info "Try running manually:"
            print_detail "$VENV_PYTHON -m pip install -r requirements.txt --verbose"
            exit 1
        fi
    fi
fi

INSTALLED_COUNT=$($VENV_PYTHON -m pip list | wc -l)
print_detail "Total packages in environment: $INSTALLED_COUNT"
echo ""

# Step 6: Download spacy model
echo "Step 6: Downloading NLP language model..."
print_detail "Checking if spacy model 'en_core_web_sm' is already installed..."

MODEL_INSTALLED=false
if $VENV_PYTHON -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    print_success "Model 'en_core_web_sm' already installed"
    MODEL_INSTALLED=true
    MODEL_INFO=$($VENV_PYTHON -m spacy info en_core_web_sm 2>/dev/null | grep -E "lang|name|version" | head -3)
    print_detail "Model info: $(echo $MODEL_INFO | tr '\n' ' ')"
else
    print_detail "Downloading spaCy model: en_core_web_sm (~15MB)"
    print_detail "This includes: tokenizer, parser, NER, word vectors"
    print_info "This may take 1-2 minutes depending on your connection..."

    if $VENV_PYTHON -m spacy download en_core_web_sm 2>&1 | tee /tmp/spacy_download.log; then
        if $VENV_PYTHON -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
            print_success "Language model downloaded and verified"
            MODEL_INSTALLED=true
        else
            print_error "Model downloaded but verification failed"
            MODEL_INSTALLED=false
        fi
    else
        print_error "Failed to download language model"
        print_info "This is not critical - the app will work with reduced NLP features"
        print_detail "You can install it later: $VENV_PYTHON -m spacy download en_core_web_sm"
        MODEL_INSTALLED=false
    fi
fi
echo ""

# Step 7: Setup configuration
echo "Step 7: Setting up configuration files..."
print_detail "Checking for setup_config.sh..."

if [ -f "setup_config.sh" ]; then
    print_detail "Running setup_config.sh..."
    if bash setup_config.sh; then
        print_success "Configuration files setup complete"
    else
        print_warning "setup_config.sh had issues, but continuing..."
        print_detail "Configuration files may need manual setup"
    fi
else
    print_warning "setup_config.sh not found, skipping config setup"
    print_detail "Creating .config directory manually..."
    mkdir -p .config
    print_success ".config directory created"
fi

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
echo "Step 8: Verifying installation..."
print_detail "Running final checks..."

# Check tkinter again (in case it was installed during setup)
print_detail "Checking tkinter availability..."
if $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
    TKINTER_VERSION=$($PYTHON_CMD -c "import tkinter; print(tkinter.TkVersion)" 2>/dev/null)
    print_detail "  ✓ tkinter ($TKINTER_VERSION)"
else
    print_detail "  ✗ tkinter (NOT INSTALLED - GUI will not work!)"
fi

print_detail "Checking key Python packages:"

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

# Check tkinter one more time for final summary
if ! $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
    echo ""
    print_error "CRITICAL: tkinter is NOT installed!"
    print_warning "The application GUI will NOT work without tkinter"
    print_info "Install tkinter before running the app:"
    echo "  See: docs/guides/TKINTER_INSTALLATION.md"
    echo "  Test: python3 -m tkinter"
    echo "  Quick test: python test_tkinter.py"
fi

echo ""
print_warning "IMPORTANT: You still need to configure API keys and credentials!"
echo ""
echo "Next steps:"
echo ""
echo "  0. Verify tkinter is installed (REQUIRED for GUI):"
echo "     python test_tkinter.py"
echo "     OR: python3 -m tkinter"
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
