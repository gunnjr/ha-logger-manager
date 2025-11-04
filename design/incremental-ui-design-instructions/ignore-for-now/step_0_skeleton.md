# Step 0 — Card Skeleton & Theming

## Objective
Create the LitElement card shell with HA look & feel, responsive layout, and shadow DOM.

## Prompt to Copilot
- Scaffold a TypeScript custom card named `ha-logger-multiselect-card` using LitElement.
- Implement `set hass(hass: HomeAssistant)` to receive HA connection.
- Render a card header “Logger Picker” and an empty body container.
- Apply HA theme via CSS variables (no hardcoded colors/fonts).
- Ensure responsive layout and dark-mode compatibility.

## Acceptance Checklist
- Card loads into a Lovelace dashboard without errors.
- Header renders; body area is present.
- Styles match HA themes (light/dark).
