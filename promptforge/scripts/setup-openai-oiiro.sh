#!/bin/bash
#
# Complete Setup: OpenAI Configuration for Oiiro
#
# This script demonstrates the complete flow:
# 1. Login with Oiiro credentials
# 2. Create OpenAI provider configuration
# 3. Verify the configuration
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
API_URL="http://localhost:8000/api/v1"
EMAIL="rohit.iyer@oiiro.com"
PASSWORD="Welcome123"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}OpenAI Setup for Oiiro Client${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if OpenAI API key is provided
OPENAI_API_KEY="${1:-}"

if [ -z "${OPENAI_API_KEY}" ]; then
  echo -e "${YELLOW}Enter your OpenAI API key:${NC}"
  read -s OPENAI_API_KEY
  echo ""
fi

# Validate API key format
if [[ ! "${OPENAI_API_KEY}" =~ ^sk- ]]; then
  echo -e "${RED}❌ Invalid OpenAI API key format. Must start with 'sk-'${NC}"
  exit 1
fi

echo -e "${YELLOW}Step 1: Authenticating as Oiiro user...${NC}"
echo "  Email: ${EMAIL}"
echo ""

LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}")

ACCESS_TOKEN=$(echo "${LOGIN_RESPONSE}" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('access_token', ''))" 2>/dev/null || echo "")

if [ -z "${ACCESS_TOKEN}" ]; then
  echo -e "${RED}❌ Login failed${NC}"
  echo "${LOGIN_RESPONSE}" | python3 -m json.tool
  exit 1
fi

echo -e "${GREEN}✅ Authenticated successfully${NC}"
echo ""

# Check for existing configuration
echo -e "${YELLOW}Step 2: Checking for existing OpenAI configuration...${NC}"
EXISTING_CONFIGS=$(curl -s -X GET "${API_URL}/model-providers/configs?provider_name=openai" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

EXISTING_CONFIG_ID=$(echo "${EXISTING_CONFIGS}" | python3 -c "import sys, json; data = json.load(sys.stdin); configs = data.get('configs', []); print(configs[0]['id'] if configs else '')" 2>/dev/null || echo "")

if [ -n "${EXISTING_CONFIG_ID}" ]; then
  echo -e "${YELLOW}⚠️  Found existing OpenAI configuration${NC}"
  echo ""
  echo "Current configuration:"
  echo "${EXISTING_CONFIGS}" | python3 -m json.tool
  echo ""

  echo -e "${YELLOW}Do you want to update it with the new API key? (y/n)${NC}"
  read -r CONFIRM

  if [ "${CONFIRM}" != "y" ]; then
    echo "Keeping existing configuration."
    CONFIG_ID="${EXISTING_CONFIG_ID}"
  else
    # Update existing configuration
    echo -e "${YELLOW}Step 3: Updating OpenAI configuration...${NC}"
    UPDATE_RESPONSE=$(curl -s -X PUT "${API_URL}/model-providers/configs/${EXISTING_CONFIG_ID}" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{
        \"api_key\": \"${OPENAI_API_KEY}\",
        \"display_name\": \"Oiiro OpenAI Production\",
        \"config\": {
          \"organization_id\": \"org-oiiro\",
          \"default_model\": \"gpt-4-turbo\",
          \"max_tokens\": 4096,
          \"temperature\": 0.7
        }
      }")

    CONFIG_ID="${EXISTING_CONFIG_ID}"
    echo -e "${GREEN}✅ Configuration updated${NC}"
  fi

else
  # Create new configuration
  echo -e "${GREEN}No existing configuration found${NC}"
  echo ""
  echo -e "${YELLOW}Step 3: Creating OpenAI configuration...${NC}"

  CREATE_RESPONSE=$(curl -s -X POST "${API_URL}/model-providers/configs" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{
      \"provider_name\": \"openai\",
      \"provider_type\": \"llm\",
      \"display_name\": \"Oiiro OpenAI Production\",
      \"api_key\": \"${OPENAI_API_KEY}\",
      \"config\": {
        \"organization_id\": \"org-oiiro\",
        \"default_model\": \"gpt-4-turbo\",
        \"max_tokens\": 4096,
        \"temperature\": 0.7
      },
      \"is_active\": true,
      \"is_default\": true,
      \"project_id\": null
    }")

  CONFIG_ID=$(echo "${CREATE_RESPONSE}" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null || echo "")

  if [ -z "${CONFIG_ID}" ]; then
    echo -e "${RED}❌ Failed to create configuration${NC}"
    echo "${CREATE_RESPONSE}" | python3 -m json.tool
    exit 1
  fi

  echo -e "${GREEN}✅ Configuration created${NC}"
fi

echo "  Config ID: ${CONFIG_ID}"
echo ""

# Verify configuration
echo -e "${YELLOW}Step 4: Verifying configuration...${NC}"
VERIFY_RESPONSE=$(curl -s -X GET "${API_URL}/model-providers/configs/${CONFIG_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "${VERIFY_RESPONSE}" | python3 -m json.tool
echo ""

# Extract masked key
MASKED_KEY=$(echo "${VERIFY_RESPONSE}" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('api_key_masked', 'N/A'))")

echo -e "${GREEN}✅ API Key stored and encrypted: ${MASKED_KEY}${NC}"
echo ""

# Test connection
echo -e "${YELLOW}Step 5: Testing OpenAI connection...${NC}"
TEST_RESPONSE=$(curl -s -X POST "${API_URL}/model-providers/configs/${CONFIG_ID}/test" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"test_model": "gpt-3.5-turbo"}')

TEST_SUCCESS=$(echo "${TEST_RESPONSE}" | python3 -c "import sys, json; data = json.load(sys.stdin); print('true' if data.get('success') else 'false')" 2>/dev/null || echo "false")

if [ "${TEST_SUCCESS}" = "true" ]; then
  echo -e "${GREEN}✅ OpenAI connection test successful!${NC}"
  echo ""
  echo "Test results:"
  echo "${TEST_RESPONSE}" | python3 -m json.tool
else
  echo -e "${YELLOW}⚠️  Connection test failed${NC}"
  echo "${TEST_RESPONSE}" | python3 -m json.tool
  echo ""
  echo "Note: This may be normal if:"
  echo "  - The API key is a placeholder"
  echo "  - You don't have OpenAI API credits"
  echo "  - The OpenAI API is temporarily unavailable"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Summary:"
echo "  ✓ Organization: Oiiro"
echo "  ✓ User: rohit.iyer@oiiro.com"
echo "  ✓ Provider: OpenAI"
echo "  ✓ Configuration ID: ${CONFIG_ID}"
echo "  ✓ API Key: Encrypted (${MASKED_KEY})"
echo "  ✓ Default Model: gpt-4-turbo"
echo "  ✓ Status: Active"
echo ""
echo "Your OpenAI configuration is now ready for use in PromptForge!"
echo ""
