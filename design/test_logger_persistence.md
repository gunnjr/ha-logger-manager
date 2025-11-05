# Logger Persistence Test

## Hypothesis

Based on HA documentation, logger levels set via `logger.set_level` service calls are **NOT** persisted across restarts.

## Test Plan

1. **Check current state**: Use our sensor to see current logger levels
2. **Apply a test change**: Use our service to change a logger level
3. **Verify change**: Confirm the change took effect
4. **Restart HA**: Restart Home Assistant
5. **Check post-restart**: See if the change persisted

## Test Commands

### Step 1: Check current state

```bash
# Check our sensor state
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  http://your-ha-instance:8123/api/states/sensor.logger_levels
```

### Step 2: Apply test change

```bash
# Set custom_components.logger_manager to debug level
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "logger_manager.apply_levels",
    "level": "debug", 
    "loggers": ["custom_components.logger_manager"]
  }' \
  http://your-ha-instance:8123/api/services/logger_manager/apply_levels
```

### Step 3: Verify change

```bash
# Check sensor again to confirm change
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  http://your-ha-instance:8123/api/states/sensor.logger_levels
```

### Step 4: Restart HA

```bash
# Restart via service call
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' \
  http://your-ha-instance:8123/api/services/homeassistant/restart
```

### Step 5: Check post-restart

```bash
# After restart, check if our logger_manager debug level persisted
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  http://your-ha-instance:8123/api/states/sensor.logger_levels
```

## Expected Results

**Pre-restart**: `custom_components.logger_manager` should show as `debug` level in sensor attributes

**Post-restart**: `custom_components.logger_manager` should revert to default level (likely `warning` or `info`), proving service calls don't persist

## Implications

If test confirms our hypothesis:

- HA's `logger.set_level` changes are temporary (memory only)
- Our service changes won't survive restarts
- We need persistent storage to maintain managed logger state
- Users will lose custom levels on restart unless we implement persistence
