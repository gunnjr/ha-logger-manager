<div align="center">

<img src="logo.png" alt="Logger Manager Logo" width="200"/>

# Logger Manager

A Home Assistant integration for managing logging levels

[![HACS](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/gunnjr/ha-logger-manager.svg)](https://github.com/gunnjr/ha-logger-manager/releases)
[![License](https://img.shields.io/github/license/gunnjr/ha-logger-manager.svg)](LICENSE)

</div>

---

## What It Does

Logger Manager helps you change and monitor Home Assistant logging levels. It provides a sensor to track which loggers you've customized, services to change log levels, and an optional UI card for visual management.

## Why Use This?

When debugging Home Assistant, you often need to enable debug logging for specific integrations. Logger Manager:
- Remembers which loggers you've customized
- Lets you change multiple logger levels at once
- Provides a sensor showing your current logging configuration
- Includes a UI card for easier management (optional)

It's a helper tool for developers and power users who frequently work with HA logging.

## Features

### Logger State Sensor

A sensor (`sensor.logger_levels`) showing:
- Current default log level
- List of loggers you've customized and their levels
- Count of customized loggers
- Updates every 10 seconds

### Services

#### `logger_manager.apply_levels`

Change log levels for one or more loggers. Similar to HA's built-in `logger.set_level` but tracks what you've changed.

```yaml
service: logger_manager.apply_levels
data:
  level: debug
  loggers:
    - homeassistant.components.zha
    - custom_components.logger_manager
```

#### `logger_manager.refresh_logger_cache`

Manually refresh the list of available loggers (normally refreshes every 30 minutes automatically).

### UI Card (Optional)

A Lovelace card that lets you:
- Select multiple loggers from a searchable dropdown
- Change their log levels with buttons
- See which loggers are currently customized

## Installation

### Via HACS

1. Open HACS → Integrations
2. Add custom repository: `https://github.com/gunnjr/ha-logger-manager`
3. Download "Logger Manager"
4. Restart Home Assistant
5. Add integration: Settings → Devices & Services → Add Integration → Logger Manager

### Manual

1. Copy `custom_components/logger_manager` to your HA `config/custom_components/` directory
2. Restart Home Assistant
3. Add integration: Settings → Devices & Services → Add Integration → Logger Manager

## Setup

### Adding the Integration

1. Go to Settings → Devices & Services
2. Click Add Integration
3. Search for "Logger Manager"
4. Click Submit (no configuration needed)

You'll see:
- `sensor.logger_levels` entity created
- Services registered under `logger_manager`

### Adding the UI Card (Optional)

The UI card should be automatically available after installation. To add it to your dashboard:

1. Edit your dashboard
2. Add Card → Search for "Logger Manager Card"
3. Add the card

If the card doesn't appear, you may need to hard-refresh your browser (Ctrl+F5 or Cmd+Shift+R).

Alternatively, add via YAML:
```yaml
type: custom:ha-logger-multiselect-card
entity: sensor.logger_levels
```

## Usage

### Via UI Card

1. Open the card on your dashboard
2. Use the dropdown to select loggers (supports search and multi-select)
3. Click a log level button (Critical, Error, Warning, Info, Debug)
4. Click Apply

### Via Service

```yaml
service: logger_manager.apply_levels
data:
  level: debug
  loggers:
    - homeassistant.components.mqtt
    - custom_components.logger_manager
```

### Common Logger Names

**Core integrations:**
```
homeassistant.components.<integration_name>
```
Examples: `homeassistant.components.zha`, `homeassistant.components.mqtt`

**Custom integrations:**
```
custom_components.<integration_name>
```
Examples: `custom_components.logger_manager`, `custom_components.hacs`

**System loggers:**
```
homeassistant.core
homeassistant.loader
homeassistant.setup
```

## Limitations

- Loggers must exist for level changes to take effect
- Some third-party libraries may not follow HA logging conventions
- The sensor updates every 10 seconds, not instantly
- WebSocket API for logger discovery caches results for 30 minutes

## Requirements

- Home Assistant ≥ 2024.6.0

## Troubleshooting

**UI Card Not Showing:**
- Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)
- Check browser console for errors
- Verify integration is installed and loaded

**Logger Not in Dropdown:**
- Use `logger_manager.refresh_logger_cache` service
- Verify the integration is loaded in HA
- Try typing the logger name manually in the card

**Levels Not Persisting:**
- Logger Manager stores state in `.storage/logger_manager`
- Check file permissions if levels disappear after restart

## Contributing

Contributions welcome! This is a small project maintained as-needed. Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**[⬆ Back to Top](#logger-manager)**

Built for Home Assistant developers and power users

</div>
