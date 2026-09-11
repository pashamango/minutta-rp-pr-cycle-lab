# Hourly Codex Scheduler Quota Review

Date: 2026-09-11
Observation window: 2026-09-10 16:29Z to 2026-09-11 16:29Z
Repository: pashamango/minutta-rp-pr-cycle-lab

## Conclusion

One active hourly scheduler is producing strong research throughput, but the evidence is insufficient for a trustworthy token forecast. The safe decision is to add capacity gradually, not all four schedulers at once.

Observed GitHub output in the window:

| Metric | Count |
|---|---:|
| New PRs | 5 |
| PR commits | 9 |
| Changed files | 27 |
| Added lines | 1,653 |
| Merges | 0 |

PRs #81, #87, #89, #91 and #93 were created between 02:15Z and 15:25Z on September 11. All remained open; they are reviewable research outputs, not merged production releases.

A simple throughput projection for one scheduler is approximately 8–9 PRs/day and 60 PRs/week, with roughly 15 commits/day and 100+ commits/week. This is an output projection, not a token projection.

## Token forecast limitation

GitHub records durable outputs but does not expose Codex quota burn. Available Drive-backed run artifacts did not provide a complete, reliable per-run token ledger for this hourly batch. Therefore it would be unsafe to invent tokens-per-PR or multiply an assumed value by five.

The correct quantity to measure is:

verified useful output / actual Codex tokens

Separate accounting is needed for model reasoning, tool calls, retries, failed starts, local computation, settlement and recovery.

The first scheduler's tasks are heterogeneous: recovery analysis, public-data retrieval, image processing and QR experiments. Local computation may dominate some runs, while model reasoning or retries dominate others.

## Model evidence

The intended strict-economy default is Luna Light, but model identity has not been reliably enforced:

- #75 required GPT-5.6 Luna.
- Its bound result says the trusted runtime selected gpt-6-astra at low effort.
- No intended research started for #75.
- #77 records local Gemma timeout and external Gemini requiring explicit authentication.
- New Issue text requesting Luna is not evidence that Luna actually ran.

Thus the first required improvement is model identity observability and enforcement, not default step-up. If a task requires Luna and Astra is selected, the run should fail as MODEL_POLICY_MISMATCH before substantive work.

## Scaling estimate

The observed interval produced 5 PRs in about 14 hours. Naively, five identical schedulers would produce 40–45 PR-equivalents/day. That estimate is likely optimistic because schedulers share one quota pool and may contend for local inference, workspace resources and provider limits.

A scheduler count N is safe only if:

N × measured hourly burn × hours until reset <= remaining quota - safety margin

The missing variable is measured hourly burn. Until it exists, the responsible forecast is a staged experiment.

## Recommendation

Keep Luna Light as default. Add one extra scheduler first and observe 6–12 hours. If burn is stable and projected depletion remains below the safety margin, move to two schedulers for a complete measurement interval. Add the remaining three only after the two-scheduler measurement confirms headroom.

Do not enable general default step-up. Permit step-up only after a documented Light reasoning bottleneck, with a fixed ceiling and a separate recorded attempt. Never silently substitute another model.

## Smallest architecture change

Add a dispatcher-written usage.json for every run, bound to task_id, source_sha256 and lease_id. Record actual model/provider, effort, timestamps, input/output/reasoning/tool token counters when exposed, retry count, terminal state, scheduler identity and reset-window identifier.

Add a quota governor that projects depletion before admitting each hourly run and fails closed as QUOTA_GUARD_BLOCKED. It must not silently degrade model identity or consume the remaining pool.

## Negative finding

A PR with 500 lines may cost fewer tokens than a short blocked run that spent its budget in hidden reasoning or retries. The mailbox currently measures durable work much better than scarce-resource consumption.

## Final decision

Do not activate all four additional schedulers yet. Run a two-scheduler measurement phase, beginning with one additional scheduler, while keeping Luna Light and enforcing actual model identity.
