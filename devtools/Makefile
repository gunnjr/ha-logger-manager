# Makefile for deploying Home Assistant Logger Manager

# === CONFIGURATION ===
HA_HOST=homeassistant.local
HA_USER=hassio
HA_HTTP_PORT=8123

# Path to project root (Makefile is in devtools/)
ROOT_DIR=..

# Main UI deployment (legacy/manual install)
UI_SRC=$(ROOT_DIR)/custom_components/logger_manager/frontend/ha-logger-multiselect-card.js
UI_TMP=ha-logger-multiselect-card.js
UI_DST=/config/www/logger_manager/ha-logger-multiselect-card.js

# HACS-style UI deployment
HACS_UI_DST=/config/www/community/logger_manager/ha-logger-multiselect-card.js

BACKEND_SRC=$(ROOT_DIR)/custom_components/logger_manager/__init__.py \
            $(ROOT_DIR)/custom_components/logger_manager/sensor.py \
            $(ROOT_DIR)/custom_components/logger_manager/config_flow.py \
            $(ROOT_DIR)/custom_components/logger_manager/const.py \
            $(ROOT_DIR)/custom_components/logger_manager/manifest.json \
            $(ROOT_DIR)/custom_components/logger_manager/strings.json \
            $(ROOT_DIR)/custom_components/logger_manager/services.yaml
BACKEND_DST=/config/custom_components/logger_manager/

.PHONY: ui ui-hacs backend all all-legacy all-ha-install-ready clean status help

# Show help by default
help:
	@echo "Logger Manager Deployment Targets:"
	@echo "  make all             - Deploy complete integration (default)"
	@echo "  make all-ha-install-ready - Deploy complete integration (explicit)"
	@echo "  make all-legacy      - Deploy UI and backend to legacy paths"
	@echo "  make backend         - Deploy backend Python files to HA"
	@echo "  make ui              - Deploy UI card (legacy path)"
	@echo "  make ui-hacs         - Deploy UI card (HACS path)"
	@echo "  make clean           - Remove integration from all install paths"
	@echo "  make status          - Show what would be deployed"
	@echo ""
	@echo "After deployment, restart HA via:"
	@echo "  Settings → System → Restart (or use HA UI/CLI)"
	@echo ""
	@echo "Configuration:"
	@echo "  HA_HOST: $(HA_HOST)"
	@echo "  HA_USER: $(HA_USER)"

# Show what files will be deployed
status:
	@echo "=== Backend Files to Deploy ==="
	@for file in $(BACKEND_SRC); do \
	  if [ -f "$$file" ]; then \
	    echo "  ✓ $$file"; \
	  else \
	    echo "  ✗ $$file (MISSING)"; \
	  fi \
	done
	@echo ""
	@echo "=== UI Files to Deploy ==="
	@if [ -f "$(UI_SRC)" ]; then \
	  echo "  ✓ $(UI_SRC)"; \
	else \
	  echo "  ✗ $(UI_SRC) (MISSING)"; \
	fi
	@echo ""
	@echo "Target: $(HA_USER)@$(HA_HOST):$(BACKEND_DST)"

ui:
	cat $(UI_SRC) | ssh $(HA_USER)@$(HA_HOST) "cat > /tmp/$(UI_TMP) && sudo mkdir -p $$(dirname $(UI_DST)) && sudo rm -f $(UI_DST) && sudo mv /tmp/$(UI_TMP) $(UI_DST)"

# Deploy frontend JS to HACS community path
.PHONY: ui-hacs
ui-hacs:
	cat $(UI_SRC) | ssh $(HA_USER)@$(HA_HOST) "cat > /tmp/$(UI_TMP) && sudo mkdir -p $$(dirname $(HACS_UI_DST)) && sudo rm -f $(HACS_UI_DST) && sudo mv /tmp/$(UI_TMP) $(HACS_UI_DST)"
