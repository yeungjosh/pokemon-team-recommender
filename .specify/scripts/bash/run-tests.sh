#!/bin/bash
# Run test suite for Pokemon Team Recommender

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Pokemon Team Recommender - Test Runner${NC}"
echo ""

# Check if virtual environment is activated
if [ -z "${VIRTUAL_ENV:-}" ]; then
    echo -e "${YELLOW}⚠${NC} Virtual environment not activated"
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    else
        echo -e "${RED}Error: Virtual environment not found. Run ./setup-dev.sh first${NC}"
        exit 1
    fi
fi

# Parse arguments
COVERAGE=false
VERBOSE=false
FILTER=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --filter|-f)
            FILTER="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: ./run-tests.sh [--coverage|-c] [--verbose|-v] [--filter|-f <pattern>]"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="pytest tests/"

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ -n "$FILTER" ]; then
    PYTEST_CMD="$PYTEST_CMD -k '$FILTER'"
fi

if [ "$COVERAGE" = true ]; then
    echo -e "${BLUE}Running tests with coverage...${NC}"
    eval "$PYTEST_CMD --cov=src --cov-report=term-missing --cov-report=html"
    echo ""
    echo -e "${GREEN}Coverage report generated: htmlcov/index.html${NC}"
else
    echo -e "${BLUE}Running tests...${NC}"
    eval "$PYTEST_CMD"
fi

echo ""
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
