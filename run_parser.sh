#!/bin/bash

# Check if a virtual environment directory exists
if [ -d "venv" ]; then
    echo "Activating the virtual environment..."
    source venv/bin/activate
else
    echo "No virtual environment found. Creating a new one..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "No requirements.txt found. Please make sure dependencies are installed."
fi

# Run the main.py script
echo "Running main.py..."
python3 main.py

# Deactivate the virtual environment
echo "Deactivating the virtual environment..."
deactivate
