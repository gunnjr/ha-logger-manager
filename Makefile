# Makefile for deploying Home Assistant Logger Manager

# === CONFIGURATION ===
HA_HOST=homeassistant.local
HA_USER=hassio

# Main UI deployment (legacy/manual install)
UI_SRC=custom_components/logger_manager/frontend/ha-logger-multiselect-card.js
UI_TMP=ha-logger-multiselect-card.js
UI_DST=/config/www/logger_manager/ha-logger-multiselect-card.js

# HACS-style UI deployment
HACS_UI_DST=/config/www/community/logger_manager/ha-logger-multiselect-card.js

BACKEND_SRC=custom_components/logger_manager/__init__.py custom_components/logger_manager/sensor.py custom_components/logger_manager/manifest.json custom_components/logger_manager/services.yaml
BACKEND_DST=/config/custom_components/logger_manager/

.PHONY: ui backend all

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

