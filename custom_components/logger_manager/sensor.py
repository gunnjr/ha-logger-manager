"""Logger Manager sensor platform."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=10)
DOMAIN = "logger"  # built-in HA logger integration


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Logger Manager sensor platform."""
    _LOGGER.debug("Setting up Logger Manager sensor platform")
    async_add_entities([LoggerInspectorSensor(hass)], True)


class LoggerInspectorSensor(SensorEntity):
    """Sensor that exposes Home Assistant logger state."""

    _attr_name = "Logger Levels"
    _attr_icon = "mdi:file-document-alert"
    _attr_should_poll = True

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the sensor."""
        self.hass = hass

    def update(self) -> None:
        """Update the sensor state."""
        data = self.hass.data.get(DOMAIN) or {}
        default = data.get("default") or "unknown"
        loggers = dict(sorted((data.get("loggers") or {}).items()))
        
        self._attr_native_value = default
        self._attr_extra_state_attributes = {
            "default": default,
            "loggers": loggers,
            "count": len(loggers),
        }