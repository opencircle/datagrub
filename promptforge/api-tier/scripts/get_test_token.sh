#!/bin/bash
# Get Test Token - Generate authentication token for API testing
# Usage: ./get_test_token.sh [email] [password]
#
# Default credentials: demo@promptforge.ai / demo123

set -euo pipefail

# Configuration
API_BASE="${API_BASE:-http://localhost:8000}"
EMAIL="${1:-demo@promptforge.ai}"
PASSWORD="${2:-demo123}"

echo "🔐 PromptForge Test Token Generator"
echo "===================================="
echo ""
echo "API Base: $API_BASE"
echo "Email: $EMAIL"
echo ""

# Check if API is running
echo "🔍 Checking API availability..."
if ! curl -s -f "$API_BASE/docs" > /dev/null 2>&1; then
    echo "❌ API not available at $API_BASE"
    echo ""
    echo "💡 Start the API with:"
    echo "   cd /Users/rohitiyer/datagrub/promptforge/api-tier"
    echo "   docker-compose up -d"
    echo "   # or"
    echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    exit 1
fi
echo "✅ API is running"
echo ""

# Login and extract token
echo "🔑 Logging in..."
TOKEN_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "⚠️  jq not installed - install with: brew install jq"
    echo ""
    echo "Raw response:"
    echo "$TOKEN_RESPONSE"
    exit 0
fi

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')
REFRESH_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.refresh_token')

if [ "$ACCESS_TOKEN" = "null" ] || [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Failed to get token"
    echo ""
    echo "Response:"
    echo "$TOKEN_RESPONSE" | jq .
    echo ""
    echo "💡 Common issues:"
    echo "   - User doesn't exist (run pytest to create fixtures)"
    echo "   - Wrong password"
    echo "   - Database not initialized"
    exit 1
fi

echo "✅ Access Token obtained"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 ACCESS TOKEN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$ACCESS_TOKEN"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 EXPORT TO ENVIRONMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "export TOKEN='$ACCESS_TOKEN'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 CURL EXAMPLES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "# List projects"
echo "curl -X GET $API_BASE/api/v1/projects \\"
echo "  -H 'Authorization: Bearer $ACCESS_TOKEN'"
echo ""
echo "# Create project"
echo "curl -X POST $API_BASE/api/v1/projects \\"
echo "  -H 'Authorization: Bearer $ACCESS_TOKEN' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"name\":\"Test Project\",\"description\":\"Created via curl\"}'"
echo ""
echo "# Get user profile"
echo "curl -X GET $API_BASE/api/v1/users/me \\"
echo "  -H 'Authorization: Bearer $ACCESS_TOKEN'"
echo ""

# Decode token to show expiration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 TOKEN DETAILS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TOKEN_PAYLOAD=$(echo "$ACCESS_TOKEN" | cut -d. -f2)
# Add padding if needed for base64
TOKEN_PAYLOAD="${TOKEN_PAYLOAD}$(printf '=%.0s' {1..4})"
echo "$TOKEN_PAYLOAD" | base64 -d 2>/dev/null | jq . || echo "Unable to decode token payload"
echo ""

# Test the token
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 TESTING TOKEN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing GET /api/v1/projects..."
TEST_RESPONSE=$(curl -s -X GET "$API_BASE/api/v1/projects" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$TEST_RESPONSE" | jq . > /dev/null 2>&1; then
    echo "✅ Token is valid!"
    echo ""
    echo "Response:"
    echo "$TEST_RESPONSE" | jq .
else
    echo "❌ Token validation failed"
    echo "Response: $TEST_RESPONSE"
fi
echo ""

# Save to file for reuse
TOKEN_FILE="${TOKEN_FILE:-.test_token}"
echo "$ACCESS_TOKEN" > "$TOKEN_FILE"
echo "💾 Token saved to: $TOKEN_FILE"
echo ""
echo "💡 Use saved token:"
echo "   export TOKEN=\$(cat $TOKEN_FILE)"
echo "   curl -X GET $API_BASE/api/v1/projects -H \"Authorization: Bearer \$TOKEN\""
