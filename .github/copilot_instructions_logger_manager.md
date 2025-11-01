# Copilot Instructions — Logger Manager (Home Assistant)

## Collaboration Guidelines

### Before Making Changes

- **Always explain** what you're about to do before making multiple file changes
- **Get explicit consent** before proceeding with large batches of changes
- **Break down work** into logical chunks and confirm each step
- **Ask questions** if anything in the requirements is unclear

### Communication Style

- Be concise but thorough in explanations
- Highlight any assumptions you're making
- Point out potential issues or alternatives you see
- Wait for confirmation before proceeding to next milestone

### Change Management

- Make changes incrementally following the IMT approach
- Test/verify each milestone before moving to the next
- Don't bundle unrelated changes together

## Workspace Configuration Preferences

### Linting & Formatting

- **Disable linting** for the following files:
  - `.github/copilot-instructions.md` (this file)
  - `README.md` (documentation formatting flexibility)
  - `CHANGELOG.md` (release note formatting)
  - `LICENSE` (standard license text)

### Editor Settings

- Use `.editorconfig` for consistent formatting
- Prefer spaces over tabs (2-space indentation for YAML, 4-space for Python)
- UTF-8 encoding with LF line endings
- Trim trailing whitespace

### File Organization

- Keep project root clean (only essential config files)
- All integration code in `custom_components/logger_manager/`
- Documentation and meta files in root level
- CI/CD configurations in `.github/`

## Context

We are building a **Home Assistant custom integration** named **Logger Manager**. It provides a sensor (`sensor.logger_levels`) that exposes the current **default log level** and **per-logger overrides**. Later milestones will add services, presets, and a UI card.\
Use an **Incremental & Minimally Testable (IMT)** approach: deliver the smallest working piece at each step.

---

## Milestone 0 — Repository Setup

- Create a new repository: `ha-logger-manager`
- Add standard scaffolding for a Home Assistant custom integration published via HACS.

### Structure

```
ha-logger-manager/
├─ custom_components/
│  └─ logger_manager/
│     ├─ __init__.py
│     ├─ manifest.json
│     └─ sensor.py
├─ .gitignore
├─ .editorconfig
├─ README.md
├─ LICENSE
├─ hacs.json
└─ copilot-instructions.md
```

### Metadata

- Repo: `ha-logger-manager`
- Friendly name: **Logger Manager**
- Owner: `gunnjr`
- License: MIT
- Target platform: Home Assistant ≥ 2024.6

---

## Milestone 1 — Basic Files

Generate the following minimal files:

### `.gitignore`

Include Python, build, and editor artifacts (`__pycache__/`, `.DS_Store`, `.idea/`, `dist/`, `build/`).

### `.editorconfig`

Use spaces, UTF-8, LF endings, trim trailing whitespace.

### `LICENSE`

Use MIT License.

### `README.md`

Brief description: integration that exposes HA logger state as a sensor. Include manual install instructions.

### `hacs.json`

```json
{
  "name": "Logger Manager",
  "render_readme": true,
  "country": "US",
  "domains": ["sensor"],
  "homeassistant": "2024.6.0",
  "iot_class": "Local Polling",
  "categories": ["integration"]
}
```

### `manifest.json`

```json
{
  "domain": "logger_manager",
  "name": "Logger Manager",
  "version": "0.1.0",
  "documentation": "https://github.com/gunnjr/ha-logger-manager",
  "issue_tracker": "https://github.com/gunnjr/ha-logger-manager/issues",
  "requirements": [],
  "codeowners": ["@gunnjr"],
  "iot_class": "local_polling"
}
```

### `sensor.py`

Implement a polling sensor that reads `hass.data['logger']`.

- State: default log level
- Attributes: `default`, `loggers` dict, `count`

### `__init__.py`

Minimal placeholder comment.

---

## Milestone 2 — Git Initialization

```
git init
git add .
git commit -m "feat: initial scaffold for Logger Manager"
git branch -M main
git remote add origin git@github.com:gunnjr/ha-logger-manager.git
git push -u origin main
```

---

## Milestone 3 — Local Verification

1. Copy `custom_components/logger_manager` into `/config/custom_components/` in Home Assistant.
2. Add to `configuration.yaml`:

   ```yaml
   sensor:
     - platform: logger_manager
   ```

3. Restart Home Assistant.
4. Confirm `sensor.logger_levels` appears under **Developer Tools → States**.

