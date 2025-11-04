# Copilot Build Plan — Home Assistant Lovelace Card: Searchable Multi‑Select w/ Chips

**Goal (IMT v1.0):** Implement a *custom Lovelace card* that:
1) Loads a full list of logger names **once** at card init via an existing WebSocket command (already implemented on your backend).  
2) Provides a **search box** that filters client‑side (debounced).  
3) Shows a **virtualized, checkbox list** of filtered results.  
4) Adds selected items as **chips** (removing them from the results).  
5) Offers a **Proceed** button to act on the *entire selection* (call a backend service or emit an event).

We will build this incrementally in **small, testable steps** (your IMT approach). Every step should compile, render, and be verifiable in HA before moving on.

---

## Constraints & Design Directives (tell Copilot to honor all of these)
- **Tech stack:** LitElement (TypeScript) for the card. Avoid heavy frameworks.
- **Data model:** Full list (≤ 2,000 strings, each ≤ 50 chars) fetched once via HA WebSocket (e.g., `my_domain/get_loggers`). Store in component state.
- **Filtering:** Client‑side, **case‑insensitive substring** match; **debounce** input by 150–250 ms.
- **Virtualization:** Use a lightweight virtual scroller (e.g., `lit-virtualizer`) for the results list. Do not render all items at once.
- **Selection model:** Maintain a `Set<string>` of selected IDs. Items in the selection **must not** appear in the results list.
- **Chips:** Selected items appear as chips with an ✕ remove affordance.
- **Styling:** **Inherit Home Assistant look & feel**. Use HA CSS variables, fonts, spacing, and theme tokens. **Do not hardcode colors.**
- **Accessibility:** Proper ARIA roles for combobox/listbox; keyboard navigation (↑/↓, Enter to select, Esc to clear/close).
- **Performance:** Keep renders under 16ms; avoid large attribute blobs; no polling.
- **Actions:** Proceed button triggers a backend **service call** (e.g., `my_domain.batch_act`) passing the full selected list (or emits a `CustomEvent` the dashboard can handle). Handle `supports_response=True` if implemented.
- **Resilience:** Show empty/error states, and a Refresh action that re-fetches when needed (uses returned `version`/hash to decide whether to replace cache).

---

## File/Module Structure (ask Copilot to scaffold)
- `src/ha-logger-multiselect-card.ts` — main custom card (LitElement)
- `src/types.ts` — small shared types/interfaces (logger item, WS payloads)
- `src/search.ts` — pure functions for filtering/matching (unit-testable)
- `src/state.ts` — minimal in‑card state helpers (selection set ops, debounce)
- `package.json`, `tsconfig.json`, `rollup`/`vite` config as needed
- **Registration:** Standard custom-card registration header and `customElements.define(...)`

> **Note:** This plan assumes you already know how to load a custom card into HA (www/community or HACS dev workflow).

---

## Step‑By‑Step Build Prompts for Copilot

### Step 0 — Card Skeleton & Theming
**Prompt to Copilot:**  
- Create a LitElement custom card named `ha-logger-multiselect-card` (TypeScript).  
- Expose `set hass(hass: HomeAssistant)` to receive HA connection.  
- Render an empty container with a card header “Logger Picker”.  
- Import and apply Home Assistant theme variables (e.g., `--primary-text-color`, `--ha-card-background`, spacing tokens).  
- Ensure the card is responsive (mobile friendly), supports dark mode automatically, and uses shadow DOM safely.

**Acceptance:** Card loads in a dashboard as a blank shell with HA styling.

---

### Step 1 — One‑Time WebSocket Fetch & Local Cache
**Prompt to Copilot:**  
- On first update/connected callback, call the existing HA WebSocket command (e.g., `my_domain/get_loggers`).  
- Store the full array in a private field (e.g., `_allLoggers: string[]`).  
- Also expose `_version?: string|number` from the response for future refresh decisions.  
- Show three states in UI: “Loading…”, “Loaded N items”, “Error (retry)”.

**Acceptance:** On load, I see “Loaded N items” (N ≈ size of backend list).

---

### Step 2 — Search Input + Debounced Client Filter
**Prompt to Copilot:**  
- Add a search text input at the top of the card (placeholder: “Search loggers”).  
- Debounce user input by ~200ms.  
- Implement a pure function `filterLoggers(all: string[], q: string, exclude: Set<string>): string[]` that returns matches **excluding** anything already selected.  
- Render a small result count (“128 matches”) below the input.

**Acceptance:** Typing updates match count without lag.

---

### Step 3 — Virtualized Results List w/ Checkboxes
**Prompt to Copilot:**  
- Add a **virtualized** scroll list beneath the search input (visible 8–12 rows).  
- Each row shows a checkbox + label (the logger string).  
- Keyboard: up/down to move focus; Enter/Space to toggle.  
- When a row is checked, add to selection set and remove it from results.  
- Provide a “Select all (filtered)” link that toggles all visible matches. Clarify scope in the UI.

