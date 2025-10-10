#!/bin/bash
#
# Vendor Library Installation Script for PromptForge Evaluation Abstraction Layer
#
# This script installs all vendor evaluation libraries required for the full
# evaluation catalog (93 evaluations across 5 vendors).
#
# Usage:
#   ./install_vendor_libraries.sh [--skip-verification]
#
# Exit codes:
#   0 - All libraries installed successfully
#   1 - Installation failed for one or more libraries
#   2 - Verification failed
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/vendor_install.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1" | tee -a "$LOG_FILE"
}

# Initialize log file
echo "=== Vendor Library Installation Log ===" > "$LOG_FILE"
echo "Started: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

log_info "Installing vendor evaluation libraries for PromptForge..."
echo ""

# Parse arguments
SKIP_VERIFICATION=false
if [[ "$1" == "--skip-verification" ]]; then
    SKIP_VERIFICATION=true
fi

#
# Phase 1: Core Vendor Evaluation Frameworks
#
log_info "Phase 1: Installing core vendor evaluation frameworks"
echo ""

# DeepEval (15 evaluations)
log_info "Installing DeepEval >= 0.21.0..."
if pip install --no-cache-dir 'deepeval>=0.21.0' >> "$LOG_FILE" 2>&1; then
    DEEPEVAL_VERSION=$(pip show deepeval | grep Version | awk '{print $2}')
    log_success "DeepEval $DEEPEVAL_VERSION installed"
else
    log_error "DeepEval installation failed"
    exit 1
fi

# Ragas (23 evaluations)
log_info "Installing Ragas >= 0.1.0..."
if pip install --no-cache-dir 'ragas>=0.1.0' >> "$LOG_FILE" 2>&1; then
    RAGAS_VERSION=$(pip show ragas | grep Version | awk '{print $2}')
    log_success "Ragas $RAGAS_VERSION installed"
else
    log_error "Ragas installation failed"
    exit 1
fi

# MLflow (18 evaluations)
log_info "Installing MLflow >= 2.10.0..."
if pip install --no-cache-dir 'mlflow>=2.10.0' >> "$LOG_FILE" 2>&1; then
    MLFLOW_VERSION=$(pip show mlflow | grep Version | awk '{print $2}')
    log_success "MLflow $MLFLOW_VERSION installed"
else
    log_error "MLflow installation failed"
    exit 1
fi

# Deepchecks LLM (15 evaluations)
log_info "Installing Deepchecks LLM Client >= 0.1.0..."
if pip install --no-cache-dir 'deepchecks-llm-client>=0.1.0' >> "$LOG_FILE" 2>&1; then
    DEEPCHECKS_VERSION=$(pip show deepchecks-llm-client | grep Version | awk '{print $2}')
    log_success "Deepchecks LLM Client $DEEPCHECKS_VERSION installed"
else
    log_warning "Deepchecks LLM Client installation failed (optional)"
fi

# Arize Phoenix (16 evaluations)
log_info "Installing Arize Phoenix >= 3.0.0..."
if pip install --no-cache-dir 'arize-phoenix>=3.0.0' 'arize-phoenix-evals>=0.1.0' >> "$LOG_FILE" 2>&1; then
    PHOENIX_VERSION=$(pip show arize-phoenix | grep Version | awk '{print $2}')
    log_success "Arize Phoenix $PHOENIX_VERSION installed"
else
    log_warning "Arize Phoenix installation failed (optional)"
fi

echo ""

#
# Phase 2: Required Dependencies for Vendor Libraries
#
log_info "Phase 2: Installing required dependencies"
echo ""

# Datasets (required by Ragas and DeepEval)
log_info "Installing datasets >= 2.16.0..."
if pip install --no-cache-dir 'datasets>=2.16.0' >> "$LOG_FILE" 2>&1; then
    log_success "datasets installed"
else
    log_error "datasets installation failed"
    exit 1
fi

# Nest-asyncio (async compatibility)
log_info "Installing nest-asyncio >= 1.6.0..."
if pip install --no-cache-dir 'nest-asyncio>=1.6.0' >> "$LOG_FILE" 2>&1; then
    log_success "nest-asyncio installed"
else
    log_error "nest-asyncio installation failed"
    exit 1
fi

echo ""

#
# Phase 3: MLflow Metric Dependencies
#
log_info "Phase 3: Installing MLflow metric dependencies"
echo ""

# Textstat (readability metrics)
log_info "Installing textstat >= 0.7.0..."
if pip install --no-cache-dir 'textstat>=0.7.0' >> "$LOG_FILE" 2>&1; then
    log_success "textstat installed"
else
    log_warning "textstat installation failed (MLflow readability metrics may not work)"
fi

# ROUGE Score (text similarity)
log_info "Installing rouge-score >= 0.1.0..."
if pip install --no-cache-dir 'rouge-score>=0.1.0' >> "$LOG_FILE" 2>&1; then
    log_success "rouge-score installed"
else
    log_warning "rouge-score installation failed (MLflow ROUGE metrics may not work)"
fi

