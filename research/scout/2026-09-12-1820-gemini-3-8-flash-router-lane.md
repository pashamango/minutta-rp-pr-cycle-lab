# Research Scout — Gemini 3.8 Flash router-lane assessment

Date: 2026-09-12 PT
Status: RESEARCH FINDING / NO EXECUTION AUTHORITY

## Finding
Google released Gemini 3.8 Flash on 2026-09-02 as a GA agent/coding workhorse. Primary-source evidence says it is available through the Gemini API at an introductory $0.75/M input and $3.75/M output tokens through 2026-12-31, rising to $1.50/$7.50 on 2027-01-01. Google reports 73.7% on DeepSWE v1.1, 54.9% HLE-Verified, and explicitly says 3.8 may perform extra reasoning/tool iterations and consume more tokens on complex tasks; lower effort or 3.7 Flash remains the efficiency-first option.

Primary sources:
- Google launch, 2026-09-02: https://blog.google/innovation-and-ai/models-and-research/gemini-models/3-8-flash-and-3-8-flash-cyber/
- DeepMind model card: https://deepmind.google/models/model-cards/gemini-3-8-flash/

## Decision relevance
SmartRouter should not treat nominal $/token as the routing objective. 3.8 Flash is a plausible low-cost external lane for public/non-sensitive coding and agent tasks, but Google itself warns that higher diligence can increase token use. Therefore the right comparison is *verified useful result per task* (quality, total tokens, latency, retries, tool calls, failure rate), not model-card price alone.

This strengthens the existing provider-neutral treasury design rather than justifying a provider/model switch.

## Smallest future falsification
Only after the existing Gemini credential/capability path is safely active and Research Market admits a successor:
1. Use a fixed, non-sensitive 10–20 task corpus representative of NICLI/PentAGI routing.
2. Compare 3.8 Flash low/default effort vs 3.7 Flash and the current local/default lane where applicable.
3. Measure actual input/output tokens, wall time, retries, terminal semantic success, and evidence quality; do not infer unavailable provider quota counters.
4. Reject 3.8 as a default cheap lane if total task cost or failure/retry burden erases its nominal price advantage.

## Opportunity assessment
Option value: MEDIUM-HIGH, but no new candidate Issue created in this run because the backlog already contains multiple strong same-day candidates and the existing SmartRouter / credential-enrollment Issues (#156/#157) are the correct parent context. Revisit only after credential activation or when Research Market asks for provider-lane benchmarking.

## Quota discipline
No Codex execution allocated. Luna/Light remains default downstream. Missing account quota counters were not estimated.
