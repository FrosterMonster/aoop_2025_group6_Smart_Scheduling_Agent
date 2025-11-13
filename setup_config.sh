#!/bin/bash

# Setup script for AI Schedule Agent configuration
# This script creates your personal config files from templates

echo "=== AI Schedule Agent - Configuration Setup ==="
echo ""

CONFIG_DIR=".config"

# Check if config directory exists
if [ ! -d "$CONFIG_DIR" ]; then
    echo "Error: .config directory not found!"
    exit 1
fi

# Function to copy if not exists
copy_if_not_exists() {
    local template="$1"
    local target="$2"

    if [ -f "$target" ]; then
        echo "✓ $target already exists (skipping)"
    else
        if [ -f "$template" ]; then
            cp "$template" "$target"
            echo "✓ Created $target from template"
        else
            echo "✗ Template $template not found!"
        fi
    fi
}

echo "Step 1: Setting up configuration files..."
echo ""

# Copy config templates
copy_if_not_exists "$CONFIG_DIR/paths.json.example" "$CONFIG_DIR/paths.json"
copy_if_not_exists "$CONFIG_DIR/settings.json.example" "$CONFIG_DIR/settings.json"
copy_if_not_exists "$CONFIG_DIR/credentials.json.template" "$CONFIG_DIR/credentials.json"

echo ""
echo "Step 2: Creating necessary directories..."
mkdir -p "$CONFIG_DIR/data"
mkdir -p "$CONFIG_DIR/logs"
echo "✓ Created data and logs directories"

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Edit .config/credentials.json with your Google OAuth credentials"
echo "   (See .config/README.md for instructions)"
echo ""
echo "2. (Optional) Customize .config/settings.json:"
echo "   - Window size"
echo "   - Email notifications (SMTP settings)"
echo "   - Reminder times"
echo ""
echo "3. Run the application:"
echo "   ./run.sh"
echo ""