# Tiktoken (token counting)
log_info "Installing tiktoken >= 0.5.0..."
if pip install --no-cache-dir 'tiktoken>=0.5.0' >> "$LOG_FILE" 2>&1; then
    log_success "tiktoken installed"
else
    log_warning "tiktoken installation failed (token metrics may not work)"
fi

# NLTK (natural language processing)
log_info "Installing nltk >= 3.8.0..."
if pip install --no-cache-dir 'nltk>=3.8.0' >> "$LOG_FILE" 2>&1; then
    log_success "nltk installed"
else
    log_warning "nltk installation failed (NLP metrics may not work)"
fi

# SQLParse (SQL parsing)
log_info "Installing sqlparse >= 0.4.0..."
if pip install --no-cache-dir 'sqlparse>=0.4.0' >> "$LOG_FILE" 2>&1; then
    log_success "sqlparse installed"
else
    log_warning "sqlparse installation failed (SQL metrics may not work)"
fi

echo ""

#
# Phase 4: Download NLTK Data (if NLTK installed)
#
log_info "Phase 4: Downloading NLTK data packages"
echo ""

python3 << 'EOF'
import sys
try:
    import nltk
    print("Downloading NLTK punkt tokenizer...")
    nltk.download('punkt', quiet=True)
    print("Downloading NLTK stopwords...")
    nltk.download('stopwords', quiet=True)
    print("Downloading NLTK wordnet...")
    nltk.download('wordnet', quiet=True)
    print("✓ NLTK data packages downloaded")
except Exception as e:
    print(f"⚠ NLTK data download failed: {e}", file=sys.stderr)
    sys.exit(0)  # Non-fatal
EOF

if [ $? -eq 0 ]; then
    log_success "NLTK data packages downloaded"
else
    log_warning "NLTK data download failed (some metrics may not work)"
fi

echo ""

#
# Phase 5: Verification
#
if [ "$SKIP_VERIFICATION" = false ]; then
    log_info "Phase 5: Verifying installations"
    echo ""

    python3 << 'EOF'
import sys

verification_results = {
    "required": {},
    "optional": {}
}

# Required libraries
required_libs = [
    ("deepeval", "DeepEval"),
    ("ragas", "Ragas"),
    ("mlflow", "MLflow"),
    ("datasets", "Datasets"),
    ("nest_asyncio", "nest-asyncio"),
]

for module_name, display_name in required_libs:
    try:
        module = __import__(module_name)
        version = getattr(module, "__version__", "unknown")
        verification_results["required"][display_name] = {"status": "OK", "version": version}
        print(f"✓ {display_name}: {version}")
    except ImportError as e:
        verification_results["required"][display_name] = {"status": "FAILED", "error": str(e)}
        print(f"✗ {display_name}: Import failed - {e}")

print()

# Optional libraries
optional_libs = [
    ("deepchecks_client", "Deepchecks LLM"),
    ("phoenix", "Arize Phoenix"),
    ("textstat", "textstat"),
    ("rouge_score", "rouge-score"),
    ("tiktoken", "tiktoken"),
    ("nltk", "NLTK"),
    ("sqlparse", "sqlparse"),
]

for module_name, display_name in optional_libs:
    try:
        module = __import__(module_name)
        version = getattr(module, "__version__", "unknown")
        verification_results["optional"][display_name] = {"status": "OK", "version": version}
        print(f"✓ {display_name}: {version}")
    except ImportError as e:
        verification_results["optional"][display_name] = {"status": "MISSING", "error": str(e)}
        print(f"⚠ {display_name}: Not available - {e}")

print()

# Check if all required libraries are installed
failed_required = [name for name, result in verification_results["required"].items() if result["status"] != "OK"]

if failed_required:
    print(f"✗ Verification failed: {len(failed_required)} required libraries missing")
    for lib in failed_required:
        print(f"  - {lib}")
    sys.exit(1)
else:
    required_count = len(verification_results["required"])
    optional_count = sum(1 for r in verification_results["optional"].values() if r["status"] == "OK")
    total_optional = len(verification_results["optional"])
    print(f"✓ Verification passed: {required_count}/{required_count} required, {optional_count}/{total_optional} optional")
    sys.exit(0)
EOF

    VERIFICATION_EXIT_CODE=$?

    if [ $VERIFICATION_EXIT_CODE -eq 0 ]; then
        log_success "All required libraries verified successfully"
    else
        log_error "Verification failed - some required libraries are missing"
        exit 2
    fi
else
    log_warning "Verification skipped"
fi

echo ""
log_success "Vendor library installation complete!"
echo ""
echo "Summary:"
echo "  - DeepEval: 15 evaluations"
echo "  - Ragas: 23 evaluations"
echo "  - MLflow: 18 evaluations"
echo "  - Deepchecks: 15 evaluations (optional)"
echo "  - Arize Phoenix: 16 evaluations (optional)"
echo "  - Total: 87 vendor evaluations available"
echo ""
echo "Log file: $LOG_FILE"
echo ""
echo "Completed: $(date)" >> "$LOG_FILE"

exit 0
