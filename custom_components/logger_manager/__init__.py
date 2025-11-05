"""The Logger Manager integration."""
from __future__ import annotations

from datetime import datetime
import logging
import time
import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)

DOMAIN = "logger_manager"
LEVELS = ["critical", "error", "warning", "info", "debug", "notset"]
STORAGE_VERSION = 1
STORAGE_KEY = "logger_manager_state"

# Cache configuration
CACHE_TTL = 1800  # 30 minutes
CACHE_KEY = "logger_cache"

# Platforms to set up
PLATFORMS = [Platform.SENSOR]

SCHEMA = vol.Schema({
    vol.Required("level"): vol.In(LEVELS),
    vol.Required("loggers"): [str],
})

# Test schema (no parameters needed)
TEST_SCHEMA = vol.Schema({})


async def _discover_available_loggers(hass: HomeAssistant) -> list[str]:
    """Discover available loggers from Python logging system.

    Extracts the core discovery logic from the test service for reuse.
    Returns a sorted list of relevant logger names.
    """
    # JG comment to copilot: I just realized that we are explicit in the loggers that we want to include.
    # I'm concerned that this may miss some loggers that users want to debug.
    # Specifically, loggers related to integrations that are not under "homeassistant" or "custom_components".
    # Do such loggers comply with a naming convention we can use to include them? (perhaps they're already picked up by
    # our inclusion of loggers with "homeassistant" in the name?)
    try:
        logger_dict = logging.Logger.manager.loggerDict

        # Get all string logger names
        all_loggers = [name for name in logger_dict.keys() if isinstance(name, str)]

        # Filter to relevant loggers (HA core + custom components + key libraries)
        relevant_loggers = []

        # Add HA core loggers
        ha_loggers = [name for name in all_loggers if "homeassistant" in name]
        relevant_loggers.extend(ha_loggers)

        # Add custom component loggers
        custom_loggers = [name for name in all_loggers if "custom_components" in name]
        relevant_loggers.extend(custom_loggers)

        # Add key library loggers that users often debug
        key_libraries = ["asyncio", "aiohttp", "urllib3", "requests", "aiodns", "aiofiles", "websockets"]
        lib_loggers = [name for name in all_loggers if name in key_libraries]
        relevant_loggers.extend(lib_loggers)

        # Remove duplicates and sort
        unique_loggers = sorted(list(set(relevant_loggers)))

        _LOGGER.debug(f"Logger discovery found {len(unique_loggers)} relevant loggers from {len(all_loggers)} total")

        return unique_loggers

    except Exception as e:
        _LOGGER.error(f"Logger discovery failed: {e}", exc_info=True)
        return []


def _get_logger_cache(hass: HomeAssistant) -> dict | None:
    """Get cached logger data if still valid."""
    cache_data = hass.data.get(DOMAIN, {}).get(CACHE_KEY)
    if not cache_data:
        return None

    # Check if cache is still valid
    if _is_cache_valid(cache_data):
        return cache_data

    # Cache expired, remove it
    if DOMAIN in hass.data and CACHE_KEY in hass.data[DOMAIN]:
        del hass.data[DOMAIN][CACHE_KEY]

    return None


def _update_logger_cache(hass: HomeAssistant, loggers: list[str]) -> None:
    """Update the logger cache with new data."""
    cache_data = {
        "loggers": loggers,
        "timestamp": time.time(),
        "version": 1
    }

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    hass.data[DOMAIN][CACHE_KEY] = cache_data
    _LOGGER.debug(f"Logger cache updated with {len(loggers)} loggers")


def _is_cache_valid(cache_data: dict) -> bool:
    """Check if cache data is still within TTL."""
    if not cache_data or "timestamp" not in cache_data:
        return False

    age = time.time() - cache_data["timestamp"]
    return age < CACHE_TTL


