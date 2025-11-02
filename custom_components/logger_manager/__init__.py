"""The Logger Manager integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

DOMAIN = "logger_manager"
LEVELS = ["critical", "error", "warning", "info", "debug", "notset"]

SCHEMA = vol.Schema({
    vol.Required("level"): vol.In(LEVELS),
    vol.Required("loggers"): [str],
})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Logger Manager integration."""
    
    async def handle_apply_levels(call: ServiceCall) -> None:
        """Handle the apply_levels service call."""
        # Copy the data to avoid ReadOnlyDict issues
        data = SCHEMA(dict(call.data))
        level = data["level"]
        logger_names = data["loggers"]
        
        # Create mapping for HA's logger.set_level service
        mapping = {name: level for name in logger_names}
        
        # Call Home Assistant's built-in logger service
        await hass.services.async_call("logger", "set_level", mapping, blocking=True)
    
    # Register our service
    hass.services.async_register(DOMAIN, "apply_levels", handle_apply_levels)
    
    return True