#!/bin/bash
# Dev environment setup

set -e

echo "Setting up Pokemon Team Recommender..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    exit 1
fi

# Create venv
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Created virtual environment"
fi

# Activate and install
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "Done! Activate with: source venv/bin/activate"
