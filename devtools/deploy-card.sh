#!/bin/bash

# Logger Manager Card Deployment Script
# Copies the custom card to Home Assistant www directory

# Configuration
HA_HOST="homeassistant.local"
LOCAL_CARD_FILE="custom_components/logger_manager/frontend/ha-logger-multiselect-card.js"
REMOTE_WWW_DIR="/config/www"
CARD_FILENAME="ha-logger-multiselect-card.js"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Deploying Logger Manager Card to Home Assistant...${NC}"

# Check if local file exists
if [ ! -f "$LOCAL_CARD_FILE" ]; then
    echo -e "${RED}Error: Local card file not found at $LOCAL_CARD_FILE${NC}"
    exit 1
fi

# Copy file to HA via /tmp then move to final location
echo "Copying $LOCAL_CARD_FILE to $HA_HOST via /tmp..."
if cat "$LOCAL_CARD_FILE" | ssh "$HA_HOST" "cat > /tmp/$CARD_FILENAME && sudo rm -f $REMOTE_WWW_DIR/$CARD_FILENAME && sudo mv /tmp/$CARD_FILENAME $REMOTE_WWW_DIR/$CARD_FILENAME"; then
    echo -e "${GREEN}✓ Card deployed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Refresh your browser (Ctrl+F5 or Cmd+Shift+R)"
    echo "2. Test the card in your dashboard"
    echo ""
    echo "Resource URL: /local/$CARD_FILENAME"
else
    echo -e "${RED}✗ Deployment failed!${NC}"
    echo "Check your SSH connection to $HA_HOST or file permissions"
    exit 1
fi