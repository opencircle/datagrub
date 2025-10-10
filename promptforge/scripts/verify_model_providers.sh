#!/bin/bash
#
# Model Provider Configuration - Verification Script
#
# This script verifies that the Model Provider feature is working correctly
# by testing the API endpoints and checking the database state.
#

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Model Provider Configuration Verification"
echo "========================================"
echo ""

# Check if services are running
echo -e "${YELLOW}1. Checking Docker Services...${NC}"
if docker ps | grep -q "promptforge-api"; then
    echo -e "${GREEN}✓ API service is running${NC}"
else
    echo -e "${RED}✗ API service is not running${NC}"
    exit 1
fi

if docker ps | grep -q "promptforge-postgres"; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${RED}✗ PostgreSQL is not running${NC}"
    exit 1
fi
echo ""

# Check database tables
echo -e "${YELLOW}2. Checking Database Tables...${NC}"
TABLES=$(docker exec promptforge-postgres psql -U promptforge -d promptforge -t -c "SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename LIKE 'model_provider%';" | tr -d ' ')

if echo "$TABLES" | grep -q "model_provider_metadata"; then
    echo -e "${GREEN}✓ model_provider_metadata table exists${NC}"
else
    echo -e "${RED}✗ model_provider_metadata table not found${NC}"
    exit 1
fi

if echo "$TABLES" | grep -q "model_provider_configs"; then
    echo -e "${GREEN}✓ model_provider_configs table exists${NC}"
else
    echo -e "${RED}✗ model_provider_configs table not found${NC}"
    exit 1
fi
echo ""

# Check seed data
echo -e "${YELLOW}3. Checking Provider Metadata (Seed Data)...${NC}"
PROVIDER_COUNT=$(docker exec promptforge-postgres psql -U promptforge -d promptforge -t -c "SELECT COUNT(*) FROM model_provider_metadata WHERE is_active = true;" | tr -d ' ')

if [ "$PROVIDER_COUNT" -ge 1 ]; then
    echo -e "${GREEN}✓ Found $PROVIDER_COUNT active providers in catalog${NC}"

    # Show provider list
    echo ""
    docker exec promptforge-postgres psql -U promptforge -d promptforge -c "SELECT provider_name, provider_type, display_name FROM model_provider_metadata WHERE is_active = true ORDER BY provider_name;"
else
    echo -e "${RED}✗ No providers found in catalog${NC}"
    echo "Run: docker exec promptforge-api python scripts/seed_model_providers.py"
    exit 1
fi
echo ""

# Check existing configs
echo -e "${YELLOW}4. Checking Existing Provider Configurations...${NC}"
CONFIG_COUNT=$(docker exec promptforge-postgres psql -U promptforge -d promptforge -t -c "SELECT COUNT(*) FROM model_provider_configs WHERE is_active = true;" | tr -d ' ')

if [ "$CONFIG_COUNT" -ge 1 ]; then
    echo -e "${GREEN}✓ Found $CONFIG_COUNT active provider configuration(s)${NC}"

    # Show config list (with masked keys)
    echo ""
    docker exec promptforge-postgres psql -U promptforge -d promptforge -c "SELECT display_name, provider_name, substring(api_key_encrypted, 1, 20) || '...' as api_key_preview, is_default, created_at::date FROM model_provider_configs WHERE is_active = true ORDER BY created_at DESC;"
else
    echo -e "${YELLOW}⚠ No provider configurations found (this is OK for new installations)${NC}"
fi
echo ""

