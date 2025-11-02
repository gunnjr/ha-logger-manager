"""The Logger Manager integration."""
from __future__ import annotations

from datetime import datetime
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "logger_manager"
LEVELS = ["critical", "error", "warning", "info", "debug", "notset"]
STORAGE_VERSION = 1
STORAGE_KEY = "logger_manager_state"

SCHEMA = vol.Schema({
    vol.Required("level"): vol.In(LEVELS),
    vol.Required("loggers"): [str],
})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Logger Manager integration."""
    
    # Initialize storage
    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    
    # Initialize managed loggers tracking if not already done
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    if "managed_loggers" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["managed_loggers"] = {}
    if "last_updated" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["last_updated"] = None
    
    # Store the store instance for use in service calls
    hass.data[DOMAIN]["store"] = store
    
    # Load and restore previous state
    try:
        stored_data = await store.async_load()
        if stored_data:
            managed_loggers = stored_data.get("managed_loggers", {})
            last_updated = stored_data.get("last_updated")
            
            # Restore previous state to memory
            hass.data[DOMAIN]["managed_loggers"] = managed_loggers
            hass.data[DOMAIN]["last_updated"] = last_updated
            
            # Reapply all managed logger levels
            if managed_loggers:
                _LOGGER.info(f"Restoring {len(managed_loggers)} managed logger levels from previous session")
                try:
                    await hass.services.async_call("logger", "set_level", managed_loggers, blocking=True)
                    _LOGGER.debug(f"Successfully restored logger levels: {managed_loggers}")
                except Exception as e:
                    _LOGGER.error(f"Failed to restore logger levels on startup: {e}")
            else:
                _LOGGER.debug("No managed logger levels to restore")
        else:
            _LOGGER.debug("No previous logger state found")
    except Exception as e:
        _LOGGER.error(f"Failed to load logger state from storage: {e}")
    
    async def handle_apply_levels(call: ServiceCall) -> None:
        """Handle the apply_levels service call."""
        # Copy the data to avoid ReadOnlyDict issues
        data = SCHEMA(dict(call.data))
        level = data["level"]
        logger_names = data["loggers"]
        
        # Smart debug logging for our own integration
        our_integration = "custom_components.logger_manager"
        if our_integration in logger_names:
            # Get current managed level for our integration
            managed_data = hass.data[DOMAIN]
            current_level = managed_data["managed_loggers"].get(our_integration, "warning")
            
            # Log BEFORE if changing FROM debug (while debug still visible)
            if current_level.lower() == "debug" and level.lower() != "debug":
                _LOGGER.debug(f"Setting {our_integration} to {level}")
        
        # Create mapping for HA's logger.set_level service
        mapping = {name: level for name in logger_names}
        
        # Call Home Assistant's built-in logger service
        await hass.services.async_call("logger", "set_level", mapping, blocking=True)
        
        # Post-validate: check what actually got set
        logger_data = hass.data.get("logger")
        actual_overrides = getattr(logger_data, 'overrides', {}) if logger_data else {}
        
        # Track only loggers that were actually set
        successfully_set = []
        failed_loggers = []
        
        for logger_name in logger_names:
            # Check if the logger was actually set to our requested level
            if logger_name in actual_overrides:
                # Convert the actual level to string for comparison
                actual_level_int = actual_overrides[logger_name]
                actual_level_str = logging.getLevelName(actual_level_int).lower()
                if actual_level_str == level.lower():
                    successfully_set.append(logger_name)
                else:
                    failed_loggers.append(logger_name)
                    _LOGGER.warning(f"Logger '{logger_name}' was set but to unexpected level '{actual_level_str}' instead of '{level}'")
            else:
                failed_loggers.append(logger_name)
                _LOGGER.warning(f"Failed to set logger level for '{logger_name}' - logger may not exist or setting failed")
        
        # Smart debug logging continued
        if our_integration in successfully_set:
            # Log AFTER if changing TO debug (so debug message appears)
            if level.lower() == "debug":
                _LOGGER.debug(f"Setting {our_integration} to {level}")
                # Also log other integrations now that debug is active
                for logger_name in successfully_set:
                    if logger_name != our_integration:
                        _LOGGER.debug(f"Setting {logger_name} to {level}")
        else:
            # Log for other integrations only (our integration wasn't in the successful list)
            for logger_name in successfully_set:
                if logger_name != our_integration:
                    _LOGGER.debug(f"Setting {logger_name} to {level}")
        
        # Track only the loggers we successfully managed
        managed_data = hass.data[DOMAIN]
        for logger_name in successfully_set:
            managed_data["managed_loggers"][logger_name] = level
        managed_data["last_updated"] = datetime.now().isoformat()
        
        # Log summary if there were any failures
        if failed_loggers:
            _LOGGER.info(f"Successfully set {len(successfully_set)} logger(s), failed to set {len(failed_loggers)} logger(s)")
        else:
            _LOGGER.debug(f"Successfully set all {len(successfully_set)} logger(s)")
        
        # Persist the state to storage
        try:
            store = managed_data["store"]
            await store.async_save({
                "managed_loggers": managed_data["managed_loggers"],
                "last_updated": managed_data["last_updated"]
            })
            _LOGGER.debug(f"Persisted logger state for {len(successfully_set)} loggers")
        except Exception as e:
            _LOGGER.error(f"Failed to persist logger state: {e}")
    
    # Register our service
    hass.services.async_register(DOMAIN, "apply_levels", handle_apply_levels)
    
    return True