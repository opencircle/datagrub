#!/bin/bash

###############################################################################
# ⚠️  DEPRECATED SCRIPT
#
# This script is deprecated and will be removed in a future version.
# Please use the new startup scripts in the ui-tier/ directory.
###############################################################################

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo ""
echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║                                                                ║${NC}"
echo -e "${RED}║                  ⚠️  DEPRECATED SCRIPT ⚠️                      ║${NC}"
echo -e "${RED}║                                                                ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}This script is deprecated and will be removed in a future version.${NC}"
echo ""
echo -e "${BLUE}Please use the new startup scripts in the ui-tier/ directory:${NC}"
echo ""
echo -e "${GREEN}  cd ui-tier${NC}"
echo ""
echo -e "${GREEN}  # Start all MFE applications${NC}"
echo -e "${GREEN}  ./start-all-mfes.sh${NC}"
echo ""
echo -e "${GREEN}  # Stop all MFE applications${NC}"
echo -e "${GREEN}  ./stop-all-mfes.sh${NC}"
echo ""
echo -e "${GREEN}  # Run integration tests${NC}"
echo -e "${GREEN}  ./test-integration.sh${NC}"
echo ""
echo -e "${BLUE}For more information, see:${NC}"
echo "  - UI_DEPLOYMENT_GUIDE.md"
echo "  - UI_DEPLOYMENT_COMPLETION.md"
echo ""
echo -e "${YELLOW}The new scripts provide:${NC}"
echo "  ✓ Individual log files for each MFE"
echo "  ✓ Background process management with PID tracking"
echo "  ✓ Health checks before starting"
echo "  ✓ Better debugging and troubleshooting"
echo "  ✓ Graceful shutdown"
echo ""

# Ask if user wants to run the new script
read -p "Would you like to run the new startup script now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd ui-tier
    ./start-all-mfes.sh
else
    echo "Exiting. To start manually, run: cd ui-tier && ./start-all-mfes.sh"
fi
