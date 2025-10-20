#!/bin/bash
# Initialize development environment for Pokemon Team Recommender

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Pokemon Team Recommender - Development Setup${NC}"
echo ""

# Check Python version
echo -e "${BLUE}[1/6]${NC} Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} found"
echo ""

# Create virtual environment
echo -e "${BLUE}[2/6]${NC} Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${YELLOW}⚠${NC} Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo -e "${BLUE}[3/6]${NC} Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"
echo ""

# Upgrade pip
echo -e "${BLUE}[4/6]${NC} Upgrading pip..."
pip install --upgrade pip --quiet
echo -e "${GREEN}✓${NC} pip upgraded"
echo ""

# Install dependencies
echo -e "${BLUE}[5/6]${NC} Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} requirements.txt not found, skipping dependency installation"
fi
echo ""

# Install development dependencies
echo -e "${BLUE}[6/6]${NC} Installing development dependencies..."
pip install --quiet ruff black pytest pytest-cov
echo -e "${GREEN}✓${NC} Development dependencies installed"
echo ""

echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "To activate the virtual environment manually, run:"
echo -e "${YELLOW}source venv/bin/activate${NC}"
echo ""
echo "To run the app locally:"
echo -e "${YELLOW}python app.py${NC}"
echo ""
echo "To run tests:"
echo -e "${YELLOW}pytest tests/${NC}"
echo ""
echo "To format code:"
echo -e "${YELLOW}black .${NC}"
echo ""
echo "To lint code:"
echo -e "${YELLOW}ruff check .${NC}"
