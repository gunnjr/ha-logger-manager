# Home Assistant: Searchable Logger List UI (Design Overview)

## Objective
Create a searchable dropdown list for selecting loggers within a Home Assistant custom integration. The dataset is limited to ~2000 items (each ≤50 chars) and changes infrequently. The list is fetched once at page load via a WebSocket API and filtered client-side for fast searching.

---

## Backend Design

### Data Retrieval
- Retrieve the list of registered loggers from Python’s logging registry.
- Normalize entries: trim, deduplicate, and sort.
- Include both original and lowercase forms for case-insensitive search.

### WebSocket API
- Expose a command (e.g., `my_domain/get_loggers`) returning:
  - `items`: array of strings.
  - `version`: integer or hash for cache validation.
- Optional `refresh` command for on-demand re-fetch.

### Caching Strategy
- Store `{items, version, timestamp}` in `hass.data`.
- TTL: 10–30 minutes, or refresh on request.
- Rebuild only when expired, explicitly requested, or triggered by HA events.

### Permissions
- Restrict to admin users (optional, but safer).
- Payload size: ~100 KB for 2000 × 50-char entries — easily manageable.

### Error Handling
- Gracefully handle lookup failures with empty `items` + `error` field.
- Log debug info for troubleshooting.

---

## Frontend Design (Custom Lovelace Card)

### Load Behavior
- Fetch `items` + `version` on card initialization.
- Cache locally (in-memory and optionally in `localStorage` keyed by `version`).
- Refresh on demand or when backend `version` changes.

### Search Implementation
- Client-side substring filtering (case-insensitive).
- Debounce input (150–250 ms).
- No backend round trips during search.

### Rendering
- Virtualized dropdown list for performance (e.g., using `lit-virtualizer`).
- Display only ~8–12 visible rows; scroll within dropdown.
- Show result count (“128 matches”).

### User Experience
- Keyboard navigation (arrow keys, Enter, Esc).
- Highlight matched substring.
- Empty states: “Start typing to search”, “No matches”, and a Refresh link.
- Mobile-friendly layout with touch-safe controls.
- Proper accessibility attributes (`aria-*`).

### Selection Handling
- On selection:
  - Emit custom event OR
  - Call backend service (e.g., to set log level).
- Optional: write selection to `input_text` helper for automation visibility.

### Refresh Support
- Provide a “↻ Refresh list” control calling backend `refresh` command.
- Compare `version` before updating local cache.

---

## Why This Approach Works
- **Performance:** One-time fetch of ~100 KB; client-side filtering is instant.
- **Simplicity:** No entities, no recorder bloat, minimal backend logic.
- **UX:** Type-ahead search with virtualization for smooth experience.
- **Maintainability:** Clear separation between data fetch (backend) and UI behavior (frontend).

---

## Optional Enhancements
- **Recent/Favorites:** MRU section persisted in localStorage.
- **Scoped Search:** Toggle between “contains” and “starts with”.
- **Copy to Clipboard:** Quick copy button for selected logger.
- **Batch Actions:** Multi-select for bulk operations.

---

## Test Plan
1. Populate with 2000 dummy logger names and benchmark:
   - Backend fetch < 50 ms.
   - WS round-trip < 200 ms LAN.
2. Validate UI responsiveness (<16 ms per keystroke).
3. Test reconnect (WS drop/reconnect).
4. Verify permissions and empty/error handling.

---

## Summary
This design delivers a smooth, searchable dropdown for large but stable datasets without bloating HA state. It uses a single WebSocket fetch, client-side caching, and a virtualized UI for excellent performance across desktop and mobile.
