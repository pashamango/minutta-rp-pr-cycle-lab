# Codex Quota Governor v0

Purpose: maximize verified useful work before the next Work/Codex reset without exhausting the shared allowance early or leaving a large unused remainder.

## Primary meters

Use account quota meters when observable:

- `weekly_remaining_pct`
- `weekly_reset_at`
- `five_hour_remaining_pct`
- `five_hour_reset_at`

Per-run token counters are secondary telemetry because Work/Codex allowance burn is model/task/settings dependent and may not map linearly to raw tokens.

## Per-run usage record

When observable, bind telemetry to `(task_id, source_sha256, lease_id)` and record:

- scheduler/steward identity
- actual model/provider
- actual reasoning effort
- started_at / finished_at
- input/output/reasoning/tool tokens if exposed
- retries
- terminal semantic state
- artifacts / PR / commit
- quota snapshot before/after when available

Never estimate missing counters.

## Burn-rate control

Let:

`W = weekly remaining percentage points`
`R = desired weekly reserve at reset (default 8 percentage points)`
`H = hours until weekly reset`

Then the sustainable average weekly burn is approximately:

`b_target = max(0, W - R) / max(H, 1)` percentage points/hour.

Estimate `b_observed` from real quota snapshots over a multi-hour interval, not from PR count.

Initial staged policy:

- keep GPT-5.6 Luna / Light as default;
- no silent model substitution;
- if `b_observed > 1.25 * b_target`, reduce new Codex admissions; specialist schedulers continue Git/web/local work without consuming Codex;
- if `b_observed < 0.60 * b_target` for >= 6 hours and the 5-hour window has comfortable headroom, permit one additional bounded Codex lane or a documented step-up experiment;
- between those bands, hold capacity steady and keep measuring;
- never increase capacity based only on lines/PRs/commits.

The 5-hour meter is a short-term circuit breaker. Keep at least ~20% headroom unless a deliberate end-of-window experiment justifies otherwise.

## First calibration experiment

Run exactly one additional hourly specialist (Research Scout) for 6–12 hours while leaving other capacity unchanged. Capture account quota snapshots at the start and end of the interval. Compare useful Git evidence and downstream Codex admissions against percentage-point burn.

If automated access to account quota meters is unavailable, one human snapshot at interval boundaries is acceptable; do not invent telemetry.

## Routing under quota pressure

Quota pressure should change routing, not kill research:

`specialist -> web/Git analysis -> candidate handoff`

Only the Research Market admits scarce Codex execution. When Codex budget is tight, preserve candidates in Git for later execution or route to tested local/external low-cost lanes when available and authorized.
