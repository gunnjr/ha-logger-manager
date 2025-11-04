# Step 5 — Proceed Action (Batch)

## Objective
Execute a batch action on all selected items via HA service or event.

## Prompt to Copilot
- Add a prominent **Proceed** button near the basket.
- On click, confirm (“Proceed with {count} items?”).
- Call `my_domain.batch_act` with `{ targets: string[] }` from the selection Set.
- Handle success (toast/snackbar) and error (message; keep selection intact).
- (Optional) Support `dry_run: true` to validate first.

## Acceptance Checklist
- Payload matches selection (verified via backend logs).
- Success shows confirmation; errors do not clear selection.
