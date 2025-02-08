#!/bin/bash

VENV_DIR="venv"
# Check if the virtual environment directory does not exist
if [ ! -d "$VENV_DIR" ]; then
    # Create the virtual environment
    python3 -m venv $VENV_DIR
    echo "Virtual environment created in $VENV_DIR"
else
    echo "Virtual environment already exists in $VENV_DIR"
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Install the required packages
pip install --upgrade pip
pip install -r requirements.txt
echo "Required packages installed from requirements.txt"
