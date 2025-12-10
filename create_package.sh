#!/bin/bash
# Create deployment package (ZIP file)
# Run this script from the sterling_edi_app directory

PACKAGE_NAME="sterling_edi_app.zip"
EXCLUDE_PATTERNS="*.pyc __pycache__ *.log .git .gitignore"

echo "Creating deployment package: $PACKAGE_NAME"

# Remove existing package if it exists
if [ -f "$PACKAGE_NAME" ]; then
    rm "$PACKAGE_NAME"
    echo "Removed existing package"
fi

# Create ZIP file excluding patterns
zip -r "$PACKAGE_NAME" . \
    -x "*.pyc" \
    -x "__pycache__/*" \
    -x "*.log" \
    -x ".git/*" \
    -x ".gitignore" \
    -x "$PACKAGE_NAME"

if [ $? -eq 0 ]; then
    echo "Package created: $PACKAGE_NAME"
    echo "Size: $(du -h "$PACKAGE_NAME" | cut -f1)"
else
    echo "Error creating package"
    exit 1
fi

