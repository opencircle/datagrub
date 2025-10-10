#!/bin/bash

###############################################################################
# PromptForge UI - Start All Micro-Frontends
#
# This script starts all MFE applications and the shell in development mode
# Ensures all dependencies are installed before starting
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
    "shell:3000"
    "mfe-projects:3001"
    "mfe-evaluations:3002"
    "mfe-playground:3003"
    "mfe-traces:3004"
    "mfe-policy:3005"
    "mfe-models:3006"
    "mfe-insights:3007"
)

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to install dependencies for an MFE
install_dependencies() {
    local mfe_name=$1

    if [ ! -d "$mfe_name/node_modules" ]; then
        log_info "Installing dependencies for $mfe_name..."
        cd "$mfe_name"
        npm install
        cd ..
        log_success "Dependencies installed for $mfe_name"
    else
        log_info "Dependencies already installed for $mfe_name"
    fi
}

# Function to start an MFE
start_mfe() {
    local mfe_info=$1
    local mfe_name=$(echo $mfe_info | cut -d: -f1)
    local port=$(echo $mfe_info | cut -d: -f2)

    log_info "Starting $mfe_name on port $port..."

    # Check if port is already in use
    if check_port $port; then
        log_warning "$mfe_name port $port is already in use. Skipping..."
        return 0
    fi

    # Start the MFE in background
    cd "$mfe_name"
    npm start > "../logs/${mfe_name}.log" 2>&1 &
    local pid=$!
    echo $pid > "../logs/${mfe_name}.pid"
    cd ..

    log_success "$mfe_name started (PID: $pid)"
}

# Main execution
main() {
    log_info "==================================================================="
    log_info "  PromptForge UI - Starting All Micro-Frontends"
    log_info "==================================================================="

    # Create logs directory
    mkdir -p logs

    # Check if backend is running
    log_info "Checking backend API health..."
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Backend API is healthy"
    else
        log_warning "Backend API is not responding. UI will work but API calls will fail."
        log_warning "Start backend with: docker-compose up -d"
    fi

    echo ""
    log_info "Installing dependencies for all MFEs..."
    echo ""

    # Install dependencies for all MFEs
    for mfe_info in "${MFES[@]}"; do
        mfe_name=$(echo $mfe_info | cut -d: -f1)
        install_dependencies "$mfe_name"
    done

    echo ""
    log_info "Starting all MFE applications..."
    echo ""

    # Start all MFEs
    for mfe_info in "${MFES[@]}"; do
        start_mfe "$mfe_info"
        sleep 2  # Wait before starting next MFE
    done

    echo ""
    log_success "==================================================================="
    log_success "  All MFE applications started successfully!"
    log_success "==================================================================="
    echo ""
    log_info "Application URLs:"
    echo "  - Shell (Main App):    http://localhost:3000"
    echo "  - Projects MFE:        http://localhost:3001"
    echo "  - Evaluations MFE:     http://localhost:3002"
    echo "  - Playground MFE:      http://localhost:3003"
    echo "  - Traces MFE:          http://localhost:3004"
    echo "  - Policy MFE:          http://localhost:3005"
    echo "  - Models MFE:          http://localhost:3006"
    echo "  - Deep Insights MFE:   http://localhost:3007"
    echo ""
    log_info "Backend API:           http://localhost:8000"
    echo ""
    log_info "Logs are stored in:    ./logs/"
    echo ""
    log_info "To stop all MFEs, run: ./stop-all-mfes.sh"
    log_info "To view logs, run:     tail -f logs/<mfe-name>.log"
    echo ""
}

# Run main function
main
