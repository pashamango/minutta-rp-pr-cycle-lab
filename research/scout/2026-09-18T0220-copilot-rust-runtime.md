# Research Scout finding — 2026-09-18 02:20 PT

Status: FINDING / NO EXECUTION AUTHORIZED
Priority: P2 candidate insight; not claimed; not dispatched.

## Evidence
Primary source: GitHub Engineering, Stephen Toub, 2026-09-16, “Migrating the GitHub Copilot runtime to Rust, using Copilot”. GitHub reports a live incremental rewrite of the Copilot agent runtime from TypeScript/Node/V8 to ~832k lines of production Rust, with 128 PRs and most code written by AI agents. The resulting native runtime exposes a C ABI and can run in-process or out-of-process. In GitHub’s 100-by-10 session-lifecycle workload, pre-port TypeScript achieved 7.55 lifecycles/s, Rust out-of-process 57.45, Rust in-process 120.0; measured ten-client private-memory delta fell from 1,383 MB to 126 MB in-process. GitHub explicitly warns these are workload-specific, not universal speedups. Known regressions clustered around incomplete migration, state/lifetime, behavioral-contract mismatches, host boundaries, and incorrect test oracles.

Source: https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/

## Decision relevance
For always-on local agent infrastructure (NICLI/mailbox/router/PentAGI-adjacent), this is strong primary evidence that agent-runtime overhead can be reduced materially by separating UI from runtime and using one embeddable native engine shared across many sessions. The more important lesson is architectural, not “rewrite everything in Rust”: preserve a stable protocol/SDK boundary, migrate incrementally, and benchmark session lifecycle + memory + CPU rather than token count alone.

## Opportunity Card
Proposed asset/capability: a small, non-executing design candidate for a shared native `agent-runtime-core` boundary (or equivalent daemon) behind existing mailbox/router interfaces; no rewrite authorization.
Expected value: infrastructure leverage through lower per-session process/memory overhead and cleaner multi-client embedding; potentially higher local concurrency on existing hardware.
Time-to-first-useful-result: day for paper/design comparison; week for a bounded benchmark only if Research Market later authorizes execution.
Complexity/risk: MEDIUM-HIGH. Main uncertainty: current local bottleneck may be model inference rather than harness/process overhead; a Rust rewrite could have near-zero practical value. Lifecycle/FFI regressions are a demonstrated risk.
Smallest falsification: measure existing harness baseline for N idle/lightweight concurrent sessions: startup latency, RSS/private memory, CPU, process count. If harness overhead is <10% of total resource/time budget, reject/deprioritize native-runtime work.
Codex/local-compute cost class: research/design = none/low; benchmark = low local; implementation = high and must be separately allocated.
Why now: GitHub published unusually detailed production measurements and failure modes on 2026-09-16, giving a concrete external baseline for deciding whether our own runtime layer is worth optimizing.

## Quota discipline
No Work/Codex/local runner invoked. Missing quota counters were not estimated. Per `research/quota-governor-v0.md`, this remains web/Git research -> candidate handoff only.
