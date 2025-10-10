#!/bin/bash
# Test evaluation catalog endpoint with authentication

# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@promptforge.ai","password":"demo123"}' | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "Failed to get auth token"
  exit 1
fi

echo "Got auth token: ${TOKEN:0:20}..."
echo ""

# Test catalog
echo "=== Total Evaluations ==="
curl -s "http://localhost:8000/api/v1/evaluation-catalog/catalog?is_active=true" \
  -H "Authorization: Bearer $TOKEN" | jq 'length'

echo ""
echo "=== Evaluations by Source ==="
curl -s "http://localhost:8000/api/v1/evaluation-catalog/catalog?is_active=true" \
  -H "Authorization: Bearer $TOKEN" | jq '[group_by(.source) | .[] | {source: .[0].source, count: length}]'

echo ""
echo "=== PromptForge Evaluations ==="
curl -s "http://localhost:8000/api/v1/evaluation-catalog/catalog?source=PROMPTFORGE&is_active=true" \
  -H "Authorization: Bearer $TOKEN" | jq '[.[] | {name: .name, adapter_evaluation_id: .adapter_evaluation_id}]'

echo ""
echo "=== Sample Vendor Evaluation (DeepEval) ==="
curl -s "http://localhost:8000/api/v1/evaluation-catalog/catalog?source=VENDOR&is_active=true" \
  -H "Authorization: Bearer $TOKEN" | jq '.[0] | {name: .name, source: .source, category: .category, adapter_evaluation_id: .adapter_evaluation_id}'
