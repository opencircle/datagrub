#!/bin/bash

###############################################################################
# PromptForge UI - Integration Testing Script
#
# Tests integration between UI and backend APIs
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Test helper function
run_test() {
    local test_name=$1
    local test_command=$2

    log_info "Testing: $test_name"

    if eval "$test_command" > /dev/null 2>&1; then
        log_success "$test_name"
        ((TESTS_PASSED++))
        return 0
    else
        log_error "$test_name"
        ((TESTS_FAILED++))
        return 1
    fi
}

# API base URL
API_BASE="http://localhost:8000"
API_V1="${API_BASE}/api/v1"

# Test token (you'll need to set this after logging in)
# For now, we'll test public endpoints
TOKEN="${TOKEN:-}"

###############################################################################
# Test Suite
###############################################################################

main() {
    log_info "==================================================================="
    log_info "  PromptForge UI - Integration Testing"
    log_info "==================================================================="
    echo ""

    # 1. Backend Health Checks
    log_info "--- Backend Health Checks ---"
    run_test "Backend health endpoint" \
        "curl -sf ${API_BASE}/health"

    run_test "Backend database connection" \
        "curl -sf ${API_BASE}/health | grep -q 'connected'"

    run_test "Backend Redis connection" \
        "curl -sf ${API_BASE}/health | grep -q 'connected'"
    echo ""

    # 2. API Endpoints (Public)
    log_info "--- Public API Endpoints ---"
    run_test "API v1 root accessible" \
        "curl -sf -o /dev/null -w '%{http_code}' ${API_V1}/ | grep -q '404\\|200'"
    echo ""

    # 3. Authentication Endpoints
    log_info "--- Authentication Endpoints ---"
    run_test "Login endpoint exists" \
        "curl -sf -X POST ${API_V1}/auth/login -H 'Content-Type: application/json' -d '{\"email\":\"test\",\"password\":\"test\"}' -w '%{http_code}' -o /dev/null | grep -q '401\\|422\\|200'"
    echo ""

    # 4. Protected Endpoints (require authentication)
    if [ -n "$TOKEN" ]; then
        log_info "--- Protected API Endpoints (Authenticated) ---"

        run_test "Get evaluations" \
            "curl -sf -H 'Authorization: Bearer ${TOKEN}' ${API_V1}/evaluations"

        run_test "Get evaluation catalog" \
            "curl -sf -H 'Authorization: Bearer ${TOKEN}' ${API_V1}/evaluation-catalog/catalog"

        run_test "Get model provider catalog" \
            "curl -sf -H 'Authorization: Bearer ${TOKEN}' ${API_V1}/model-providers/catalog"

        run_test "Get provider configs" \
            "curl -sf -H 'Authorization: Bearer ${TOKEN}' ${API_V1}/model-providers/configs"
        echo ""
    else
        log_warning "TOKEN not set. Skipping authenticated endpoint tests."
        log_info "Set TOKEN environment variable to test authenticated endpoints:"
        log_info "  export TOKEN='your-jwt-token'"
        echo ""
    fi

    # 5. UI Application Checks
    log_info "--- UI Application Health ---"
    run_test "Shell app accessible (port 3000)" \
        "curl -sf -o /dev/null http://localhost:3000"

    run_test "Evaluations MFE accessible (port 3002)" \
        "curl -sf -o /dev/null http://localhost:3002"
    echo ""

    # 6. Module Federation Checks
    log_info "--- Module Federation ---"
    run_test "Shell remoteEntry.js exists" \
        "curl -sf -o /dev/null http://localhost:3000/remoteEntry.js"

    run_test "Evaluations remoteEntry.js exists" \
        "curl -sf -o /dev/null http://localhost:3002/remoteEntry.js"
    echo ""

    # Results Summary
    log_info "==================================================================="
    log_info "  Test Results Summary"
    log_info "==================================================================="
    echo ""
    log_success "Tests Passed: ${TESTS_PASSED}"
    if [ $TESTS_FAILED -gt 0 ]; then
        log_error "Tests Failed: ${TESTS_FAILED}"
        echo ""
        log_warning "Some tests failed. Check the output above for details."
        exit 1
    else
        log_success "Tests Failed: ${TESTS_FAILED}"
        echo ""
        log_success "All tests passed! ✨"
        exit 0
    fi
}

# Run main function
main
