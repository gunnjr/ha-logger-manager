# Step Cards Pack — Home Assistant Lovelace Card (Searchable Multi‑Select with Chips)

This pack breaks the build into **small, testable steps** for Copilot. Work through them in order. After each step, **stop and verify** the Acceptance Checklist before proceeding.

## Global Constraints (apply to every step)
- **LitElement + TypeScript** custom card (`ha-logger-multiselect-card`).
- **One-time WS fetch** of all loggers (`my_domain/get_loggers`), then **client‑side** filtering.
- **Virtualized results** list; do **not** render all rows.
- **Selection Set** of chosen items; selected items must not appear in results.
- **Home Assistant styling** only (CSS variables, tokens; no hardcoded colors).
- **A11y + keyboard** support.
- Keep renders fast (<16ms), avoid polling, handle empty/error/refresh.

If you haven’t already, load the card via your dev workflow (www/community or HACS dev).

---

## Files in this pack
- step_0_skeleton.md
- step_1_ws_fetch.md
- step_2_search.md
- step_3_virtual_list.md
- step_4_selection_chips.md
- step_5_proceed_action.md
- step_6_refresh_empty_states.md
- step_7_accessibility_keyboard.md
