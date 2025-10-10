#!/bin/bash

###############################################################################
# PromptForge UI - Stop All Micro-Frontends
#
# This script stops all running MFE applications
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# MFE applications
MFES=(
    "shell"
    "mfe-projects"
    "mfe-evaluations"
    "mfe-playground"
    "mfe-traces"
    "mfe-policy"
    "mfe-models"
    "mfe-insights"
)

# Function to stop an MFE
stop_mfe() {
    local mfe_name=$1
    local pid_file="logs/${mfe_name}.pid"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            log_info "Stopping $mfe_name (PID: $pid)..."
            kill $pid 2>/dev/null || true
            rm "$pid_file"
            log_success "$mfe_name stopped"
        else
            log_warning "$mfe_name process not running (stale PID file)"
            rm "$pid_file"
        fi
    else
        log_info "$mfe_name is not running (no PID file)"
    fi
}

# Main execution
main() {
    log_info "==================================================================="
    log_info "  PromptForge UI - Stopping All Micro-Frontends"
    log_info "==================================================================="
    echo ""

    # Stop all MFEs
    for mfe_name in "${MFES[@]}"; do
        stop_mfe "$mfe_name"
    done

    # Also kill any webpack-dev-server processes on ports 3000-3007
    log_info "Checking for orphaned webpack-dev-server processes..."
    for port in {3000..3007}; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_info "Killing process on port $port..."
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
        fi
    done

    echo ""
    log_success "==================================================================="
    log_success "  All MFE applications stopped"
    log_success "==================================================================="
}

# Run main function
main
