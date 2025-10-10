#!/bin/bash

# Start Models MFE
# This script ensures mfe-models starts correctly

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}Starting Models MFE...${NC}"

# Navigate to mfe-models
cd "$(dirname "$0")/../mfe-models"

# Check if port 3006 is in use
if lsof -Pi :3006 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}Port 3006 is already in use. Stopping existing process...${NC}"
    kill -9 $(lsof -ti:3006) 2>/dev/null || true
    sleep 2
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}node_modules not found. Running npm install...${NC}"
    npm install
fi

# Start the dev server
echo -e "${GREEN}Starting webpack dev server on port 3006...${NC}"
npm start

echo -e "${GREEN}✓ Models MFE started successfully${NC}"
echo -e "${GREEN}  URL: http://localhost:3006${NC}"
echo -e "${GREEN}  Remote Entry: http://localhost:3006/remoteEntry.js${NC}"
