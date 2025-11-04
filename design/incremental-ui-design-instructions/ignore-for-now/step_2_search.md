# Step 2 — Search Input + Debounced Client Filter

## Objective
Add a debounced search field that filters locally (case‑insensitive) excluding selected items.

## Prompt to Copilot
- Add a text input (“Search loggers…”).
- Debounce input ~200ms.
- Implement `filterLoggers(all: string[], q: string, exclude: Set<string>): string[]`.
- Display a small result count (“128 matches”).

## Acceptance Checklist
- Typing updates match count smoothly (no WS calls).
- Empty query returns all items (minus selected).
