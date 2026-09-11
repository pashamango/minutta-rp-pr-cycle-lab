# Quota Snapshot Ledger

Record only observed account-level Work/Codex quota snapshots and reset times. Do not infer missing values.

Suggested row schema:

`timestamp_local | weekly_remaining_pct | weekly_reset_at | five_hour_remaining_pct | five_hour_reset_at | source | note`

Primary use: calibrate percentage-point burn over 6–12 hour scheduler experiments. Per-run usage telemetry belongs in bound run artifacts/usage.json when available.
