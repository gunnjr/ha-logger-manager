# Makefile for deploying Home Assistant Logger Manager

# === CONFIGURATION ===
HA_HOST=homeassistant.local
HA_USER=hassio
HA_HTTP_PORT=8123

# Path to project root (Makefile is in devtools/)
ROOT_DIR=..

# Backend Python files (root level)
BACKEND_FILES = \
	__init__.py \
	sensor.py \
	config_flow.py \
	const.py \
	manifest.json \
	strings.json \
	services.yaml

# Frontend files
FRONTEND_FILES = \
	__init__.py \
	ha-logger-multiselect-card.js

# Translation files
TRANSLATION_FILES = \
	en.json

# Icon files
ICON_FILES = \
	icon.png \
	icon@2x.png

# Deployment destination
BACKEND_DST=/config/custom_components/logger_manager/

.PHONY: all clean status help

# Show help by default
help:
	@echo "Logger Manager Deployment Targets:"
	@echo "  make all             - Deploy complete integration (default)"
	@echo "  make clean           - Remove integration from all install paths"
	@echo "  make status          - Show what files will be deployed"
	@echo ""
	@echo "After deployment, restart HA via:"
	@echo "  Settings → System → Restart (or use HA UI/CLI)"
	@echo ""
	@echo "Configuration:"
	@echo "  HA_HOST: $(HA_HOST)"
	@echo "  HA_USER: $(HA_USER)"

# Show what files will be deployed
status:
	@echo "=== Files to Deploy ==="
	@echo ""
	@echo "Backend files (root level):"
	@for file in $(BACKEND_FILES); do \
	  fullpath="$(ROOT_DIR)/custom_components/logger_manager/$$file"; \
	  if [ -f "$$fullpath" ]; then \
	    echo "  ✓ $$file"; \
	  else \
	    echo "  ✗ $$file (MISSING)"; \
	  fi \
	done
	@echo ""
	@echo "Frontend files:"
	@for file in $(FRONTEND_FILES); do \
	  fullpath="$(ROOT_DIR)/custom_components/logger_manager/frontend/$$file"; \
	  if [ -f "$$fullpath" ]; then \
	    echo "  ✓ frontend/$$file"; \
	  else \
	    echo "  ✗ frontend/$$file (MISSING)"; \
	  fi \
	done
	@echo ""
	@echo "Translation files:"
	@for file in $(TRANSLATION_FILES); do \
	  fullpath="$(ROOT_DIR)/custom_components/logger_manager/translations/$$file"; \
	  if [ -f "$$fullpath" ]; then \
	    echo "  ✓ translations/$$file"; \
	  else \
	    echo "  ✗ translations/$$file (MISSING)"; \
	  fi \
	done
	@echo ""
	@echo "Icon files:"
	@for file in $(ICON_FILES); do \
	  fullpath="$(ROOT_DIR)/custom_components/logger_manager/$$file"; \
	  if [ -f "$$fullpath" ]; then \
	    echo "  ✓ $$file"; \
	  else \
	    echo "  ✗ $$file (MISSING)"; \
	  fi \
	done
	@echo ""
	@echo "Deployment target: $(HA_USER)@$(HA_HOST):$(BACKEND_DST)"

# Deploy complete integration to custom_components (mimics HACS installation)
all:
	@echo "Deploying complete integration to Home Assistant..."
	@ssh $(HA_USER)@$(HA_HOST) "sudo mkdir -p $(BACKEND_DST)"
	@ssh $(HA_USER)@$(HA_HOST) "sudo mkdir -p $(BACKEND_DST)/translations"
	@ssh $(HA_USER)@$(HA_HOST) "sudo mkdir -p $(BACKEND_DST)/frontend"
	@echo "  → Backend files..."
	@for file in $(BACKEND_FILES); do \
	  cat $(ROOT_DIR)/custom_components/logger_manager/$$file | \
	    ssh $(HA_USER)@$(HA_HOST) "cat > /tmp/$$file && sudo mv /tmp/$$file $(BACKEND_DST)/$$file"; \
	done
	@echo "  → Frontend files..."
	@for file in $(FRONTEND_FILES); do \
	  cat $(ROOT_DIR)/custom_components/logger_manager/frontend/$$file | \
	    ssh $(HA_USER)@$(HA_HOST) "cat > /tmp/frontend_$$file && sudo mv /tmp/frontend_$$file $(BACKEND_DST)/frontend/$$file"; \
	done
	@echo "  → Translation files..."
	@for file in $(TRANSLATION_FILES); do \
	  cat $(ROOT_DIR)/custom_components/logger_manager/translations/$$file | \
	    ssh $(HA_USER)@$(HA_HOST) "cat > /tmp/$$file && sudo mv /tmp/$$file $(BACKEND_DST)/translations/$$file"; \
	done
	@echo "  → Icon files..."
	@for file in $(ICON_FILES); do \
	  cat $(ROOT_DIR)/custom_components/logger_manager/$$file | \
	    ssh $(HA_USER)@$(HA_HOST) "cat > /tmp/$$file && sudo mv /tmp/$$file $(BACKEND_DST)/$$file"; \
	done
	@echo "✓ Complete integration deployed to $(BACKEND_DST)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Restart Home Assistant"
	@echo "  2. Go to Settings → Devices & Services → Add Integration"
	@echo "  3. Search for 'Logger Manager'"

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

