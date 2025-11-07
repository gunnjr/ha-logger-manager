"""Frontend resource registration for Logger Manager."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http.static import StaticPathConfig
from homeassistant.components.lovelace import LovelaceResources
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
        await self._async_register_path()

        # Only attempt automatic resource registration if Lovelace is in storage mode
        if self.lovelace_data and self.lovelace_data.mode == "storage":
            await self._async_wait_for_lovelace_resources()
        else:
            _LOGGER.debug(
                "Lovelace is not in storage mode or not available. "
                "Users will need to manually add the card resource."
            )

    async def _async_register_path(self) -> None:
        """Register resource path for the frontend card."""
        try:
            await self.hass.http.async_register_static_paths([
                StaticPathConfig(URL_BASE, Path(__file__).parent, False)
            ])
            _LOGGER.debug("Registered frontend resource path: %s", URL_BASE)
        except RuntimeError:
            # Already registered - this is fine
            _LOGGER.debug("Frontend resource path already registered")

    async def _async_wait_for_lovelace_resources(self) -> None:
        """Wait for Lovelace resources to be loaded, then register card."""
        @callback
        async def _check_resources_loaded(now) -> None:
            """Check if Lovelace resources are loaded."""
            if self.lovelace_data.resources.loaded:
                await self._async_register_card_resource()
            else:
                # Resources not loaded yet, check again in 5 seconds
                async_call_later(self.hass, 5, _check_resources_loaded)

        # Start checking
        await _check_resources_loaded(None)

    async def _async_register_card_resource(self) -> None:
        """Register the card resource in Lovelace."""
        try:
            resources: ResourceStorageCollection = self.lovelace_data.resources
            existing_resources = await resources.async_items()

            # Check if our resource already exists
            for resource in existing_resources:
                if CARD_URL in resource.get("url", ""):
                    _LOGGER.debug("Card resource already registered: %s", CARD_URL)
                    return

            # Resource doesn't exist, create it
            await resources.async_create_item({
                "res_type": "module",
                "url": CARD_URL,
            })
            _LOGGER.info("Automatically registered Logger Manager card resource: %s", CARD_URL)

        except Exception as e:
            _LOGGER.warning(
                "Could not automatically register card resource: %s. "
                "Users can manually add it via Dashboard Resources.",
                e
            )

    async def async_unregister(self) -> None:
        """Unregister frontend card resources."""
        if not self.lovelace_data or self.lovelace_data.mode != "storage":
            _LOGGER.debug("Lovelace not in storage mode, no resources to unregister")
            return

        try:
            resources: ResourceStorageCollection = self.lovelace_data.resources
            existing_resources = await resources.async_items()

            # Find and remove our resource
            for resource in existing_resources:
                if CARD_URL in resource.get("url", ""):
                    await resources.async_delete_item(resource["id"])
                    _LOGGER.info("Unregistered Logger Manager card resource")
                    return

        except Exception as e:
            _LOGGER.warning("Could not unregister card resource: %s", e)
