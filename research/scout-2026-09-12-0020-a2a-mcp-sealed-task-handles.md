# Research Scout — stateless A2A↔MCP task handles

Date: 2026-09-12
Status: evidence note; no execution authorized
Decision: do **not** create a new candidate Issue; fold as design evidence into existing sovereign-worker/control-plane work (#108, #131) when/if Research Market admits it.

## Signal

A small public bridge, `aarushitandon0/a2a-mcp-bridge`, implements A2A 1.0 behind MCP 2026-07-28 and makes one design choice directly relevant to our mailbox/NICLI work: the bridge is stateless, while the client carries an opaque sealed `taskId` that encodes enough routing identity for any bridge instance to resume `tasks/get`, `tasks/update`, or `tasks/cancel` against the authoritative A2A task.

Primary sources:
- https://github.com/aarushitandon0/a2a-mcp-bridge
- https://github.com/aarushitandon0/a2a-mcp-bridge/blob/main/SPEC-NOTES.md
- MCP Tasks extension / MCP 2026-07-28 references are enumerated with pinned SHAs inside that SPEC-NOTES file.

The repo reports independent conformance runs against `modelcontextprotocol/conformance` for stateless server/header/tool-list behavior. This is project-reported evidence, not independently reproduced by Scout.

## Important protocol finding

The project's spec analysis distinguishes two interrupt mechanisms that are easy to conflate:

1. pre-task input requirement: core MCP multi-round-trip request + opaque `requestState`;
2. input required **during an already-running task**: MCP Tasks `tasks/get` -> `input_required`, then `tasks/update` with `inputResponses`.

For A2A tasks that enter `INPUT_REQUIRED` after submission, the second mechanism is the correct mapping. The project uses the opaque sealed task handle itself as the restart/routing carrier.

## Security / authority relevance

The current MCP Tasks extension intentionally has no `tasks/list`. The bridge preserves this rather than projecting A2A `ListTasks`, because without a session/authorization story a global task listing can leak cross-caller visibility. This is a useful negative design result for NICLI/mailbox: **enumerability is a privilege, not a convenience API**.

Candidate invariant:

`opaque capability-like task handle + exact task/lease binding > globally enumerable task registry`

but only for routing/resumption. A sealed handle must **not** become authority or settlement proof by itself.

## Fit to current work

- #108 `A2A-SOVEREIGN-WORKER-0001`: gives a concrete reference design for stateless resume/cancel/input-required semantics without giving coordinator generic host access.
- #131 `PUBLISH-EVIDENCE-BEFORE-SETTLE-0001`: compatible with exact task/lease identity, but does not solve durable evidence publication. Treat transport-resumption identity and evidence settlement as separate layers.

Potential clean split:

`sealed task handle -> routing / continuation identity`
`durable Git evidence manifest -> reviewability / provenance`
`reporter/verifier -> semantic settlement`

Do not collapse these three.

## Opportunity assessment

Option value: medium-high architectural leverage, low immediate execution urgency.
Time to first useful result if later admitted: day-scale synthetic comparison inside #108.
Complexity/risk: low-medium; main uncertainty is whether this third-party bridge remains aligned with rapidly evolving MCP Tasks extension details.
Codex/local-compute cost: none for this Scout finding; later falsification should be deterministic/local-first and Luna/Light only if reasoning is needed.

## Smallest future falsification

If #108 executes, compare its chosen A2A/ACP implementation with this pattern using one synthetic task:
- create task;
- restart/replace bridge process;
- resume via opaque handle from another instance;
- verify wrong/tampered handle fails closed;
- prove no task-list capability is required;
- prove handle possession alone does not authorize an out-of-scope mutation or mark the task settled.

Fail the pattern if secure resumption requires hidden in-process state, a globally enumerable registry, reusable broad credentials, or if the handle becomes indistinguishable from authorization/settlement authority.

## Quota discipline

Read and followed `research/quota-governor-v0.md`: no quota counters were estimated, no Codex lane was admitted, and no model step-up was requested. This run used web/Git research only.
