# Research Scout Finding — pi-smart-router trust boundary

Date: 2026-09-14
Status: AUDITABLE FINDING / NO EXECUTION AUTHORIZED

## Finding

`beettlle/pi-smart-router` is a technically relevant reference for NICLI/router quota economics, but **not yet trustworthy as evidence that cheaper-tier auto-routing preserves quality in real agent sessions**.

The project is explicitly cache-aware and uses session pinning, local/economical/frontier tiers, context-fit gates, repeated-failure escalation, deterministic triage, local Ollama/LM Studio routing, HyDRA-style embedding matching, and routing telemetry. This matches several of our current concerns: scarce cloud quota, local-first fallback, prompt-cache preservation, and avoiding turn-by-turn model switching that destroys cache economics.

Primary source: https://github.com/beettlle/pi-smart-router

## Decision-relevant negative evidence

Upstream itself keeps issue #95 open as **priority/P0**: the maintainers state that unit/fixture success is insufficient to trust live cost/quality optimization and that they still need shadow dogfood traces plus a pinned TwinRouterBench public-track subset before relaxing toward cheaper defaults. They explicitly cite prior failures from both undersized pins (lost work) and expensive over-routing (spend burn).

Primary issue: https://github.com/beettlle/pi-smart-router/issues/95
Updated upstream: 2026-09-12.

Therefore:

`interesting router design != validated cheaper routing`

and for our stack:

`routing heuristic -> shadow evidence -> release gates -> only then quota-saving policy`

## Relevance to current infrastructure

Useful ideas to borrow conceptually:
- preserve session/model pinning to retain prompt-cache economics;
- escalate on repeated tool-loop failure rather than model-upgrading every turn;
- gate local inference on hardware/context fit;
- expose route reason, candidates, estimated cost, and latency as audit telemetry;
- treat context compaction/overflow as explicit pin-break conditions;
- separate structural triage from learned/embedding-based routing.

Do **not** infer that the package should replace the current Research Market/router. It is pi-specific and its own P0 tracker says behavioral calibration is incomplete.

## Scout action

No new candidate Issue created in this run. The daily opportunity backlog already contains multiple candidates and quality/ceiling discipline favors avoiding another overlapping router item.

No installation, model substitution, routing mutation, spend, or Codex allocation performed.

Quota policy remains `research/quota-governor-v0.md`: Luna/Light default; no silent step-up; do not estimate missing quota counters.
