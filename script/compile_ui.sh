#!/bin/bash

# Exit on error
set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/../.venv"
UI_DIR="$SCRIPT_DIR/../qwindow"
PYUIC="$VENV_DIR/bin/pyside6-uic"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR"
    exit 1
fi

# Check if PyUIC exists
if [ ! -f "$PYUIC" ]; then
    echo "Error: PyUIC not found at $PYUIC"
    echo "Please ensure PySide6 is installed in your virtual environment"
    exit 1
fi

# UI files to compile
declare -a UI_FILES=(
    "MainWindow.ui"
    "BatchContent.ui"
    "BatchCode.ui"
    "SettingsModel.ui"
    "SettingsPrompt.ui"
)

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Compile each UI file
for ui_file in "${UI_FILES[@]}"; do
    input_file="$UI_DIR/$ui_file"
    output_file="$UI_DIR/${ui_file%.ui}_ui.py"
    
    echo "Compiling $ui_file..."
    
    if [ ! -f "$input_file" ]; then
        echo "Error: UI file not found: $input_file"
        deactivate
        exit 1
    fi
    
    if ! "$PYUIC" "$input_file" -o "$output_file"; then
        echo "Error: Failed to compile $ui_file"
        deactivate
        exit 1
    fi
done

# Deactivate virtual environment
deactivate

echo "UI compilation completed successfully"
exit 0
