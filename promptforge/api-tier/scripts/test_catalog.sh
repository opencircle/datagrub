#!/bin/bash
# Test evaluation catalog endpoint

echo "Testing evaluation catalog endpoint..."
echo ""

# Count evaluations by source
echo "=== Evaluations by Source ==="
curl -s "http://localhost:8000/api/v1/evaluation-catalog/catalog?is_active=true" | \
  jq '[group_by(.source) | .[] | {source: .[0].source, count: length}]'

echo ""
echo "=== Total Count ==="
curl -s "http://localhost:8000/api/v1/evaluation-catalog/catalog?is_active=true" | \
  jq 'length'

echo ""
echo "=== Sample PromptForge Evaluation ==="
curl -s "http://localhost:8000/api/v1/evaluation-catalog/catalog?source=PROMPTFORGE&is_active=true" | \
  jq '.[0]'

echo ""
echo "=== Sample Vendor Evaluation ==="
curl -s "http://localhost:8000/api/v1/evaluation-catalog/catalog?source=VENDOR&is_active=true" | \
  jq '.[0]'
