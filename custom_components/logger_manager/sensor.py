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
        data = self.hass.data.get(DOMAIN)
        
        if data is None:
            self._attr_native_value = "unavailable"
            self._attr_extra_state_attributes = {
                "default": "unavailable",
                "loggers": {},
                "count": 0,
                "error": "Logger data not found"
            }
            return
            
        # Debug: log the type and available attributes
        _LOGGER.debug(f"Logger data type: {type(data)}")
        _LOGGER.debug(f"Logger data attributes: {dir(data)}")
        
        try:
            # Try to access logger data - we need to figure out the correct structure
            if hasattr(data, 'default_level'):
                default = str(data.default_level)
            elif hasattr(data, 'default'):
                default = str(data.default)
            else:
                default = "unknown"
                
            if hasattr(data, 'loggers'):
                loggers = dict(data.loggers) if data.loggers else {}
            else:
                loggers = {}
                
            self._attr_native_value = default
            self._attr_extra_state_attributes = {
                "default": default,
                "loggers": loggers,
                "count": len(loggers),
                "data_type": str(type(data))
            }
        except Exception as e:
            _LOGGER.error(f"Error accessing logger data: {e}")
            self._attr_native_value = "error"
            self._attr_extra_state_attributes = {
                "error": str(e),
                "data_type": str(type(data))
            }