**Acceptance:** I can select multiple matches quickly; list remains smooth at 1,000+ items.

---

### Step 4 — Selection Basket (Chips) + Remove
**Prompt to Copilot:**  
- Add a right‑hand (or bottom on mobile) **selection area** showing chips for each selected item (label + ✕).  
- Display a badge: **Selected: {count}**.  
- Clicking ✕ removes the item from selection and returns it to results.  
- Provide “Clear all” for the basket.  
- Ensure virtual list recomputes efficiently when selection changes.

**Acceptance:** Chips reflect my choices; removing a chip restores it to the result set.

---

### Step 5 — Proceed Action (Batch)
**Prompt to Copilot:**  
- Add a prominent **Proceed** button near the selection area.  
- On click: call a backend **service** (e.g., `my_domain.batch_act`) with `{ targets: string[] }` built from the selection set.  
- Show a confirmation dialog that summarizes the count before sending.  
- On success: toast/snackbar with success count; on error: show message and keep selection intact.  
- Prepare for `dry_run` mode (optional boolean) to validate before final run.

**Acceptance:** Proceed sends the correct list; success/error UX is clear.

---

### Step 6 — Refresh Handling & Empty/Error States
**Prompt to Copilot:**  
- Add a small “↻ Refresh list” control.  
- Call the same WS endpoint; if `version` is new, replace cache, re-run filter.  
- Define and display three empty states: “Start typing to search”, “No matches”, “No data loaded”.  
- Esc clears search; Cmd/Ctrl+A selects all **filtered** items.

**Acceptance:** Refresh works; empty states look intentional.

---

### Step 7 — Accessibility & Keyboard Nav
**Prompt to Copilot:**  
- Apply correct ARIA roles: `combobox` for search input wrapper, `listbox` for results, `option` rows, `aria-selected`, and chip `button` roles.  
- Focus management: Enter focuses list on first item; Esc returns focus to search.  
- Announce count changes to screen readers (aria‑live region).

**Acceptance:** Keyboard-only operation is smooth; roles validate in Lighthouse/axe.

---

## Styling Guidance (for Copilot)
- Use HA CSS variables (examples):  
  - `--primary-text-color`, `--secondary-text-color`  
  - `--ha-card-background`, `--card-background-color`  
  - `--divider-color`, `--mdc-theme-primary`  
  - `--control-border-radius`, `--spacing`, `--ha-chip-border-radius`
- Typography: inherit from HA; do **not** set custom fonts.  
- Spacing: use consistent 8px multiples (or HA `--spacing`).  
- States: use HA focus outlines; keep high contrast for accessibility.  
- **No hardcoded colors/themes.** Respect light/dark modes automatically.

---

## Service Contract (for Proceed)
- Default: call `my_domain.batch_act` with `{ targets: string[] }`.  
- Optional: support `{ dry_run: true }` to preview and return `{ valid[], invalid[] }`.  
- Optional long‑running jobs: return `{ job_id }` and poll via WS `get_job_status`.

---

## Test Checklist (each step)
- Card compiles and loads in HA panel.  
- Initial WS fetch occurs exactly once per mount; handles reconnect.  
- Filtering remains <16ms per keystroke at 2,000 items.  
- Virtualized list never renders all nodes; scroll is smooth on mobile.  
- Selection survives search changes; “Select all (filtered)” behaves as labeled.  
- Proceed sends the right payload; errors do not lose selection.  
- A11y roles and keyboard flows pass basic audits.  
- Theming matches HA in light/dark; no hardcoded styles.

---

## Copilot “Do/Don’t”
**Do**
- Keep functions small and pure where possible (`filterLoggers`, selection ops).  
- Write minimal types in `src/types.ts`.  
- Add inline JSDoc on public methods and events.  
- Guard against undefined HA connection before sending messages.

**Don’t**
- Don’t fetch on every keystroke.  
- Don’t render unvirtualized long lists.  
- Don’t ship hardcoded colors/margins or external heavy UI libs.  
- Don’t store large data on entities/attributes.

---

## Ready‑to‑Paste Seed Prompt for Copilot
> *“Create a Home Assistant custom Lovelace card in TypeScript using LitElement named `ha-logger-multiselect-card`. The card must fetch a full list of logger names once via HA WebSocket (`my_domain/get_loggers`) and store them in component state. Add a debounced search input that filters the list client‑side (case‑insensitive substring), a **virtualized** checkbox list of matches (8–12 visible rows), and a selection **chip** area for chosen items. Items in the selection must not appear in results. Add ‘Select all (filtered)’, ‘Clear all’, a count badge, empty states, and a **Proceed** button that calls `my_domain.batch_act` with `{targets: string[]}`. Inherit Home Assistant styling using theme CSS variables and support dark mode. Include keyboard navigation and appropriate ARIA roles. Build this in small, compiling steps and stop after each step to let me test before continuing.”*

---

**That’s the plan.** Use these prompts step‑by‑step; verify each acceptance criterion before moving on.
