# Step 3 — Virtualized Results List w/ Checkboxes

## Objective
Render filtered results with virtualization and checkbox selection.

## Prompt to Copilot
- Use a virtual scroller (e.g., `lit-virtualizer`) for the results list (8–12 visible rows).
- Each row: checkbox + label (logger string).
- Arrow keys navigate; Enter/Space toggles.
- When selected, add to a `Set<string>` and remove from results.
- Provide “Select all (filtered)” / “Clear selection (filtered)”.

## Acceptance Checklist
- Scrolling stays smooth at 1,000+ items.
- Selecting items removes them from the results list.
- “Select all (filtered)” selects only the matches currently shown.
