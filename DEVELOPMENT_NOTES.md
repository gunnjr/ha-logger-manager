# Logger Manager Development Notes

## Current Status (November 2, 2025)

### What's Working ✅
- **Backend Integration**: Complete and functional
  - `sensor.py`: Logger discovery working (571 loggers found, filtered to ~19 for UI)
  - `__init__.py`: Services registered and working
  - `services.yaml`: Documentation complete
  - Database size optimization: Resolved >16KB sensor attribute warnings

- **UI Card**: Basic functionality working
  - `logger-manager-card.js`: Loads and displays correctly
  - Card shows "19 loggers available"
  - Dropdown populates with logger names
  - Service integration implemented

### Current Issue ❌
**Dropdown UX Problem**: The logger dropdown appears when clicked but disappears too quickly for user selection. User cannot actually select a logger from the list.

**Root Cause Discovered**: `ha-generic-picker` component access issue in custom cards.

**V2 Card Error**: 
```
Uncaught (in promise) TypeError: Cannot read properties of undefined (property 'render') at ha-generic-picker.ts:102
```

## Research Findings: ha-generic-picker Access Methods

### Option 1: Direct Import Method ⚠️
**Status**: Not straightforward for custom cards
**Findings**:
- `ha-generic-picker` is used extensively in HA core (entity-picker, user-picker, etc.)
- Requires proper import: `import "../ha-generic-picker"`
- HA core uses: `import type { HaGenericPicker } from "../ha-generic-picker"`
- **Problem**: Import paths not accessible to external custom cards
- **Possible Solution**: Need to research if component loads after HA initialization

**Import Pattern from HA Core**:
```typescript
import "../ha-generic-picker";
import type { HaGenericPicker } from "../ha-generic-picker";

// Usage in render():
<ha-generic-picker
  .hass=${this.hass}
  .getItems=${this._getItems}
  .rowRenderer=${this._rowRenderer}
  .searchFn=${this._searchFn}
  @value-changed=${this._valueChanged}
></ha-generic-picker>
```

### Option 2: Decluttering Card Method ✅
**Status**: Proven solution for accessing internal HA components
**Repository**: https://github.com/custom-cards/decluttering-card
**How it works**:
- HACS add-on that creates reusable card templates
- Provides access to internal HA components not normally available to custom cards
- Uses HA's own component loading system through templates

**Implementation Approach**:
1. Install Decluttering card from HACS
2. Create template that uses `ha-generic-picker`
3. Pass our logger data as template variables
4. Template renders using real HA components

**Pros**:
- ✅ Proven to work with internal HA components
- ✅ No import/loading issues
- ✅ Handles component lifecycle properly
- ✅ Active maintenance and community support

**Cons**:
- ❌ Adds external dependency
- ❌ More complex setup process
- ❌ Template syntax vs direct code

**Template Structure Example**:
```yaml
# In decluttering_templates:
logger_picker_template:
  card:
    type: custom:ha-generic-picker
    hass: "[[hass]]"
    items: "[[logger_items]]"
    getItems: "[[get_items_fn]]"
    # ... other properties

# In our card usage:
- type: custom:decluttering-card
  template: logger_picker_template
  variables:
    - logger_items: [our logger array]
    - get_items_fn: [our function]
```

### Option 3: Alternative Component (Fallback) 🔄
**Status**: Backup option if others fail
**Components to try**:
- `ha-combo-box` - Available and works in custom cards
- `ha-textfield` with custom dropdown - Manual implementation
- Basic HTML select with enhanced styling

## Recommendation

**Primary Path**: Try Option 1 (Direct Import) first with proper component waiting
**Fallback Path**: Option 2 (Decluttering Card) for guaranteed compatibility  
**Emergency Path**: Option 3 (ha-combo-box) for immediate functionality

**Next Testing Priority**:
1. Research proper `ha-generic-picker` import syntax for custom cards
2. Test component availability timing (wait for HA load)
3. If needed, implement Decluttering card approach
4. Document working solution for future reference

## Next Steps

### Immediate Priority (Next Session)
1. **Fix Dropdown Behavior**
   - Debug why dropdown closes too quickly
   - Likely solutions:
     - CSS z-index/positioning adjustments
     - Event handling review (focus/blur conflicts)
     - Container styling issues
   - Test dropdown persistence and selection

### Validation Steps (After Dropdown Fix)
1. **End-to-End Testing**
   - Select logger from dropdown
   - Change logger level
   - Verify service call works
   - Confirm persistent state changes

### Future Enhancements (Post-MVP)
1. **UI Improvements**
   - Better visual feedback for level changes
   - Current logger states display
   - Bulk operations for multiple loggers

2. **Backend Optimizations**
   - Consider caching mechanism for logger discovery
   - Add more granular logger filtering options

## Technical Architecture

### File Structure
```
custom_components/logger_manager/
├── __init__.py          # Service registration
├── sensor.py            # Logger discovery & state
├── manifest.json        # Integration metadata
└── services.yaml        # Service documentation

www/
└── logger-manager-card.js  # Lovelace UI card
```

### Key Code Components
- **Logger Discovery**: `sensor.py._discover_available_loggers()`
- **UI Population**: `logger-manager-card.js.getAvailableLoggers()`
- **Service Calls**: `apply_levels` service for setting logger levels
- **Data Flow**: Sensor → Card → Service → HA Core

## Development Environment
- **Repository**: github.com/gunnjr/ha-logger-manager
- **Testing**: Symlinked to HA Core 2025.10.0
- **Branch**: main
- **Version**: 0.1.0 MVP

## Important Reminders
- **ALWAYS ask before making code changes** - no exceptions
- User prefers discussion of approach before implementation
- Test changes incrementally, not in large batches
- Keep debug logging minimal in production code

## Recent Learning
- HA has strict database size limits for sensor attributes (16KB)
- Browser caching can mask JavaScript changes - require hard refresh
- Dropdown UI behavior is more complex than basic form styling
- User experience testing is critical for interactive components

---
*Last Updated: November 2, 2025*
*Status: Dropdown behavior debugging needed*