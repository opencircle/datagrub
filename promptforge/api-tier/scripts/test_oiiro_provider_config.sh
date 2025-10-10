#!/bin/bash
#
# Test Model Provider Configuration API with Oiiro OpenAI Example
#
# This script demonstrates:
# 1. Creating an OpenAI API key configuration for Oiiro organization
# 2. Retrieving the configuration
# 3. Updating the configuration if needed
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# API Configuration
API_URL="http://localhost:8000/api/v1"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTk2OTc5OTksInN1YiI6ImVhNGFiMTg2LWMzMWUtNDA1OS05OTZlLTI5ZWE5OWVhNmM0NyIsInR5cGUiOiJhY2Nlc3MifQ.t_gJA9zyUAplq1Th6o1DC5goCDAt8sitt6EGPCOanno"

# Sample OpenAI API key (replace with actual key for real usage)
OPENAI_API_KEY="sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Model Provider Configuration Test${NC}"
echo -e "${BLUE}Oiiro OpenAI Configuration Example${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Step 1: List available providers in catalog
echo -e "${YELLOW}Step 1: List Provider Catalog${NC}"
echo "GET ${API_URL}/model-providers/catalog"
echo ""
CATALOG_RESPONSE=$(curl -s -X GET \
  "${API_URL}/model-providers/catalog" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")
echo "${CATALOG_RESPONSE}" | python3 -m json.tool
echo ""

# Step 2: Check existing configurations
echo -e "${YELLOW}Step 2: Check Existing Configurations${NC}"
echo "GET ${API_URL}/model-providers/configs"
echo ""
EXISTING_CONFIGS=$(curl -s -X GET \
  "${API_URL}/model-providers/configs" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")
echo "${EXISTING_CONFIGS}" | python3 -m json.tool
echo ""

# Extract config ID if exists
CONFIG_ID=$(echo "${EXISTING_CONFIGS}" | python3 -c "import sys, json; data = json.load(sys.stdin); configs = [c for c in data.get('configs', []) if c['provider_name'] == 'openai']; print(configs[0]['id'] if configs else '')" 2>/dev/null || echo "")

if [ -n "${CONFIG_ID}" ]; then
  echo -e "${GREEN}✓ Found existing OpenAI configuration: ${CONFIG_ID}${NC}"
  echo ""

  # Step 3a: Get specific configuration
  echo -e "${YELLOW}Step 3: Get Specific Configuration${NC}"
  echo "GET ${API_URL}/model-providers/configs/${CONFIG_ID}"
  echo ""
  CONFIG_DETAIL=$(curl -s -X GET \
    "${API_URL}/model-providers/configs/${CONFIG_ID}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json")
  echo "${CONFIG_DETAIL}" | python3 -m json.tool
  echo ""

  # Step 4a: Update configuration
  echo -e "${YELLOW}Step 4: Update Configuration${NC}"
  echo "PUT ${API_URL}/model-providers/configs/${CONFIG_ID}"
  echo ""
  UPDATE_DATA='{
    "display_name": "Oiiro OpenAI Production (Updated)",
    "config": {
      "organization_id": "org-oiiro",
      "default_model": "gpt-4-turbo",
      "max_tokens": 8192,
      "temperature": 0.7
    }
  }'
  echo "Request Body:"
  echo "${UPDATE_DATA}" | python3 -m json.tool
  echo ""

  UPDATE_RESPONSE=$(curl -s -X PUT \
    "${API_URL}/model-providers/configs/${CONFIG_ID}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "${UPDATE_DATA}")
  echo "Response:"
  echo "${UPDATE_RESPONSE}" | python3 -m json.tool
  echo ""

  echo -e "${GREEN}✓ Configuration updated successfully${NC}"

else
  echo -e "${YELLOW}No existing OpenAI configuration found${NC}"
  echo ""

  # Step 3b: Create new configuration
  echo -e "${YELLOW}Step 3: Create OpenAI Configuration for Oiiro${NC}"
  echo "POST ${API_URL}/model-providers/configs"
  echo ""

  CREATE_DATA=$(cat <<EOF
{
  "provider_name": "openai",
  "provider_type": "llm",
  "display_name": "Oiiro OpenAI Production",
  "api_key": "${OPENAI_API_KEY}",
  "config": {
    "organization_id": "org-oiiro",
    "default_model": "gpt-4-turbo",
    "max_tokens": 4096,
    "temperature": 0.7
  },
  "is_active": true,
  "is_default": true,
  "project_id": null
}
EOF
)

  echo "Request Body (API key masked for security):"
  echo "${CREATE_DATA}" | sed 's/"api_key": ".*"/"api_key": "sk-proj-***masked***"/' | python3 -m json.tool
  echo ""

  CREATE_RESPONSE=$(curl -s -X POST \
    "${API_URL}/model-providers/configs" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "${CREATE_DATA}")

  echo "Response:"
  echo "${CREATE_RESPONSE}" | python3 -m json.tool
  echo ""

  # Extract new config ID
  NEW_CONFIG_ID=$(echo "${CREATE_RESPONSE}" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null || echo "")

  if [ -n "${NEW_CONFIG_ID}" ]; then
    echo -e "${GREEN}✓ Configuration created successfully: ${NEW_CONFIG_ID}${NC}"
    CONFIG_ID="${NEW_CONFIG_ID}"
  else
    echo -e "${YELLOW}⚠ Failed to create configuration. Response:${NC}"
    echo "${CREATE_RESPONSE}"
    exit 1
  fi
fi

# Step 5: Test the provider configuration
echo -e "${YELLOW}Step 5: Test Provider Connection${NC}"
echo "POST ${API_URL}/model-providers/configs/${CONFIG_ID}/test"
echo ""

TEST_DATA='{"test_model": "gpt-3.5-turbo"}'
echo "Request Body:"
echo "${TEST_DATA}" | python3 -m json.tool
echo ""

TEST_RESPONSE=$(curl -s -X POST \
  "${API_URL}/model-providers/configs/${CONFIG_ID}/test" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "${TEST_DATA}")

echo "Response:"
echo "${TEST_RESPONSE}" | python3 -m json.tool
echo ""

# Check if test was successful
TEST_SUCCESS=$(echo "${TEST_RESPONSE}" | python3 -c "import sys, json; data = json.load(sys.stdin); print('true' if data.get('success') else 'false')" 2>/dev/null || echo "false")

if [ "${TEST_SUCCESS}" = "true" ]; then
  echo -e "${GREEN}✓ Provider connection test successful${NC}"
else
  echo -e "${YELLOW}⚠ Provider connection test failed (may require valid API key)${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Test Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Summary:"
echo -e "  • Configuration ID: ${CONFIG_ID}"
echo -e "  • Provider: OpenAI"
echo -e "  • Organization: Oiiro"
echo -e "  • API endpoint: ${API_URL}/model-providers"
echo ""
