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

## Version 1.1.1

### What's New

1. **Bug Fix:**  
   - Fixed issue where pressing return on the config screen submitted the form instead of allowing multiple lines. You can now enter multiple patterns as a YAML list.

2. **Documentation:**  
   - Refreshed README file for clarity and accuracy.

3. **Usability:**  
   - Logger names in the selection bin are now right-justified, making it easier to see the most relevant part of long logger names.

---

## Overview

Logger Manager aims to solve a common frustration for Home Assistant developers and power users: **managing logging levels is tedious**.

## Target Users
**Power Home Assistant users** who need to leverage HA debug logging for:
- Custom integration development
- Issue diagnosis and troubleshooting
- System optimization and monitoring
- Integration debugging and testing

## The Problem
> **Power HA users need precise, discoverable, and fast logger control for debugging/development, but current methods are either too slow (configuration.yaml + reboot), imprecise (setting default logger level), too obscure (non-discoverable loggers), or too time consuming (writing use-case specific logger control scripts), forcing users to miss out on otherwise helpful debug logging or deal with unmanageably verbose default debug logging.**

## The Solution

Logger Manager aims to solve this with a **power user targeted** user interface that makes it easy to discover, select, and configure loggers. Using the provided lovelace card, users can quickly dial in logging specific to their task or challenge.

## Installation

### HACS Custom Repository (Current Method)
1. Open HACS → Integrations
2. Click the three dots (⋮) in the top-right corner
3. Select "Custom repositories"
4. Add repository URL: `https://github.com/gunnjr/ha-logger-manager`
5. Category: `Integration`
6. Click "Add"
7. Find "Logger Manager" in the list and click "Download"
8. Restart Home Assistant
9. Continue to [Setup](#setup) below

### HACS Default Repository (planned)

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

### Step 2: Add the UI Card to any Dashboard

The card resource is automatically registered when you add the integration. To use it:

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

## Solution Components
### How the components work together
The UI is the primarily intended value of this integration, supported by the underlying sensor and services.  However, the unterlying componts are availible for direct access and can be useful on a stand-alone basis (especially for automations), **the UI card is the primary reason to use Logger Manager**.
### 1. Interactive Lovelace Card
- Deployable to any lovelace dashboard
- Searchable multi-select dropdown of available loggers
- Easy logger level changes with visual feedback (Critical, Error, Warning, Info, Debug, Notset)
- Bulk operations - modify multiple loggers at once
- **Logger names in the selection bin are now right-justified for better readability**

<table>
<tr>
<td width="50%">
<img src="screenshots/logger-card-overview.png" width="100%" alt="Logger Manager Card Overview"/>
<p align="center"><em>Logger Manager Card</em></p>
</td>
<td width="50%">
<img src="screenshots/logger-dropdown-search.png" width="100%" alt="Logger Dropdown Search"/>
<p align="center"><em>Filtered by search string</em></p>
</td>
</tr>
</table>

### 2. Persistent State Sensor (`sensor.logger_levels`)
- Tracks which loggers you've customized and their current levels
- Shows default log level and count of managed loggers
- Powers the UI card and enables automations

![Logger Sensor State](screenshots/logger-sensor-state.png)

### 3. Management Services
- `logger_manager.apply_levels` - Programmatically change and track logger levels
- Services maintain managed logger state across HA restarts
- Enable automation-based logging control
- Similar to HA's built-in `logger.set_level` but maintains the list of managed loggers on the sensor for use by the UI and otherwise.

```yaml
service: logger_manager.apply_levels
data:
  level: debug
  loggers:
    - homeassistant.components.zha
    - custom_components.logger_manager
```

### Availible loggers: Common Logger Names
The list of availible loggers is currenly contrained to those for envisioned usecases. The critera is currently hardcoded as follows. The developer intends to make this configurable.
### 1. Core integrations
Loggers with names of containing: `homeassistant`
Examples: `homeassistant.components.zha`, `homeassistant.components.mqtt`

### 2. Custom integrations
Loggers with names containing: `custom_components`
Examples: `custom_components.logger_manager`, `custom_components.hacs`

### 3. Commonly used system loggers
Loggers with names containing: `asyncio`, `aiohttp`, `urllib3`, `requests`, `aiodns`, `aiofiles`, and `websockets`

## Anticipated Enhancements
As time permits, future versions will be enhanced to provide:

### Logger Management UI
- View all managed loggers in a dedicated card
- Edit or remove managed logger levels

### Default Log Level Control
- UI to change Home Assistant's default log level
- Currently can only be changed via configuration.yaml

### Integrated Dashboard
- Pre-built dashboard combining all Logger Manager features
- One-stop shop for all logging needs

## Limitations

- Loggers must exist for level changes to take effect
- Some third-party libraries may not follow HA logging conventions
- The sensor updates every 10 seconds, not instantly
- WebSocket API for logger discovery caches results for 30 minutes
- Logger discovery patterns are currently hardcoded

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
