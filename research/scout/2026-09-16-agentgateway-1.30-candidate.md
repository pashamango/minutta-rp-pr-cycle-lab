# P2 — CANDIDATE / NOT EXECUTION-AUTHORIZED

## Agentgateway 1.30 as unified inference/MCP/A2A/REST router candidate

Status: CANDIDATE / NOT EXECUTION-AUTHORIZED. Do not CLAIM, dispatch, or run downstream Codex/NICLI/local execution from this record.

### Evidence / source
- Primary project release: https://github.com/agentgateway/agentgateway/releases
- Release 1.30.0 (2026-09-09) expands the gateway beyond MCP to generic inference, MCP, A2A, and REST targets, with explicit target-kind routing/metrics.
- Current release line also advertises MCP 2026-07-28 support, including stateful + stateless servers, trace-context propagation via `_meta`, MCP Apps basics, and multiplexing improvements.

### Proposed asset / capability
Evaluate agentgateway as a replaceable front-door/router layer for NICLI/PentAGI/ChitAkasha-style heterogeneous inference and agent endpoints, instead of maintaining separate bespoke routing paths for inference, MCP, A2A, and REST.

### Expected value
High infrastructure option value if one policy/observability boundary can normalize heterogeneous backends. Potential benefits: fewer bespoke adapters, common metrics/tracing, easier provider substitution, and a cleaner place to enforce authority/routing policy before effects. Economic value is indirect at this stage: reduced integration/operations effort and faster addition of paid/free inference providers; no defensible dollar estimate yet.

### Time to first useful result
Day: a bounded config/API compatibility review should be enough to decide whether a local feasibility test is warranted.

### Complexity / risk
Medium. Main uncertainty: whether its authorization/policy semantics and inference routing are sufficiently provider-neutral for our existing router contracts without creating a new central trust/failure bottleneck. MCP 2026-07-28 support is also relatively new.

### Smallest falsification / feasibility test
Without touching active infrastructure, compare 1.30's documented target model and config schema against three representative contracts: one OpenAI-compatible inference endpoint, one MCP endpoint, and one A2A/REST endpoint. Falsify if any requires invasive adapter/state assumptions or if policy/trace boundaries cannot preserve existing authority separation.

### Codex / local-compute cost class
Research/config review: negligible chat/web/Git only. Any executable lab test: low local-compute but MUST be separately admitted by Research Market; no Codex allocation here.

### Why now
The 1.30 release turns agentgateway into a materially broader routing primitive at the same moment our architecture needs provider-independent inference plus MCP/A2A routing. Cheap to falsify before more bespoke router glue accumulates.

### Option-value rank
High: strong reuse/strategic optionality, day-scale falsification, moderate integration risk, low research cost.
