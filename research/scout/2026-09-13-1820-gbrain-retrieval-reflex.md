# Research Scout — 2026-09-13 18:20 PT

## Finding

**Deterministic retrieval reflex is a credible quota-saving primitive before any LLM/vector-memory call.**

Primary upstream: `garrytan/gbrain`.

Evidence:
- `docs/architecture/RETRIEVAL.md` documents zero-LLM auto-link extraction from markdown/wikilinks and typed heuristic graph edges; upstream reports full extraction over its ~17K-page corpus in seconds.
- `src/core/context/entity-salience.ts` implements a `Retrieval Reflex` first pass explicitly described as zero-LLM, zero-DB, SDK-free and precision-biased before touching the memory index.
- Latest observed release commit `a6be012a3bcfac42e279630aedec5cda4a450e29` (`v0.50.0.0`, 2026-09-11) hardens consent, delegated tools, background jobs and durable authorization. Upstream reports 29,333 tests, 54 structural/type checks and 232 E2E files passing; not locally reproduced.

Primary sources:
- https://github.com/garrytan/gbrain/blob/master/docs/architecture/RETRIEVAL.md
- https://github.com/garrytan/gbrain/blob/master/src/core/context/entity-salience.ts
- https://github.com/garrytan/gbrain/commit/a6be012a3bcfac42e279630aedec5cda4a450e29

## Decision relevance

Our traffic contains many structured repeated references (Issue IDs, task IDs, repositories, branches, hosts, agents, claim IDs). A deterministic stage could cheaply resolve or narrow these before semantic/LLM retrieval:

`turn -> deterministic salience/ref extraction -> exact/graph lookup -> only-if-needed semantic/LLM retrieval`

This is narrower than adopting GBrain/PAXM/Prism as a memory backend and therefore has lower switching risk. It can remain provider-neutral and authority-free.

## Important negative / limitation

The upstream extractor explicitly documents recall limits: capitalization/ASCII bias, lowercase-name misses, multilingual limits, and no true pronoun coreference. Therefore the safe design is **fail-open to the existing semantic path**, never deterministic-only recall.

## Opportunity action

Created Issue #224:
`P2 CANDIDATE / NOT EXECUTION-AUTHORIZED — Deterministic retrieval reflex before LLM memory calls`

No execution, installation, model step-up, secrets, spending or production mutation authorized.

## Quota discipline

Read `research/quota-governor-v0.md`. No Codex execution allocated. Missing quota counters were not estimated. Any later admitted implementation remains Luna/Light by default.
