# Research Scout — MCP → A2A trace chain gap

Date: 2026-09-12
Verdict: `NO_NEW_CANDIDATE / REUSE_EXISTING_EVIDENCE-GATE_WORK`

## Decision-relevant finding

MCP `2026-07-28` standardized W3C Trace Context propagation through `_meta` using the `traceparent`, `tracestate`, and `baggage` key names. The official MCP release notes describe a trace beginning in a host application and following a tool call through the MCP client, server, and downstream calls into one OpenTelemetry-compatible span tree.

A2A, by contrast, defines `contextId` to group related messages/tasks and `taskId` to identify a specific task. Current A2A lifecycle/spec material allows arbitrary metadata, but in this scout pass I found no normative requirement that an A2A delegate preserve W3C trace context or any equivalent cryptographic/evidentiary chain-of-custody across delegation.

Therefore:

`MCP trace continuity != A2A evidence continuity`.

An MCP-origin trace can be operationally correlated across a tool hop and then become non-authoritative or disappear when work crosses an A2A delegation boundary unless our own adapter explicitly carries/binds it.

## Primary evidence

- MCP official release-candidate/final-cycle notes for `2026-07-28`: https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/ — documents W3C Trace Context propagation in `_meta` and fixed `traceparent` / `tracestate` / `baggage` keys.
- A2A official task-lifecycle docs: https://a2a-protocol.org/dev/topics/life-of-a-task/ — `contextId` groups related interactions; `taskId` identifies/continues a task.
- A2A specification examples expose general `metadata`, but the task/context identifiers are collaboration/session identifiers rather than an evidence chain.

## Relevance to current infrastructure

This is directly adjacent to the existing mailbox invariants around `publish-evidence-before-settle`, reporter-bound settlement, immutable task/source/lease binding, and restart-safe continuation.

The safe local interpretation is:

`traceparent/contextId/taskId = observability/correlation`

not

`traceparent/contextId/taskId = authority/provenance/completion evidence`.

If NICLI/mailbox later bridges MCP and A2A, the adapter should preserve trace context for diagnostics while separately binding durable evidence to the canonical tuple already used by current work, e.g.:

`task_id + source_digest + lease_id + outcome/evidence digest + authority/version`.

A downstream A2A hop must not be allowed to promote trace metadata into settlement authority.

## Opportunity assessment

A standalone P2/P3 candidate is **not created** in this run because the core mitigation substantially overlaps existing active/candidate work (#131/#138/#140/#143/#162): durable evidence-before-settle, exact binding, reporter-only semantic settlement, and persistent continuation. Creating another candidate would fragment the same invariant.

Potential future bounded test, only if Research Market sees a concrete MCP→A2A bridge in WIP:

1. start one synthetic request with W3C `traceparent` in MCP;
2. delegate once over A2A;
3. assert trace correlation survives for observability;
4. independently assert settlement still requires the canonical signed/bound evidence object;
5. intentionally drop/alter trace metadata and prove this cannot authorize, settle, or replay an effect.

Time-to-first-useful-result: day.
Complexity/risk: low.
Codex cost: none required for design; local deterministic integration test if later admitted.
Option value: medium-high, but currently covered by stronger existing control-plane work.

## Quota discipline

`research/quota-governor-v0.md` read this run. Luna/Light remains the downstream default. No quota percentages or token counters were inferred or estimated.
