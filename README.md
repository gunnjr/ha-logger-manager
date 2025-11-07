<div align="center">

<img src="logo.png" alt="Logger Manager Logo" width="200"/>

# Logger Manager

A Home Assistant integration for managing logging levels

[![HACS](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/gunnjr/ha-logger-manager.svg)](https://github.com/gunnjr/ha-logger-manager/releases)
[![License](https://img.shields.io/github/license/gunnjr/ha-logger-manager.svg)](LICENSE)

</div>

---

> **Note**: This is my first published Home Assistant integration. While it works and is useful, it may need improvements and hardening as more people use it. Feedback, issues, and contributions are welcome!

---

## Overview

Logger Manager solves a common frustration for Home Assistant developers and power users: **managing logging levels is tedious and error-prone**.

### The Problem

When troubleshooting Home Assistant issues, you need to enable debug logging for specific integrations. The native approach requires:
- Opening Developer Tools → Services
- Manually typing logger names (e.g., `homeassistant.components.zha`)
- Calling `logger.set_level` with exact syntax
- Remembering which loggers you've modified
- Repeating this process after every HA restart (changes don't persist)

This workflow is slow, requires memorizing logger naming conventions, and offers no visibility into your current logging configuration.

### The Solution

Logger Manager provides three integrated components that work together to make logging management effortless:

**1. Interactive UI Card** (the primary interface)
- Searchable multi-select dropdown of all available loggers
- One-click level changes with visual feedback
- Bulk operations - modify multiple loggers at once
- No typing required, no syntax to remember

**2. Persistent State Sensor** (`sensor.logger_levels`)
- Tracks which loggers you've customized and their current levels
- Shows default log level and count of managed loggers
- Updates every 10 seconds for real-time visibility
- Powers the UI card and enables automations

**3. Management Services**
- `logger_manager.apply_levels` - Programmatically change logger levels
- `logger_manager.refresh_logger_cache` - Force refresh available loggers
- Services maintain managed logger state across HA restarts
- Enable automation-based logging control

### Why the UI Card Matters Most

While the sensor and services are useful standalone (especially for automations), **the UI card is the primary reason to use Logger Manager**. It transforms a multi-step, error-prone workflow into a simple point-and-click operation. The backend components exist primarily to support this seamless UI experience.

## Key Feature: The UI Card

![Logger Manager Card Overview](screenshots/logger-card-overview.png)

The Logger Manager card provides:
- **Searchable multi-select dropdown** of all available loggers
- **One-click level changes** (Critical, Error, Warning, Info, Debug)
- **Visual feedback** on current logger states
- **Bulk operations** - change multiple loggers at once

This is the primary reason to use Logger Manager. The backend services and sensor exist to support the UI, but the UI is where the real value lies.

![Logger Dropdown Search](screenshots/logger-dropdown-search.png)

## Secondary Features

### Logger State Sensor

![Logger Sensor State](screenshots/logger-sensor-state.png)

A sensor (`sensor.logger_levels`) that tracks:
- Current default log level
- List of loggers you've customized and their levels
- Count of customized loggers
- Updates every 10 seconds

### Services

#### `logger_manager.apply_levels`

Change log levels for one or more loggers. Similar to HA's built-in `logger.set_level` but maintains a list of managed loggers for the UI.

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

## Installation

### Via HACS (Recommended)

#### Option 1: HACS Default Repository (Coming Soon)
Once Logger Manager is accepted into HACS defaults:
1. Open HACS → Integrations
2. Click "+ Explore & Download Repositories"
3. Search for "Logger Manager"
4. Click "Download"
5. Restart Home Assistant
6. Continue to [Setup](#setup) below

#### Option 2: HACS Custom Repository (Current Method)
Until Logger Manager is in HACS defaults:
1. Open HACS → Integrations
2. Click the three dots (⋮) in the top-right corner
3. Select "Custom repositories"
4. Add repository URL: `https://github.com/gunnjr/ha-logger-manager`
5. Category: `Integration`
6. Click "Add"
7. Find "Logger Manager" in the list and click "Download"
8. Restart Home Assistant
9. Continue to [Setup](#setup) below

### Manual Installation

If you prefer not to use HACS:

1. Download the latest release from [GitHub Releases](https://github.com/gunnjr/ha-logger-manager/releases)
2. Extract the archive
3. Copy the `custom_components/logger_manager` directory to your Home Assistant `config/custom_components/` directory
   - Full path should be: `config/custom_components/logger_manager/`
   - Should contain: `__init__.py`, `manifest.json`, `sensor.py`, `config_flow.py`, etc.
4. Restart Home Assistant
5. Continue to [Setup](#setup) below

## Setup

### Step 1: Add the Integration

After installation and restart:

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"** (bottom-right)
3. Search for **"Logger Manager"**
4. Click on it to add
5. Click **"Submit"** (no configuration needed)

The integration will automatically:
- Create `sensor.logger_levels` entity
- Register `logger_manager.apply_levels` and `logger_manager.refresh_logger_cache` services
- Register the frontend card resource (storage mode only)

### Step 2: Add the UI Card to Your Dashboard

The card resource is automatically registered when you add the integration (for storage mode dashboards). To use it:

1. Navigate to any dashboard
2. Click **Edit Dashboard** (top-right)
3. Click **"+ Add Card"**
4. Search for **"Logger Manager Card"** or scroll to find it
5. Click to add it to your dashboard
6. Click **"Done"** to save

**If the card doesn't appear in the card picker:**
- Hard refresh your browser: `Ctrl+F5` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Check Settings → Dashboards → Resources to verify the card is listed
- For YAML mode dashboards, see [YAML Configuration](#yaml-configuration) below

#### YAML Configuration

If you prefer YAML or use YAML mode dashboards:

```yaml
type: custom:ha-logger-multiselect-card
entity: sensor.logger_levels
```

**Note for YAML Mode Users:** If your dashboards are in YAML mode (not storage mode), you'll need to manually add the card resource:

1. Go to Settings → Dashboards → Resources tab
2. Click "+ Add Resource"
3. URL: `/hacsfiles/logger_manager/ha-logger-multiselect-card.js`
4. Resource type: `JavaScript Module`
5. Click "Create"

## Usage

### Via UI Card (Recommended)

1. Open the card on your dashboard
2. Use the dropdown to select loggers (search and multi-select supported)
3. Click a log level button
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

## Planned Enhancements

Future versions will add:

### v1.1: Configurable Logger Discovery
- Make logger discovery patterns configurable
- Currently hardcoded to find HA core, custom components, and system loggers
- Will allow users to add custom patterns for third-party libraries

### v1.2: Logger Management UI
- View all managed loggers in a dedicated interface
- Edit or remove managed logger levels
- See history of changes

### v1.3: Default Log Level Control
- UI to change Home Assistant's default log level
- Currently can only be changed via configuration.yaml

### v2.0: Integrated Dashboard
- Pre-built dashboard combining all Logger Manager features
- One-stop shop for all logging needs

No timeline promised - these will come as time permits and based on user feedback.

## Limitations

- Loggers must exist for level changes to take effect
- Some third-party libraries may not follow HA logging conventions
- The sensor updates every 10 seconds, not instantly
- WebSocket API for logger discovery caches results for 30 minutes
- Logger discovery patterns are currently hardcoded (v1.1 will make this configurable)

## Requirements

- Home Assistant ≥ 2024.6.0

## Troubleshooting

**UI Card Not Appearing in Card Picker:**
- Hard refresh your browser: `Ctrl+F5` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Check Settings → Dashboards → Resources - you should see `/hacsfiles/logger_manager/ha-logger-multiselect-card.js`
- If using YAML mode dashboards, you must manually add the resource (see [YAML Configuration](#yaml-configuration))
- Check browser console (F12) for JavaScript errors
- Verify the integration is installed and loaded in Settings → Devices & Services

**Card Resource Not Auto-Registered:**
- Automatic registration only works in storage mode (default for most users)
- Check your Lovelace mode: if dashboards are defined in `configuration.yaml`, you're using YAML mode
- For YAML mode, manually add the resource as described in [YAML Configuration](#yaml-configuration)
- Check Home Assistant logs for any frontend registration errors

**Logger Not in Dropdown:**
- Use the `logger_manager.refresh_logger_cache` service to force a refresh
- Verify the integration/component is actually loaded in Home Assistant
- Some third-party libraries may not appear if they don't follow standard naming conventions
- The cache refreshes automatically every 30 minutes

**Log Levels Not Persisting After Restart:**
- Logger Manager stores managed loggers in `.storage/logger_manager`
- Check file permissions if levels disappear after restart
- Verify the integration is properly loaded on startup
- Check Home Assistant logs for any storage-related errors

## Contributing

This is a learning project and my first HA integration. Contributions, suggestions, and constructive feedback are very welcome:
- Report issues
- Suggest improvements
- Submit pull requests
- Share usage patterns

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**[⬆ Back to Top](#logger-manager)**

Built for Home Assistant developers and power users

</div>
