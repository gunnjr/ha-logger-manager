<div align="center">

<img src="logo.png" alt="Logger Manager Logo" width="200"/>

# Logger Manager

**A powerful Home Assistant integration for managing and monitoring logging levels**

[![HACS](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/gunnjr/ha-logger-manager.svg)](https://github.com/gunnjr/ha-logger-manager/releases)
[![License](https://img.shields.io/github/license/gunnjr/ha-logger-manager.svg)](LICENSE)

</div>

---

## Overview

Logger Manager provides a comprehensive solution for managing Home Assistant logging levels through an intuitive UI, services, and monitoring capabilities. It enhances the built-in logger functionality with better tracking, persistence, and multi-logger management.

## Why Logger Manager?

- **Visual Management**: Interactive UI card for selecting and managing multiple loggers at once
- **Better Tracking**: Track which loggers you've customized and their current levels
- **Persistent State**: Logger configurations persist across restarts
- **Multi-Logger Operations**: Change levels for multiple loggers simultaneously
- **Auto-Cleanup**: Automatically removes loggers set back to default level
- **WebSocket API**: Programmatic access for advanced use cases

## Features

### 📊 Logger State Sensor

Monitor your logging configuration in real-time:
- Current default log level
- List of all managed loggers and their levels
- Count of customized loggers
- Last updated timestamp
- Real-time updates (10-second polling)

### 🎛️ Interactive UI Card

A powerful custom Lovelace card for managing loggers:
- **Multi-select logger picker** with searchable dropdown
- **Visual level selection** with color-coded indicators
- **Bulk operations** - manage multiple loggers at once
- **Real-time feedback** on current logger states
- **Smart filtering** - search through hundreds of loggers easily

### 🔧 Services

#### `logger_manager.apply_levels`

The recommended way to manage logger levels. Provides better tracking than the built-in `logger.set_level` service.

**Parameters:**
- `level` (required): Log level to apply (critical, error, warning, info, debug)
- `loggers` (required): List of logger names

**Example:**
```yaml
service: logger_manager.apply_levels
data:
  level: debug
  loggers:
    - homeassistant.components.zha
    - homeassistant.components.mqtt
    - custom_components.logger_manager
```

#### `logger_manager.refresh_logger_cache`

Manually refresh the cached list of available loggers. Cache normally refreshes every 30 minutes automatically.

**Use case:** After installing new integrations, refresh the cache to immediately see new loggers in the UI.

### 🔌 WebSocket API

For advanced automation and custom frontends:

#### `logger_manager/get_loggers`

Retrieve the complete list of available loggers from the system.

**Request:**
```json
{
  "type": "logger_manager/get_loggers"
}
```

**Response:**
```json
{
  "loggers": [
    "homeassistant.core",
    "homeassistant.components.mqtt",
    "custom_components.logger_manager",
    ...
  ]
}
```

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the "⋮" menu in the top right
4. Select "Custom repositories"
5. Add `https://github.com/gunnjr/ha-logger-manager` as an Integration
6. Click "Download"
7. Restart Home Assistant
8. Go to **Settings → Devices & Services → Add Integration**
9. Search for "Logger Manager" and add it

### Manual Installation

1. Copy the `custom_components/logger_manager` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration**
4. Search for "Logger Manager" and add it

## Setup

### Adding the Integration

1. Navigate to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **Logger Manager**
4. Click to add (no configuration needed)

### Adding the UI Card

#### Via UI (Easiest)

1. Navigate to your dashboard
2. Click the **⋮** menu → **Edit Dashboard**
3. Click **Add Card**
4. Scroll down and select **Custom: Logger Manager Card**
5. Save

#### Via YAML

```yaml
type: custom:ha-logger-multiselect-card
entity: sensor.logger_levels
```

## Usage

### Managing Logger Levels via UI

1. Open your dashboard with the Logger Manager card
2. Use the **Logger Selection** dropdown to choose one or more loggers
   - Search by typing to filter the list
   - Select multiple loggers for bulk operations
3. Choose a **Log Level** from the buttons (Critical, Error, Warning, Info, Debug)
4. Click **Apply** to set the level
5. View current managed loggers in the **Current Logger Levels** section
6. To reset a logger to default, select it and choose the default level

### Managing Logger Levels via Service

Use the `logger_manager.apply_levels` service in automations or scripts:

```yaml
# Set multiple core components to debug
service: logger_manager.apply_levels
data:
  level: debug
  loggers:
    - homeassistant.components.zha
    - homeassistant.components.mqtt
    - homeassistant.components.automation
```

```yaml
# Set custom components to info
service: logger_manager.apply_levels
data:
  level: info
  loggers:
    - custom_components.logger_manager
    - custom_components.hacs
```

### Common Logger Patterns

**Core Components:**
```
homeassistant.components.<component_name>
```
Example: `homeassistant.components.zha`, `homeassistant.components.mqtt`

**Custom Integrations:**
```
custom_components.<integration_name>
```
Example: `custom_components.logger_manager`, `custom_components.hacs`

**System Loggers:**
```
homeassistant.core
homeassistant.loader
homeassistant.setup
homeassistant.bootstrap
```

## Sensor Attributes

The `sensor.logger_levels` entity provides the following attributes:

| Attribute | Description |
|-----------|-------------|
| `default` | Current default log level for Home Assistant |
| `managed_loggers` | Dictionary of logger names and their custom levels |
| `managed_count` | Number of loggers with custom levels |
| `last_updated` | ISO timestamp of last logger change |

## Requirements

- Home Assistant ≥ 2024.6.0
- Modern web browser for UI card

## Architecture

Logger Manager uses a pure config flow architecture with:
- Singleton service registration to prevent conflicts
- Storage-based state persistence across restarts
- WebSocket API for real-time logger discovery
- Automatic cleanup of loggers returned to default level
- Integration with Home Assistant's built-in logger system

## Troubleshooting

### UI Card Not Appearing

1. Verify the integration is installed and enabled
2. Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)
3. Check browser console for JavaScript errors
4. Verify the card resource is loaded in **Settings → Dashboards → Resources**

### Loggers Not Showing in Dropdown

1. Use the `logger_manager.refresh_logger_cache` service
2. Verify integrations are loaded (check **Settings → Devices & Services**)
3. Check Home Assistant logs for errors

### Logger Levels Not Persisting

Logger Manager stores state in `.storage/logger_manager`. If levels don't persist:
1. Check file permissions on the `.storage` directory
2. Verify Home Assistant can write to storage
3. Check logs for storage-related errors

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

- **Issues**: [GitHub Issues](https://github.com/gunnjr/ha-logger-manager/issues)
- **Discussions**: [GitHub Discussions](https://github.com/gunnjr/ha-logger-manager/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with the Home Assistant integration framework and designed to enhance the developer and power-user experience.

---

<div align="center">

**[⬆ Back to Top](#logger-manager)**

Made with ❤️ for the Home Assistant community

</div>
