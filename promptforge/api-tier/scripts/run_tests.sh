#!/bin/bash
# API Test Runner
# Runs pytest inside the API Docker container with proper database configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running API Tests...${NC}"

# Change to project root
cd "$(dirname "$0")/../.."

# Check if Docker containers are running
if ! docker ps | grep -q promptforge-api; then
    echo -e "${RED}Error: API container is not running${NC}"
    echo "Start containers with: docker-compose up -d"
    exit 1
fi

if ! docker ps | grep -q promptforge-postgres; then
    echo -e "${RED}Error: PostgreSQL container is not running${NC}"
    echo "Start containers with: docker-compose up -d"
    exit 1
fi

# Run tests inside Docker container with correct database host
echo -e "${YELLOW}Executing tests in Docker container...${NC}"
docker-compose exec -T -e TEST_DB_HOST=postgres api pytest "${@:-tests/}" -v --tb=short

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${RED}✗ Tests failed${NC}"
    exit 1
fi
