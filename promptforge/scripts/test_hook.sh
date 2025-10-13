#!/bin/bash
# Test script to verify hook invocation
# This should trigger the Script Validator

echo "Hello from test hook script"
echo "This script tests the post-tool-use hook"

# This should be flagged: missing error handling
curl http://localhost:8000/api/v1/projects

exit 0
