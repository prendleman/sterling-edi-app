#!/bin/bash
# Setup Sterling B2B Integrator Directories
# This script creates the directory structure expected by Sterling

STERLING_BASE="${STERLING_BASE:-/opt/sterling}"
OWNER_USER="${OWNER_USER:-sterling}"
OWNER_GROUP="${OWNER_GROUP:-sterling}"

echo "Setting up Sterling B2B Integrator directories..."
echo "Base path: $STERLING_BASE"
echo ""

# Create directory structure
directories=(
    "$STERLING_BASE/pickup"
    "$STERLING_BASE/pickup/processed"
    "$STERLING_BASE/pickup/error"
    "$STERLING_BASE/delivery"
    "$STERLING_BASE/archive"
)

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "Created: $dir"
    else
        echo "Exists: $dir"
    fi
done

# Set ownership (if running as root)
if [ "$EUID" -eq 0 ]; then
    if id "$OWNER_USER" &>/dev/null; then
        chown -R "$OWNER_USER:$OWNER_GROUP" "$STERLING_BASE"
        echo "Set ownership to: $OWNER_USER:$OWNER_GROUP"
    else
        echo "WARNING: User $OWNER_USER does not exist. Skipping ownership change."
    fi
fi

# Set permissions
chmod -R 755 "$STERLING_BASE"
echo "Set permissions to 755"

echo ""
echo "Sterling directory setup complete!"
echo ""

