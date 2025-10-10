#!/bin/bash
# Test evaluation execution via playground API

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTk2OTc5OTksInN1YiI6ImVhNGFiMTg2LWMzMWUtNDA1OS05OTZlLTI5ZWE5OWVhNmM0NyIsInR5cGUiOiJhY2Nlc3MifQ.t_gJA9zyUAplq1Th6o1DC5goCDAt8sitt6EGPCOanno"

echo "Testing playground execution with evaluation..."

curl -X POST http://localhost:8000/api/v1/playground/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d @- <<'EOF' | jq .
{
  "prompt": "What is 2+2?",
  "system_prompt": "You are a helpful math assistant.",
  "model": "gpt-4",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 0.9
  },
  "evaluation_ids": ["9fee921e-8000-4605-9dce-807db94d4f3d"]
}
EOF