@websocket_api.websocket_command({
    vol.Required("type"): "logger_manager/get_loggers",
})
@websocket_api.require_admin
@callback
def websocket_get_loggers(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Handle WebSocket request for available loggers."""

    async def _handle_request():
        try:
            # Check cache first
            cache_data = _get_logger_cache(hass)
            if cache_data:
                _LOGGER.debug("Returning cached logger data")
                connection.send_message(websocket_api.result_message(msg["id"], {
                    "loggers": cache_data["loggers"],
                    "cached": True,
                    "cache_age": int(time.time() - cache_data["timestamp"])
                }))
                return

            # Cache miss - discover loggers
            _LOGGER.debug("Cache miss - discovering loggers")
            loggers = await _discover_available_loggers(hass)

            # Update cache
            _update_logger_cache(hass, loggers)

            # Return results
            connection.send_message(websocket_api.result_message(msg["id"], {
                "loggers": loggers,
                "cached": False,
                "cache_age": 0
            }))

        except Exception as e:
            _LOGGER.error(f"WebSocket logger discovery failed: {e}", exc_info=True)
            connection.send_message(websocket_api.error_message(
                msg["id"],
                "discovery_failed",
                f"Logger discovery failed: {str(e)}"
            ))

    # Execute async handler
    hass.async_create_task(_handle_request())


async def async_refresh_logger_cache(call: ServiceCall) -> None:
    """Service to manually refresh the logger cache."""
    hass = call.hass

    try:
        _LOGGER.info("Manual logger cache refresh requested")

        # Clear existing cache
        if DOMAIN in hass.data and CACHE_KEY in hass.data[DOMAIN]:
            del hass.data[DOMAIN][CACHE_KEY]

        # Discover fresh loggers
        loggers = await _discover_available_loggers(hass)

        # Update cache
        _update_logger_cache(hass, loggers)

        _LOGGER.info(f"Logger cache refreshed with {len(loggers)} loggers")

    except Exception as e:
        _LOGGER.error(f"Manual cache refresh failed: {e}", exc_info=True)


async def async_test_logger_discovery(call: ServiceCall) -> None:
    """Test service to validate logger discovery approach."""
    hass = call.hass

    try:
        _LOGGER.info("🔍 Logger Discovery Test Starting...")

        # Test the new discovery function
        new_loggers = await _discover_available_loggers(hass)

        # Also test the raw approach for comparison
        logger_dict = logging.Logger.manager.loggerDict
        all_loggers = [name for name in logger_dict.keys() if isinstance(name, str)]

        _LOGGER.info(f"Raw logger_dict size: {len(logger_dict)}")
        _LOGGER.info(f"New discovery function found: {len(new_loggers)} loggers")
        _LOGGER.info(f"Raw discovery found: {len(all_loggers)} loggers")

        # Sample by categories for comparison
        ha_loggers = [name for name in all_loggers if "homeassistant" in name]
        custom_loggers = [name for name in all_loggers if "custom_components" in name]
        lib_loggers = [name for name in all_loggers if name in ["asyncio", "aiohttp", "urllib3"]]

        _LOGGER.info(f"HA loggers found: {len(ha_loggers)}")
        _LOGGER.info(f"Custom component loggers: {len(custom_loggers)}")
        _LOGGER.info(f"Library loggers: {len(lib_loggers)}")

        # Test cache functionality
        _update_logger_cache(hass, new_loggers)
        cached_data = _get_logger_cache(hass)
        cache_valid = _is_cache_valid(cached_data) if cached_data else False

        _LOGGER.info(f"Cache test - stored: {len(cached_data['loggers']) if cached_data else 0}, valid: {cache_valid}")

        # Create test result sensor
        hass.states.async_set("sensor.logger_discovery_test", len(new_loggers), {
            "new_discovery_count": len(new_loggers),
            "raw_discovery_count": len(all_loggers),
            "ha_loggers": len(ha_loggers),
            "custom_loggers": len(custom_loggers),
            "sample_discovered": sorted(new_loggers)[:20],
            "cache_working": cache_valid,
            "test_time": datetime.now().isoformat(),
        })

        _LOGGER.info("✅ Logger discovery test completed successfully")

    except Exception as e:
        _LOGGER.error(f"❌ Logger discovery test failed: {e}", exc_info=True)
        hass.states.async_set("sensor.logger_discovery_test", "error", {
            "error": str(e),
            "test_time": datetime.now().isoformat(),
        })


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Logger Manager from a config entry."""

    # Initialize domain data structure if first entry
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {
            "managed_loggers": {},
            "last_updated": None,
            "services_registered": False,
        }

    # Initialize storage
    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
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

    # Register services and WebSocket command once globally (not per entry)
    if not hass.data[DOMAIN]["services_registered"]:

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

            # Note: HA's logger service accepts any logger name, even invalid/non-existent ones.
            # It will create overrides for non-existent loggers which have no effect but are tracked.
            # This matches HA's built-in behavior. Users can remove invalid loggers by setting
            # them to the default level, which will trigger auto-cleanup in the sensor.

            # Smart debug logging continued
            if our_integration in logger_names:
                # Log AFTER if changing TO debug (so debug message appears)
                if level.lower() == "debug":
                    _LOGGER.debug(f"Setting {our_integration} to {level}")
                    # Also log other integrations now that debug is active
                    for logger_name in logger_names:
                        if logger_name != our_integration:
                            _LOGGER.debug(f"Setting {logger_name} to {level}")
            else:
                # Log for other integrations only (our integration wasn't in the list)
                for logger_name in logger_names:
                    if logger_name != our_integration:
                        _LOGGER.debug(f"Setting {logger_name} to {level}")

            # Track all loggers we requested (matches HA's behavior)
            managed_data = hass.data[DOMAIN]
            for logger_name in logger_names:
                # Remove from managed if set to system default or notset
                system_default = managed_data.get("system_default_level", "warning")
                if level.lower() == system_default or level.lower() == "notset":
                    managed_data["managed_loggers"].pop(logger_name, None)
                else:
                    managed_data["managed_loggers"][logger_name] = level
            managed_data["last_updated"] = datetime.now().isoformat()

            _LOGGER.debug(f"Successfully set all {len(logger_names)} logger(s)")

            # Persist the state to storage
            try:
                store = managed_data["store"]
                await store.async_save({
                    "managed_loggers": managed_data["managed_loggers"],
                    "last_updated": managed_data["last_updated"]
                })
                _LOGGER.debug(f"Persisted logger state for {len(logger_names)} loggers")
            except Exception as e:
                _LOGGER.error(f"Failed to persist logger state: {e}")

        # Register services
        hass.services.async_register(DOMAIN, "apply_levels", handle_apply_levels)
        hass.services.async_register(DOMAIN, "test_logger_discovery", async_test_logger_discovery, schema=TEST_SCHEMA)
        hass.services.async_register(DOMAIN, "refresh_logger_cache", async_refresh_logger_cache, schema=TEST_SCHEMA)

        # Register WebSocket command
        websocket_api.async_register_command(hass, websocket_get_loggers)

        hass.data[DOMAIN]["services_registered"] = True
        _LOGGER.debug("Services and WebSocket command registered")

    # Forward entry setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Logger Manager config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Note: We intentionally do NOT unregister services or WebSocket commands here.
    # These are global resources that should remain available even if the config entry
    # is removed. They'll be cleaned up when Home Assistant shuts down.

    return unload_ok
