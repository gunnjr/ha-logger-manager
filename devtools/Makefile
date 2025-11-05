# Makefile for deploying Home Assistant Logger Manager

# === CONFIGURATION ===
HA_HOST=homeassistant.local
HA_USER=hassio

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

.PHONY: ui ui-hacs backend all status help

# Show help by default
help:
	@echo "Logger Manager Deployment Targets:"
	@echo "  make backend     - Deploy backend Python files to HA"
	@echo "  make ui          - Deploy UI card (legacy path)"
	@echo "  make ui-hacs     - Deploy UI card (HACS path)"
	@echo "  make all         - Deploy both UI and backend"
	@echo "  make status      - Show what would be deployed"
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
	for file in $(BACKEND_SRC); do \
	  fname=$$(basename $$file); \
	  cat $$file | ssh $(HA_USER)@$(HA_HOST) "cat > /tmp/$$fname && sudo rm -f $(BACKEND_DST)/$$fname && sudo mv /tmp/$$fname $(BACKEND_DST)/$$fname"; \
	done

all: ui backend

