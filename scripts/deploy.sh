#!/bin/bash
# IBM Sterling EDI Application - Linux/Unix Deployment Script
# Run this script with appropriate permissions

set -e  # Exit on error

INSTALL_PATH="${INSTALL_PATH:-/opt/edi/sterling_edi_app}"
PYTHON_CMD="${PYTHON_CMD:-python3}"
SKIP_DEPS="${SKIP_DEPS:-false}"

echo "IBM Sterling EDI Application - Linux/Unix Deployment"
echo "===================================================="
echo ""

# Check if running as root (for some operations)
if [ "$EUID" -eq 0 ]; then
    RUN_AS_ROOT=true
else
    RUN_AS_ROOT=false
    echo "WARNING: Not running as root. Some operations may require sudo."
fi

# Step 1: Verify Python installation
echo "Step 1: Verifying Python installation..."
if command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    echo "  Found: $PYTHON_VERSION"
else
    echo "  ERROR: Python not found. Please install Python 3.8 or higher."
    exit 1
fi

# Step 2: Create installation directory
echo "Step 2: Creating installation directory..."
if [ ! -d "$INSTALL_PATH" ]; then
    mkdir -p "$INSTALL_PATH"
    echo "  Created: $INSTALL_PATH"
else
    echo "  Directory exists: $INSTALL_PATH"
fi

# Step 3: Copy application files
echo "Step 3: Copying application files..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$(dirname "$SCRIPT_DIR")"

if [ -d "$APP_DIR" ]; then
    cp -r "$APP_DIR"/* "$INSTALL_PATH/" 2>/dev/null || true
    # Remove Python cache files
    find "$INSTALL_PATH" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$INSTALL_PATH" -name "*.pyc" -delete 2>/dev/null || true
    echo "  Files copied to: $INSTALL_PATH"
else
    echo "  WARNING: Could not find application files. Manual copy may be required."
fi

# Step 4: Install dependencies
if [ "$SKIP_DEPS" != "true" ]; then
    echo "Step 4: Installing Python dependencies..."
    cd "$INSTALL_PATH"
    $PYTHON_CMD -m pip install --upgrade pip --quiet
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "  Dependencies installed successfully"
    else
        echo "  WARNING: Some dependencies may have failed to install."
    fi
else
    echo "Step 4: Skipping dependency installation (SKIP_DEPS=true)"
fi

# Step 5: Create required directories
echo "Step 5: Creating required directories..."
directories=(
    "$INSTALL_PATH/logs"
    "$INSTALL_PATH/processed"
    "$INSTALL_PATH/error"
)

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "  Created: $dir"
    fi
done

# Step 6: Set permissions
echo "Step 6: Setting permissions..."
if [ "$RUN_AS_ROOT" = true ]; then
    # Create service user if it doesn't exist
    if ! id "edi_service" &>/dev/null; then
        useradd -r -s /bin/false edi_service 2>/dev/null || echo "  Note: Could not create edi_service user"
    fi
    chown -R edi_service:edi_service "$INSTALL_PATH" 2>/dev/null || echo "  Note: Could not change ownership"
fi

chmod -R 755 "$INSTALL_PATH"
echo "  Permissions set"

# Step 7: Verify configuration files
echo "Step 7: Verifying configuration files..."
config_files=(
    "$INSTALL_PATH/config/config.yaml"
    "$INSTALL_PATH/config/sterling_config.yaml"
)

for config_file in "${config_files[@]}"; do
    if [ -f "$config_file" ]; then
        echo "  Found: $config_file"
    else
        echo "  WARNING: Missing: $config_file"
    fi
done

# Step 8: Test installation
echo "Step 8: Testing installation..."
cd "$INSTALL_PATH"
if $PYTHON_CMD -c "import yaml; import requests; print('OK')" 2>&1 | grep -q "OK"; then
    echo "  Installation test passed"
else
    echo "  WARNING: Installation test may have issues"
fi

echo ""
echo "Deployment completed!"
echo ""
echo "Next steps:"
echo "1. Edit configuration files in: $INSTALL_PATH/config/"
echo "2. Configure Sterling directories in: $INSTALL_PATH/config/sterling_config.yaml"
echo "3. Test with: $PYTHON_CMD $INSTALL_PATH/main.py process --file tests/sample_data/sample_850.x12"
echo "4. See docs/DEPLOYMENT.md for detailed setup instructions"
echo ""