---

## Milestone 4 — Basic Service: `apply_levels`

Add a new service defined in `services.yaml` and registered in `__init__.py`.

- Service name: `logger_manager.apply_levels`
- Parameters:
  - `level`: string (critical/error/warning/info/debug/notset)
  - `loggers`: list of strings
- Action: internally call `logger.set_level` with `{logger_name: level}` mapping.

---

## Milestone 5 — Release & HACS Prep

- Tag version `v0.1.0`
- Add badges (version, license) to `README.md`
- Add icons (`icon.png`, `logo.png`) and `CHANGELOG.md`
- Ensure `manifest.json` URLs are valid and public.

---

## Milestone 6 — Future Enhancements

- Lovelace card for selecting levels and loggers
- Presets and “reset to defaults” actions
- Auto-discovery of logger namespaces
- Admin-only access control

---

## Technical Specifics (Concise Add‑Ons)

### Sensor polling & resilience (`sensor.py`)

Use a light polling interval and handle missing keys safely.

```python
from datetime import timedelta
SCAN_INTERVAL = timedelta(seconds=10)

DOMAIN = "logger"  # built‑in HA logger integration

class LoggerInspectorSensor(SensorEntity):
    _attr_name = "Logger Levels"
    _attr_icon = "mdi:file-document-alert"
    _attr_should_poll = True

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    def update(self) -> None:
        data = self.hass.data.get(DOMAIN) or {}
        default = data.get("default") or "unknown"
        loggers = dict(sorted((data.get("loggers") or {}).items()))
        self._attr_native_value = default
        self._attr_extra_state_attributes = {
            "default": default,
            "loggers": loggers,
            "count": len(loggers),
        }
```

### Service schema & call (`__init__.py` + `services.yaml`)

Validate inputs with `voluptuous` and delegate to core `logger.set_level`.

`services.yaml`

```yaml
apply_levels:
  name: Apply Levels
  description: Set a log level for one or more logger names.
  fields:
    level:
      required: true
      selector:
        select:
          options: [critical, error, warning, info, debug, notset]
    loggers:
      required: true
      selector:
        object:
```

`__init__.py`

```python
from __future__ import annotations
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

DOMAIN = "logger_manager"
LEVELS = ["critical", "error", "warning", "info", "debug", "notset"]
SCHEMA = vol.Schema({
    vol.Required("level"): vol.In(LEVELS),
    vol.Required("loggers"): [str],
})

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async def handle_apply_levels(call: ServiceCall) -> None:
        data = SCHEMA(call.data)
        level = data["level"]
        names = data["loggers"]
        mapping = {name: level for name in names}
        await hass.services.async_call("logger", "set_level", mapping, blocking=True)
    hass.services.async_register(DOMAIN, "apply_levels", handle_apply_levels)
    return True
```

### Minimal CI for validation (optional)

Add both **hassfest** and **HACS** checks.

`.github/workflows/validate.yml`

```yaml
name: validate
on: [push, pull_request]
jobs:
  hassfest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: home-assistant/actions/hassfest@master
  hacs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hacs/action@main
```

### Minimal test guidance (later)

- Use `pytest-homeassistant-custom-component`.
- Test loads of the sensor platform and asserts:
  1. `sensor.logger_levels` exists,
  2. mocking `hass.data['logger']` updates state/attributes as expected.

---

## Technical Questions & Considerations (for later review)

### Data Access Verification

- **Question**: Confirm `hass.data["logger"]` is the correct path to access HA's internal logger state
- **Action**: Verify during Milestone 3 testing that this data structure exists and contains expected keys

### Service Schema Refinement  

- **Question**: Service schema shows `selector: object` for loggers field - consider if `text` with `multiple: true` would be more user-friendly
- **Current**: `selector: object`  
- **Alternative**: `selector: text: multiple: true` for comma-separated logger names

### Sensor Discovery Strategy

- **Question**: Should the sensor be auto-discovered or require manual configuration?
- **Current**: Manual configuration via `configuration.yaml`
- **Alternative**: Auto-discovery during integration setup (no yaml config needed)

### Performance Considerations

- **Question**: Is 10-second polling optimal for logger data that rarely changes?
- **Alternative**: Event-based updates or longer polling interval (30-60 seconds)

*Note: These items can be addressed/tested during implementation milestones.*
