"""Frontend resource registration for Logger Manager."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later

_LOGGER = logging.getLogger(__name__)

DOMAIN = "logger_manager"
URL_BASE = f"/hacsfiles/{DOMAIN}"
CARD_FILENAME = "ha-logger-multiselect-card.js"
CARD_URL = f"{URL_BASE}/{CARD_FILENAME}"
CARD_VERSION = "1.0.0"  # Can be updated when card changes


class JSModuleRegistration:
    """Register JavaScript modules for Logger Manager."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the JS module registration."""
        self.hass = hass
        self.lovelace_data = hass.data.get("lovelace")

    async def async_register(self) -> None:
        """Register frontend card resources."""
        _LOGGER.debug("Frontend registration starting")
        await self._async_register_path()

        # Only attempt automatic resource registration if Lovelace is in storage mode
        if self.lovelace_data and self.lovelace_data.mode == "storage":
            _LOGGER.debug("Lovelace mode: %s - will attempt automatic resource registration", self.lovelace_data.mode)
            await self._async_wait_for_lovelace_resources()
        else:
            mode = self.lovelace_data.mode if self.lovelace_data else "not available"
            _LOGGER.info(
                "Lovelace mode: %s - automatic registration skipped. "
                "Users will need to manually add the card resource.", mode
            )

    async def _async_register_path(self) -> None:
        """Register resource path for the frontend card."""
        try:
            await self.hass.http.async_register_static_paths([
                StaticPathConfig(URL_BASE, Path(__file__).parent, False)
            ])
            _LOGGER.debug("Static path registered successfully: %s", URL_BASE)
        except RuntimeError:
            # Already registered - this is fine
            _LOGGER.debug("Static path already registered: %s", URL_BASE)

    async def _async_wait_for_lovelace_resources(self) -> None:
        """Wait for Lovelace resources to be loaded, then register card."""
        _LOGGER.debug("Waiting for Lovelace resources to load")

        @callback
        async def _check_resources_loaded(now) -> None:
            """Check if Lovelace resources are loaded."""
            _LOGGER.debug("Checking if Lovelace resources are loaded...")
            if self.lovelace_data.resources.loaded:
                _LOGGER.debug("Lovelace resources loaded, proceeding to register card")
                await self._async_register_card_resource()
            else:
                # Resources not loaded yet, check again in 5 seconds
                _LOGGER.debug("Lovelace resources not loaded yet, will retry in 5 seconds")
                async_call_later(self.hass, 5, _check_resources_loaded)

        # Start checking
        await _check_resources_loaded(None)

    async def _async_register_card_resource(self) -> None:
        """Register the card resource in Lovelace."""
        _LOGGER.debug("Attempting to register card resource: %s", CARD_URL)
        try:
            resources: ResourceStorageCollection = self.lovelace_data.resources
            existing_resources = resources.async_items()
            _LOGGER.debug("Found %d existing Lovelace resources", len(existing_resources))

            # Check if our resource already exists
            for resource in existing_resources:
                if CARD_URL in resource.get("url", ""):
                    _LOGGER.debug("Card resource already registered: %s", CARD_URL)
                    return

            # Resource doesn't exist, create it
            _LOGGER.debug("Creating new card resource entry for: %s", CARD_URL)
            await resources.async_create_item({
                "res_type": "module",
                "url": CARD_URL,
            })
            _LOGGER.info("Successfully registered Logger Manager card resource: %s", CARD_URL)

        except Exception as e:
            _LOGGER.warning(
                "Could not automatically register card resource: %s. "
                "Users can manually add it via Dashboard Resources.",
                e
            )

    async def async_unregister(self) -> None:
        """Unregister frontend card resources."""
        _LOGGER.info(
            "Unregistering Logger Manager frontend resources. "
            "If you have Logger Manager cards on your dashboards, they will need to be removed manually."
        )

        if not self.lovelace_data or self.lovelace_data.mode != "storage":
            _LOGGER.debug("Lovelace not in storage mode, no resources to unregister")
            return

        try:
            resources: ResourceStorageCollection = self.lovelace_data.resources
            existing_resources = resources.async_items()

            # Find and remove our resource
            for resource in existing_resources:
                if CARD_URL in resource.get("url", ""):
                    await resources.async_delete_item(resource["id"])
                    _LOGGER.info("Unregistered Logger Manager card resource")
                    return

        except Exception as e:
            _LOGGER.warning("Could not unregister card resource: %s", e)
