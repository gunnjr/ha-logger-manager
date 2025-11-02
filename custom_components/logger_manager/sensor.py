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
            
        try:
            # LoggerDomainConfig has:
            # - overrides: dict[str, Any] - current logger level overrides
            # - settings: LoggerSettings - contains default level and stored config
            
            # Get the settings object
            settings = getattr(data, 'settings', None)
            overrides = getattr(data, 'overrides', {})
            
            if settings:
                # Get default level from settings
                default_level = getattr(settings, '_default_level', logging.INFO)
                default_str = logging.getLevelName(default_level).lower()
            else:
                default_str = "unknown"
                
            # Convert overrides to readable format
            loggers_dict = {}
            for logger_name, level in overrides.items():
                if isinstance(level, int):
                    loggers_dict[logger_name] = logging.getLevelName(level).lower()
                else:
                    loggers_dict[logger_name] = str(level).lower()
                    
            self._attr_native_value = default_str
            self._attr_extra_state_attributes = {
                "default": default_str,
                "loggers": dict(sorted(loggers_dict.items())),
                "count": len(loggers_dict),
            }
            
        except Exception as e:
            _LOGGER.error(f"Error accessing logger data: {e}")
            self._attr_native_value = "error"
            self._attr_extra_state_attributes = {
                "error": str(e),
                "data_type": str(type(data)),
                "available_attrs": [attr for attr in dir(data) if not attr.startswith('_')]
            }