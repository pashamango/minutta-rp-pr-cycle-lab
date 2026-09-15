# Research Scout — Agentic payments registry as identity/authority infrastructure

Date: 2026-09-14
Priority: P2
Status: CANDIDATE / NOT EXECUTION-AUTHORIZED

## Finding
Reuters reported on 2026-09-10 that NPCI is developing an AI-agent registry for transactions under a Unified Agentic Protocol, intended to authenticate/monitor agents initiating UPI payments. Primary-source context makes this materially more credible than a generic trend claim: NPCI already supports delegated UPI payments for IoT/software/AI profiles under UPI Circle, has a payments-specific model (FiMI) in production-oriented workflows, and UPI processed 24.509B transactions in August 2026 across 752 live banks.

Primary evidence:
- NPCI UPI Circle addendum (2025-10-08): delegation extended to IoT devices, software profiles, and AI profiles under Full Delegation; explicit user action required for debit transactions.
- NPCI FiMI announcement (2026-02-17): payments-domain model with structured tool invocation and an agentic framework.
- NPCI UPI statistics: August 2026 volume 24,508.96M transactions; 752 live banks.
- Reuters (2026-09-10): NPCI developing agent registry / Unified Agentic Protocol for agentic payments. Treat registry/UAP details as reported, not yet verified in an NPCI public technical specification.

## Decision relevance
This is evidence that agent identity + bounded delegated authority + payment settlement is becoming payment-rail infrastructure, not merely an MCP-wallet experiment. It strengthens the case for ChitAkasha/Open Money to separate: principal identity -> agent identity -> mandate/capability -> transaction intent -> settlement receipt. It weakens the case for inventing a proprietary payment token before testing compatibility with emerging agent-payment rails.

## Opportunity Card
- Proposed asset/capability: `Agent Payment Mandate Adapter v0` — protocol-neutral schema mapping ChitAkasha claim/authority objects to emerging delegated-payment primitives (UPI Circle/UAP when public, L402/NWC, and future card/wallet agent protocols). No real-money execution in the candidate phase.
- Expected value: high infrastructure/reuse option value; could become a portable authorization/receipt layer for agent markets and Open Money experiments. Near-term revenue is too speculative for a defensible dollar estimate.
- Time-to-first-useful-result: day for schema comparison; week for a mock adapter if Research Market later authorizes execution.
- Complexity/risk: medium. Main uncertainty is that NPCI's reported UAP/registry technical specification is not yet publicly verified, and payment/regulatory semantics differ by rail/jurisdiction.
- Smallest falsification test: wait/search for public NPCI UAP/registry specification; compare its identity, mandate, limits, revocation, receipt, and liability fields against existing internal authority objects. Falsify if no meaningful common abstraction survives without rail-specific leakage.
- Expected Codex/local-compute cost: LOW for schema analysis; MEDIUM for later mock adapter. Luna/Light default; no step-up justified.
- Why now: national-scale payment infrastructure is moving toward explicit agent registration/delegation; early schema alignment is cheap and preserves optionality.
- Option-value rank: HIGH, discounted by specification uncertainty and regulatory fragmentation.

## Guardrails
No spending, billing enablement, credential use, payment initiation, production integration, or execution authorization. Research Market remains sole allocator of any implementation successor.
