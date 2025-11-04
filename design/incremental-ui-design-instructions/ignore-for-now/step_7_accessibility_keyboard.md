# Step 7 — Accessibility & Keyboard Navigation

## Objective
Make the control accessible with ARIA roles and logical focus flow.

## Prompt to Copilot
- Apply ARIA roles: combobox (wrapper), listbox (results), option (rows), buttons on chips.
- Maintain `aria-selected` on active options.
- Focus flow: Enter moves focus to first result; Esc returns to search.
- Add an `aria-live` region to announce match count changes.

## Acceptance Checklist
- Keyboard-only operation works end-to-end.
- Basic axe/Lighthouse checks pass (roles, names, contrast via HA theme).
