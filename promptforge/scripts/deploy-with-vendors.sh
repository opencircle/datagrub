#!/bin/bash
#
# Deploy PromptForge with Vendor Libraries
#
# This script builds and deploys the PromptForge API with all vendor evaluation libraries.
# It uses a two-stage approach to avoid Docker build timeouts:
#   1. Build base image (fast, ~2 min)
#   2. Install vendor libraries in running container (~3-5 min)
#
# Usage:
#   ./deploy-with-vendors.sh [--skip-build] [--skip-vendors] [--verify]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Parse arguments
SKIP_BUILD=false
SKIP_VENDORS=false
VERIFY=false

for arg in "$@"; do
    case $arg in
        --skip-build)
            SKIP_BUILD=true
            ;;
        --skip-vendors)
            SKIP_VENDORS=true
            ;;
        --verify)
            VERIFY=true
            ;;
    esac
done

echo -e "${BLUE}${BOLD}================================================================${NC}"
echo -e "${BLUE}${BOLD}   PromptForge Deployment with Vendor Libraries${NC}"
echo -e "${BLUE}${BOLD}================================================================${NC}"
echo ""

cd "$PROJECT_ROOT"

#
# Step 1: Build Docker Image
#
if [ "$SKIP_BUILD" = false ]; then
    echo -e "${BLUE}Step 1: Building Docker image...${NC}"
    echo ""

    docker-compose down
    docker-compose build api

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Docker build failed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Docker image built successfully${NC}"
    echo ""
else
    echo -e "${YELLOW}⊘ Skipping Docker build${NC}"
    echo ""
fi

#
# Step 2: Start Services
#
echo -e "${BLUE}Step 2: Starting services...${NC}"
echo ""

docker-compose up -d

# Wait for API to be ready
echo -n "Waiting for API to start"
for i in {1..30}; do
    if docker-compose exec -T api python3 -c "print('ok')" &>/dev/null; then
        echo ""
        echo -e "${GREEN}✓ API container is ready${NC}"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

#
# Step 3: Install Vendor Libraries
#
if [ "$SKIP_VENDORS" = false ]; then
    echo -e "${BLUE}Step 3: Installing vendor evaluation libraries...${NC}"
    echo -e "${YELLOW}This may take 3-5 minutes...${NC}"
    echo ""

    docker-compose exec -T api bash /app/scripts/install_vendor_libraries.sh

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Vendor library installation failed${NC}"
        echo ""
        echo "Check logs with: docker-compose logs api"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}✓ Vendor libraries installed successfully${NC}"
    echo ""
else
    echo -e "${YELLOW}⊘ Skipping vendor library installation${NC}"
    echo ""
fi

#
# Step 4: Restart API (to load new libraries)
#
echo -e "${BLUE}Step 4: Restarting API to load vendor libraries...${NC}"
echo ""

docker-compose restart api

# Wait for restart
echo -n "Waiting for API restart"
for i in {1..30}; do
    if curl -sf http://localhost:8000/health &>/dev/null; then
        echo ""
        echo -e "${GREEN}✓ API restarted and healthy${NC}"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

#
# Step 5: Verify Installation (if requested)
#
if [ "$VERIFY" = true ]; then
    echo -e "${BLUE}Step 5: Verifying installation...${NC}"
    echo ""

    "$SCRIPT_DIR/docker-verify-vendors.sh" --detailed

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Verification failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⊘ Skipping verification (use --verify to enable)${NC}"
    echo ""
fi

#
# Summary
#
echo -e "${BLUE}${BOLD}================================================================${NC}"
echo -e "${GREEN}${BOLD}✓ Deployment Complete!${NC}"
echo -e "${BLUE}${BOLD}================================================================${NC}"
echo ""
echo "PromptForge API is running with vendor evaluation libraries."
echo ""
echo "Quick checks:"
echo "  - API health: curl http://localhost:8000/health"
echo "  - Evaluation catalog: curl http://localhost:8000/api/v1/evaluation-catalog/catalog | jq 'length'"
echo "  - Vendor verification: ./scripts/docker-verify-vendors.sh"
echo ""
echo "Logs:"
echo "  - View logs: docker-compose logs -f api"
echo "  - Check registry: docker-compose exec api python3 -c 'from app.evaluations.registry import registry; print(len(registry._adapters))'"
echo ""

exit 0
