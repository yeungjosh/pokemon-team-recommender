#!/bin/bash
# Deploy Pokemon Team Recommender to Hugging Face Spaces

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Pokemon Team Recommender - Hugging Face Spaces Deployment${NC}"
echo ""

# Check if HF remote exists
if ! git remote | grep -q "^hf$"; then
    echo -e "${YELLOW}⚠${NC} Hugging Face remote not configured"
    echo ""
    echo "To add Hugging Face Spaces remote:"
    echo -e "${BLUE}git remote add hf https://huggingface.co/spaces/<username>/pokemon-team-recommender${NC}"
    echo ""
    read -p "Enter your Hugging Face username: " HF_USERNAME

    if [ -z "$HF_USERNAME" ]; then
        echo -e "${RED}Error: Username cannot be empty${NC}"
        exit 1
    fi

    HF_REMOTE="https://huggingface.co/spaces/${HF_USERNAME}/pokemon-team-recommender"
    git remote add hf "$HF_REMOTE"
    echo -e "${GREEN}✓${NC} Hugging Face remote added: $HF_REMOTE"
    echo ""
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}Current branch:${NC} $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}⚠${NC} You are not on the main branch"
    read -p "Deploy from '$CURRENT_BRANCH' anyway? (y/N): " CONFIRM
    if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled"
        exit 0
    fi
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠${NC} You have uncommitted changes"
    echo ""
    git status --short
    echo ""
    read -p "Commit changes before deploying? (Y/n): " COMMIT_CONFIRM
    if [[ ! $COMMIT_CONFIRM =~ ^[Nn]$ ]]; then
        read -p "Enter commit message: " COMMIT_MSG
        if [ -z "$COMMIT_MSG" ]; then
            COMMIT_MSG="Update for deployment"
        fi
        git add .
        git commit -m "$COMMIT_MSG"
        echo -e "${GREEN}✓${NC} Changes committed"
    else
        echo -e "${RED}Deployment cancelled - please commit or stash changes${NC}"
        exit 1
    fi
fi

# Run tests before deployment
echo ""
echo -e "${BLUE}Running tests before deployment...${NC}"
if [ -f ".specify/scripts/bash/run-tests.sh" ] && [ -d "tests" ]; then
    if .specify/scripts/bash/run-tests.sh; then
        echo -e "${GREEN}✓${NC} Tests passed"
    else
        echo -e "${RED}✗${NC} Tests failed"
        read -p "Deploy anyway? (y/N): " DEPLOY_CONFIRM
        if [[ ! $DEPLOY_CONFIRM =~ ^[Yy]$ ]]; then
            echo "Deployment cancelled"
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠${NC} No tests found, skipping test run"
fi

# Push to Hugging Face Spaces
echo ""
echo -e "${BLUE}Deploying to Hugging Face Spaces...${NC}"
if git push hf "$CURRENT_BRANCH:main"; then
    echo ""
    echo -e "${GREEN}✓ Deployment successful!${NC}"
    echo ""

    # Extract username from remote URL
    HF_URL=$(git remote get-url hf)
    if [[ $HF_URL =~ spaces/([^/]+)/([^/\.]+) ]]; then
        USERNAME="${BASH_REMATCH[1]}"
        SPACE_NAME="${BASH_REMATCH[2]}"
        echo "View your Space at:"
        echo -e "${BLUE}https://huggingface.co/spaces/${USERNAME}/${SPACE_NAME}${NC}"
    fi
    echo ""
    echo "Monitor build logs in the Spaces interface"
else
    echo ""
    echo -e "${RED}✗ Deployment failed${NC}"
    echo "Check git output above for errors"
    exit 1
fi