backend:
	@echo "Creating backend directory on Home Assistant..."
	@ssh $(HA_USER)@$(HA_HOST) "sudo mkdir -p $(BACKEND_DST)"
	@echo "Deploying backend files to Home Assistant..."
	for file in $(BACKEND_SRC); do \
	  fname=$$(basename $$file); \
	  cat $$file | ssh $(HA_USER)@$(HA_HOST) "cat > /tmp/$$fname && sudo rm -f $(BACKEND_DST)/$$fname && sudo mv /tmp/$$fname $(BACKEND_DST)/$$fname"; \
	done

# Legacy deployment (manual install paths)
all-legacy: ui backend

# Deploy complete integration to custom_components (mimics HACS installation)
all-ha-install-ready:
	@echo "Deploying complete integration to Home Assistant..."
	@ssh $(HA_USER)@$(HA_HOST) "sudo mkdir -p $(BACKEND_DST)"
	@ssh $(HA_USER)@$(HA_HOST) "sudo mkdir -p $(BACKEND_DST)/translations"
	@ssh $(HA_USER)@$(HA_HOST) "sudo mkdir -p $(BACKEND_DST)/frontend"
	@echo "  → Backend Python files..."
	@for file in $(BACKEND_SRC); do \
	  fname=$$(basename $$file); \
	  cat $$file | ssh $(HA_USER)@$(HA_HOST) "cat > /tmp/$$fname && sudo mv /tmp/$$fname $(BACKEND_DST)/$$fname"; \
	done
	@echo "  → Translations..."
	@cat $(ROOT_DIR)/custom_components/logger_manager/translations/en.json | ssh $(HA_USER)@$(HA_HOST) "cat > /tmp/en.json && sudo mv /tmp/en.json $(BACKEND_DST)/translations/en.json"
	@echo "  → Icons..."
	@cat $(ROOT_DIR)/custom_components/logger_manager/icon.png | ssh $(HA_USER)@$(HA_HOST) "cat > /tmp/icon.png && sudo mv /tmp/icon.png $(BACKEND_DST)/icon.png"
	@cat $(ROOT_DIR)/custom_components/logger_manager/icon@2x.png | ssh $(HA_USER)@$(HA_HOST) "cat > /tmp/icon@2x.png && sudo mv /tmp/icon@2x.png $(BACKEND_DST)/icon@2x.png"
	@echo "  → Frontend card..."
	@cat $(UI_SRC) | ssh $(HA_USER)@$(HA_HOST) "cat > /tmp/$(UI_TMP) && sudo mv /tmp/$(UI_TMP) $(BACKEND_DST)/frontend/$(UI_TMP)"
	@echo "✓ Complete integration deployed to $(BACKEND_DST)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Restart Home Assistant"
	@echo "  2. Go to Settings → Devices & Services → Add Integration"
	@echo "  3. Search for 'Logger Manager'"

# Default: complete installation
all: all-ha-install-ready

# Remove integration from all install paths
clean:
	@echo "Checking if Home Assistant is running..."
	@if nc -z $(HA_HOST) $(HA_HTTP_PORT) > /dev/null; then \
	  echo ""; \
	  echo "ERROR: Home Assistant is currently running!"; \
	  echo ""; \
	  echo "Please stop Home Assistant before cleaning:"; \
	  echo "  1. Go to Settings → System → Restart"; \
	  echo "  2. OR use: ha core stop"; \
	  echo "  3. Then run 'make clean' again"; \
	  echo ""; \
	  exit 1; \
	fi
	@echo "✓ Home Assistant is stopped"
	@echo ""
	@echo "Removing Logger Manager from all install paths..."
	@echo "  → Removing custom_components/logger_manager/"
	@ssh $(HA_USER)@$(HA_HOST) "sudo rm -rf $(BACKEND_DST)"
	@echo "  → Removing www/logger_manager/"
	@ssh $(HA_USER)@$(HA_HOST) "sudo rm -rf /config/www/logger_manager"
	@echo "  → Removing www/community/logger_manager/"
	@ssh $(HA_USER)@$(HA_HOST) "sudo rm -rf /config/www/community/logger_manager"
	@echo ""
	@echo "✓ Logger Manager removed from all paths"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Start Home Assistant"
	@echo "  2. Deploy integration using 'make all'"
	@echo "  3. Restart Home Assistant again"

