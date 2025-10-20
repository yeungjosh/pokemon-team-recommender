#!/bin/bash
# Switch between git worktrees for parallel feature development

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Pokemon Team Recommender - Worktree Navigator${NC}"
echo ""

# List available worktrees
echo "Available worktrees:"
git worktree list | nl -w2 -s'. '
echo ""

# If argument provided, cd to that worktree
if [ $# -eq 1 ]; then
    WORKTREE_NAME=$1
    WORKTREE_PATH="./worktrees/${WORKTREE_NAME}"

    if [ -d "$WORKTREE_PATH" ]; then
        echo -e "${GREEN}Switching to worktree: ${WORKTREE_NAME}${NC}"
        cd "$WORKTREE_PATH"
        exec $SHELL
    else
        echo -e "${RED}Error: Worktree '${WORKTREE_NAME}' not found${NC}"
        echo "Usage: ./switch-worktree.sh <worktree-name>"
        echo "Available: data-pipeline, recommender-core, gradio-ui, testing, deployment"
        exit 1
    fi
else
    echo -e "${YELLOW}Usage: ./switch-worktree.sh <worktree-name>${NC}"
    echo "Available: data-pipeline, recommender-core, gradio-ui, testing, deployment"
    echo ""
    echo "Example: ./switch-worktree.sh data-pipeline"
fi
