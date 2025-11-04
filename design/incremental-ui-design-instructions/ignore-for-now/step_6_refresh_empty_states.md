# Step 6 — Refresh & Empty/Error States

## Objective
Support data refresh and well-defined empty/error UX.

## Prompt to Copilot
- Add a small “↻ Refresh list” action.
- Re-fetch WS; if `version` changed, replace cache and re-filter.
- Define empty states: “Start typing to search”, “No matches”, “No data loaded”.
- Esc clears search; Cmd/Ctrl+A selects all **filtered** items.

## Acceptance Checklist
- Refresh works and updates list when backend changes.
- Empty/error states display clearly and behave correctly.
