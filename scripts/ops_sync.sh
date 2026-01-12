#!/bin/bash

# =============================================================================
# OPS_SYNC.SH - Automated Git Operations
# =============================================================================
# A.B.E.L. Project - Commit & Sync Script
# Usage: ./scripts/ops_sync.sh "commit message" [--push]
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# COLORS
# -----------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------

print_header() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                    A.B.E.L. OPS SYNC                           ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

check_env_files() {
    # SECURITY: Ensure .env files are not being committed
    if git diff --cached --name-only 2>/dev/null | grep -q "\.env$"; then
        print_error "SECURITY VIOLATION: .env file detected in staged files!"
        print_error "Remove .env from staging: git reset HEAD .env"
        exit 1
    fi

    if git diff --cached --name-only 2>/dev/null | grep -q "\.env\.local$"; then
        print_error "SECURITY VIOLATION: .env.local file detected in staged files!"
        exit 1
    fi
}

check_secrets() {
    # SECURITY: Scan for potential secrets in staged files
    local patterns=(
        "AKIA[0-9A-Z]{16}"           # AWS Access Key
        "sk-[a-zA-Z0-9]{48}"          # OpenAI API Key
        "ghp_[a-zA-Z0-9]{36}"         # GitHub Personal Access Token
        "AIza[0-9A-Za-z\-_]{35}"      # Google API Key
    )

    for pattern in "${patterns[@]}"; do
        if git diff --cached 2>/dev/null | grep -qE "$pattern"; then
            print_error "SECURITY VIOLATION: Potential secret detected in staged changes!"
            print_error "Pattern matched: $pattern"
            print_error "Please review and remove secrets before committing."
            exit 1
        fi
    done
}

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

print_header

# Check arguments
if [ -z "$1" ]; then
    print_error "Usage: $0 \"commit message\" [--push]"
    exit 1
fi

COMMIT_MSG="$1"
SHOULD_PUSH=false

if [ "$2" == "--push" ]; then
    SHOULD_PUSH=true
fi

# Get current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "master")
print_step "Current branch: $BRANCH"

# Security checks
print_step "Running security checks..."
check_env_files
check_secrets

# Git operations
print_step "Staging changes..."
git add -A

# Check if there are changes to commit
if git diff --cached --quiet 2>/dev/null; then
    print_warning "No changes to commit."
    exit 0
fi

# Show status
print_step "Changes to be committed:"
git diff --cached --stat

# Commit
print_step "Creating commit..."
git commit -m "$COMMIT_MSG"

# Push if requested
if [ "$SHOULD_PUSH" = true ]; then
    print_step "Pushing to origin/$BRANCH..."
    git push origin "$BRANCH" 2>/dev/null || git push -u origin "$BRANCH"
    print_step "Push complete!"
fi

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    SYNC COMPLETE                               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
print_step "Commit: $COMMIT_MSG"
print_step "Branch: $BRANCH"
if [ "$SHOULD_PUSH" = true ]; then
    print_step "Pushed: Yes"
else
    print_warning "Pushed: No (use --push to push)"
fi
