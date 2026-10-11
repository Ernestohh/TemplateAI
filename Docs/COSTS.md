# COSTS.md

## Paid assets

The budget is **{{BUDGET_USD}} USD** (TASK.md §16, CLAUDE.md §6).
- With a 0 USD budget there is no paid generation, purchase or API key, and this table must stay empty. If anything ever costs money, it is a rule violation: stop and log it in DECISIONS.md.
- With a paid budget, log every call here and in the asset's `asset.json`. At 80% of the cap use the secondary provider only where the primary has no equivalent; at 100% stop.

| UTC time | Provider | Endpoint / job type | Request or job ID | Purpose | Asset id | Cost USD | Output path | Result |
|---|---|---|---|---|---|---|---|---|

## Claude usage (for the report)

The per-chunk cost reported by `claude -p` is logged automatically in `Docs/AUTODRIVE_LOG.md`. Token totals are in `Docs/TOKENS.json` (`python -I scripts/token_usage.py`). Copy the running totals here at each gate.

| Gate | UTC time | Chunks | Claude cost USD (reported) | Tokens (all / fresh in+out) |
|---|---|---|---|---|
