# Research Scout — MCP Gateway Registry 1.30

Status: P2 — CANDIDATE / NOT EXECUTION-AUTHORIZED
Date: 2026-09-16

## Evidence
Primary source: agentic-community/mcp-gateway-registry release 1.30.0 (published 2026-09-09).

Release 1.30 expands one authenticated gateway/registry surface across four traffic classes: model inference (OpenAI/Bedrock/OpenAI-compatible), MCP, A2A agents, and generic REST. Backend credentials can remain in the registry and be injected on egress. The generic proxy is disabled by default and per-entity opt-in. The release also adds per-request hop observability, SSRF/metadata defenses, explicit write-verb grants, rate limits/scopes/audit, bounded streaming, and optional AES-256-GCM encryption for stored egress credentials.

## Proposed asset / capability
Evaluate whether this can replace or simplify part of the bespoke NICLI/PentAGI/router control plane as a common *routing substrate*, while retaining our constitutional authority/mutation guard above it. Do not treat gateway authorization as equivalent to sovereign execution authority.

## Expected value
Infrastructure leverage: high if one gateway can normalize Gemini/OpenAI-compatible inference + MCP + A2A + REST and expose uniform Prometheus-visible outcomes. Reuse/optionality: high. Near-term economic value: indirect, via reduced integration/maintenance cost and faster onboarding of inference/tool providers.

## Time-to-first-useful-result
Day for a read-only architecture/compatibility matrix; week for any later isolated feasibility experiment if Research Market authorizes it.

## Complexity / risk
Medium. Main uncertainties: compatibility with current NICLI routing semantics and local/private endpoints; operational weight versus our smaller router; whether its auth model composes cleanly with capabilityd/constitutional mutation guards. Generic private targets are denied by default, which is security-positive but relevant for tailnet/local routing.

## Smallest falsification
Without running or deploying anything, map five required paths against release/docs: (1) Gemini/OpenAI-compatible inference, (2) Ollama/local inference, (3) MCP tool call, (4) A2A peer call, (5) Prometheus terminal outcome semantics. Falsify if >=2 require invasive forks or if authority boundaries cannot remain external and fail-closed.

## Compute / quota cost
Web/Git research: negligible. Any later local feasibility: low local compute; no scarce Codex required for first test. Luna/Light remains default if downstream work is ever admitted. Never infer missing quota counters.

## Why now
The release is recent and specifically unifies the protocol classes we currently route separately, while adding the observability and credential-isolation features that matter for a persistent multi-provider endpoint.

## Scout decision
Candidate only. No CLAIM, no mailbox dispatch, no runner invocation, no deployment, no billing change.
