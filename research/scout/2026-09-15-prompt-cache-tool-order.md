# Research Scout finding — stable tool ordering as quota lever

Date: 2026-09-15
Status: EVIDENCE / NO EXECUTION AUTHORIZATION
Priority: P2 candidate insight

## Evidence
OpenAI's published Codex agent-loop analysis documents that inference sampling dominates network cost and that prompt caching is a primary efficiency mechanism. It also records a concrete MCP integration bug: enumerating tools in inconsistent order caused cache misses; dynamic `tools/list_changed` notifications can likewise trigger expensive cache invalidation in long conversations.

Primary source: https://openai.com/index/unrolling-the-codex-agent-loop/

## Decision-relevant update
Before spending scarce quota on stronger models or more parallel lanes, NICLI/mailbox/router designs should treat prompt-prefix stability and deterministic tool enumeration as a first-class cache invariant. This is a cheap potential efficiency gain because it changes orchestration rather than model capability.

## Proposed asset/capability
A small `CACHE_INVARIANTS/v1` specification for agent routers: canonical tool ordering, stable static prefix, explicit cache-busting events, and telemetry for cache-hit/miss when exposed.

Expected value: infrastructure leverage; potentially lower repeated-inference cost/latency across many agents. No dollar or token saving is asserted without measured counters.
Time-to-first-useful-result: day.
Complexity/risk: low; main uncertainty is how much current NICLI/PentAGI traffic actually suffers avoidable cache misses and which providers expose usable cache telemetry.
Smallest falsification: inspect representative serialized request prefixes/tool lists from repeated equivalent runs and determine whether ordering/prefix drift occurs; if observable provider cache telemetry exists, compare stable vs deliberately permuted tool order. Do not invoke Codex for this test during debug phase.
Compute cost class: web/Git/local inspection only; zero scarce Codex required.
Why now: quota governor explicitly prefers orchestration improvements and forbids estimating missing quota counters. Cache stability is one of the few documented harness-level mechanisms that can reduce inference work without a model step-up.

CANDIDATE / NOT EXECUTION-AUTHORIZED. Research Market alone may create an executable successor.
