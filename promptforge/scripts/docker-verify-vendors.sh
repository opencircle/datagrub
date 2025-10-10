#!/bin/bash
#
# Docker Vendor Library Verification Script
#
# This script verifies vendor libraries inside the Docker container
# and provides a comprehensive status report.
#
# Usage:
#   ./docker-verify-vendors.sh [--detailed]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}   PromptForge Vendor Library Verification (Docker)${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Check if API container is running
if ! docker-compose ps api | grep -q "Up"; then
    echo -e "${RED}✗ API container is not running${NC}"
    echo ""
    echo "Start the container with:"
    echo "  docker-compose up -d api"
    exit 1
fi

echo -e "${GREEN}✓ API container is running${NC}"
echo ""

# Run verification script inside container
echo -e "${BLUE}Running verification inside container...${NC}"
echo ""

if [ "$1" == "--detailed" ]; then
    docker-compose exec api python3 /app/scripts/verify_vendor_libraries.py --detailed
else
    docker-compose exec api python3 /app/scripts/verify_vendor_libraries.py
fi

VERIFICATION_EXIT_CODE=$?

echo ""
echo -e "${BLUE}================================================================${NC}"

if [ $VERIFICATION_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Verification completed successfully${NC}"
else
    echo -e "${RED}✗ Verification failed (exit code: $VERIFICATION_EXIT_CODE)${NC}"
fi

echo -e "${BLUE}================================================================${NC}"
echo ""

exit $VERIFICATION_EXIT_CODE
