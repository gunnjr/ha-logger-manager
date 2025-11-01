# Logger Manager

A Home Assistant custom integration that exposes logger state as a sensor.

## Description

Logger Manager provides a sensor (`sensor.logger_levels`) that exposes the current default log level and per-logger overrides from your Home Assistant instance. This allows you to monitor and understand your system's logging configuration through the Home Assistant interface.

## Features

- **Logger State Sensor**: View current default log level and active logger overrides
- **Real-time Monitoring**: 10-second polling to track logger state changes
- **Clean Attributes**: Organized display of default level, logger overrides, and counts

## Installation

### Manual Installation

1. Copy the `custom_components/logger_manager` directory to your Home Assistant `config/custom_components/` directory
2. Add the following to your `configuration.yaml`:

   ```yaml
   sensor:
     - platform: logger_manager
   ```

3. Restart Home Assistant
4. Check **Developer Tools → States** for `sensor.logger_levels`

### HACS Installation

*Coming soon - integration will be available through HACS in a future release*

## Usage

Once installed, the `sensor.logger_levels` entity will be available in your Home Assistant instance with:

- **State**: Current default log level
- **Attributes**:
  - `default`: Default log level
  - `loggers`: Dictionary of logger names and their specific levels
  - `count`: Number of loggers with custom levels

## Requirements

- Home Assistant ≥ 2024.6.0

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Issues and pull requests are welcome at [https://github.com/gunnjr/ha-logger-manager](https://github.com/gunnjr/ha-logger-manager)
