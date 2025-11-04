# Step 1 — One‑Time WebSocket Fetch & Local Cache

## Objective
Fetch the full logger list once at mount and cache it in component state.

## Prompt to Copilot
- On first render/connected, call `my_domain/get_loggers` over HA WebSocket.
- Store results in `_allLoggers: string[]` and `_version?: string|number`.
- Show basic states: Loading / Loaded (N items) / Error (with Retry).

## Acceptance Checklist
- Loading indicator appears then resolves.
- “Loaded N items” shows the correct count.
- Error path displays retry and recovers.