# Test catalog endpoint
echo -e "${YELLOW}5. Testing Catalog Endpoint (Public)...${NC}"
CATALOG_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8000/api/v1/model-providers/catalog)
HTTP_CODE=$(echo "$CATALOG_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Catalog endpoint returned 200 OK${NC}"

    # Parse and show provider count
    PROVIDER_COUNT_API=$(echo "$CATALOG_RESPONSE" | grep -v "HTTP_CODE" | jq -r '.providers | length' 2>/dev/null || echo "0")
    echo -e "${GREEN}✓ API returned $PROVIDER_COUNT_API providers${NC}"

    # Show first provider
    FIRST_PROVIDER=$(echo "$CATALOG_RESPONSE" | grep -v "HTTP_CODE" | jq -r '.providers[0].display_name' 2>/dev/null || echo "")
    if [ -n "$FIRST_PROVIDER" ]; then
        echo -e "  First provider: $FIRST_PROVIDER"
    fi
else
    echo -e "${RED}✗ Catalog endpoint returned HTTP $HTTP_CODE${NC}"
    echo "Response:"
    echo "$CATALOG_RESPONSE" | grep -v "HTTP_CODE"
    exit 1
fi
echo ""

# Check API logs for errors
echo -e "${YELLOW}6. Checking Recent API Logs for Errors...${NC}"
ERROR_COUNT=$(docker logs promptforge-api --tail 100 2>&1 | grep -i "error" | grep -i "model.provider" | wc -l | tr -d ' ')

if [ "$ERROR_COUNT" = "0" ]; then
    echo -e "${GREEN}✓ No recent errors related to model providers${NC}"
else
    echo -e "${YELLOW}⚠ Found $ERROR_COUNT error(s) in recent logs${NC}"
    echo "Recent errors:"
    docker logs promptforge-api --tail 100 2>&1 | grep -i "error" | grep -i "model.provider" | tail -5
fi
echo ""

# Check encryption key
echo -e "${YELLOW}7. Checking Encryption Configuration...${NC}"
ENCRYPTION_CONFIGURED=$(docker exec promptforge-api python -c "from app.core.config import settings; print(bool(settings.MODEL_PROVIDER_ENCRYPTION_KEY))" 2>/dev/null)

if [ "$ENCRYPTION_CONFIGURED" = "True" ]; then
    echo -e "${GREEN}✓ MODEL_PROVIDER_ENCRYPTION_KEY is configured${NC}"
else
    echo -e "${RED}✗ MODEL_PROVIDER_ENCRYPTION_KEY not configured${NC}"
    exit 1
fi
echo ""

# Check mfe-models build
echo -e "${YELLOW}8. Checking MFE-Models Build...${NC}"
if [ -f "/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-models/dist/remoteEntry.js" ]; then
    echo -e "${GREEN}✓ mfe-models is built (remoteEntry.js exists)${NC}"

    BUILD_SIZE=$(du -h /Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-models/dist/remoteEntry.js | cut -f1)
    echo -e "  Build size: $BUILD_SIZE"
else
    echo -e "${YELLOW}⚠ mfe-models not built (run: cd ui-tier/mfe-models && npm run build)${NC}"
fi
echo ""

# Summary
echo "========================================"
echo -e "${GREEN}Summary${NC}"
echo "========================================"
echo ""
echo "Backend Infrastructure:"
echo -e "  ${GREEN}✓${NC} Database tables created"
echo -e "  ${GREEN}✓${NC} Provider metadata seeded ($PROVIDER_COUNT providers)"
echo -e "  ${GREEN}✓${NC} Encryption configured"
echo -e "  ${GREEN}✓${NC} API endpoints working"
echo ""
echo "Existing Data:"
echo -e "  ${GREEN}✓${NC} $CONFIG_COUNT provider configuration(s)"
echo ""
echo "Next Steps:"
echo "  1. Start all MFE services:"
echo "     cd /Users/rohitiyer/datagrub/promptforge/ui-tier"
echo "     npm run dev (in separate terminals for each MFE)"
echo ""
echo "  2. Access the Model Dashboard:"
echo "     http://localhost:3000/models"
echo ""
echo "  3. Test Provider Configuration:"
echo "     - View existing providers"
echo "     - Add new provider (Admin role required)"
echo "     - Test connection"
echo ""
echo -e "${GREEN}✓ Verification Complete!${NC}"
echo ""
