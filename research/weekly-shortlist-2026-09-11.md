# Research Shortlist — 2026-09-11

Status: weekly synthesis. Research only; no execution authority implied.

Quota policy: `research/quota-governor-v0.md` respected. No scarce Codex work was allocated; web/Git research only.

## Ranked shortlist

### 1. OpenAI Secure MCP Tunnel (`openai/tunnel-client`)
Primary source: https://github.com/openai/tunnel-client

What changed: OpenAI now publishes an official customer-run client that connects private/localhost MCP servers to ChatGPT, Codex, Responses API, and AgentKit without exposing the MCP server to the public internet. It includes health/readiness/metrics/UI, managed runtime supervision, permissions, mTLS support, stdio/HTTP/in-memory MCP transports, and a Codex/plugin workflow.

Why it matters: this directly overlaps the ChitAkasha/Wolfram/Darwin requirement for private local services reachable by cloud agents while preserving a hard inbound boundary. It may eliminate bespoke exposure glue and reduce operational complexity.

Read/try/build: TRY via bounded feasibility test only. Do not replace tailnet controls or existing authorization layers without comparison.

### 2. Zero-Knowledge Predicate Proof Gateway between MCP/A2A agents
Primary source: https://arxiv.org/abs/2608.30083

What changed: a measured implementation carries Bulletproof-style predicate proofs across MCP and A2A. Reported benchmark for a 32-bit threshold predicate: 6.2 ms proving, 1.0 ms verification, 608-byte proof on one commodity vCPU. The paper explicitly identifies the source-integrity gap and proposes binding enclave attestation to the proof.

Why it matters: directly supports ChitAkasha's desired pattern `private claim -> proven predicate -> agent-to-agent exchange`, while correctly separating proof-of-predicate from proof-of-provenance.

Read/try/build: READ NOW. Architecture reference for a future claim-unit proof adapter; not a reason to allocate Codex immediately.

### 3. Atomic Agent: local-first agent loop benchmarked on the same local model
Primary source: https://github.com/AtomicBot-ai/atomic-agent

What changed: the project reports a controlled GAIA L1 comparison using the same local qwen-3.6-35b-a3b model and same task budget: 37/53 (69.8%) vs Hermes 31/53 (58.5%), with lower average wall time (~217 s vs ~351 s). It is llama.cpp-first and keeps the agent control loop/state local.

Why it matters: evidence that agent-loop design can materially improve useful local-agent performance without buying a larger model. This is exactly the scarce-quota optimization problem: improve orchestration before increasing cloud intelligence.

Read/try/build: INSPECT, then candidate benchmark only if Research Market admits it. Main uncertainty is external reproducibility on Wolfram/Minutta hardware and tasks.

### 4. SwarmLLM: distributed/private inference matured enough for a cheap falsification
Primary source: https://github.com/enapt/SwarmLLM

What changed: September work added automatic partial GPU/CPU layer splitting when a model slightly exceeds VRAM; the project reports 1.8x CPU-only speed on an RTX 3070 for an otherwise non-fitting 7B model. It exposes OpenAI/Anthropic/MCP-compatible APIs, supports encrypted distributed inference, private/offline modes, prefix/KV caching, and reports thousands of automated tests.

Why it matters: Minutta's RTX 3090 plus Macs create exactly the heterogeneous pool this design targets. If real, it could turn idle local hardware into a larger-model fallback without Codex quota.

Read/try/build: TRY ONLY AS AN ISOLATED LOCAL/LAN FALSIFICATION. The public-swarm default and security/privacy assumptions are a material risk; no sensitive prompts should leave controlled devices during any test.

### 5. Silent Payments coinbase for miner payouts
Primary sources: https://delvingbitcoin.org/t/silent-payments-coinbase/2833 and https://bitcoinops.org/en/newsletters/2026/09/04/

What changed: proposal adapts BIP352 Silent Payments to coinbase payouts using an ephemeral pool key and block-height commitment, with the sending pubkey in the coinbase scriptSig. Miners could provide one static silent-payment address over Stratum v2 instead of xpub-derived payout addresses.

Why it matters: a concrete Open Money pattern where a static identity-like endpoint maps to unlinkable outputs. This is relevant both to mining/privacy and to agent payment identity design.

Read/try/build: READ, not build yet. Main blockers are wallet scanning-profile changes, amount fingerprinting, and pool database privacy.

### 6. Bitcoin-native metering for agent tools (LiveAuth / Lightning MCP pattern)
Primary sources: https://github.com/dulzuradev/liveauth-mcp and https://github.com/jeletor/lightning-mcp

What changed: emerging MCP servers combine PoW or Lightning/L402 payment with per-call metering, idempotent receipts, NWC wallets, service discovery and agent trust layers. LiveAuth explicitly offers free PoW authentication or sats-backed access and signed receipts; lightning-mcp combines NWC, L402 and Nostr discovery.

Why it matters: this is a concrete near-term implementation pattern for an agent market where calls have explicit cost and receipts, rather than a speculative token economy. It also fits Behavioral Mining / Proof-of-Meaning experiments because PoW can gate anonymous access before monetary payment.

Read/try/build: CHEAP PRODUCT FALSIFICATION candidate. Do not connect real-value wallets; mock/testnet/sub-wallet only.

## Negative / no-op findings

- No new Bloom-filter paper in the last week cleared the relevance/novelty bar. Do not manufacture a Bloom item just to fill the category.
- No fresh reverse-semantic-hashing primary result appeared stronger than the previously reviewed PROSE/private-dense-retrieval line. Treat that thread as unchanged this week.
- SwarmLLM remains alpha with a small public adoption footprint despite extensive self-reported testing; therefore it is a falsification target, not an infrastructure recommendation.

## Weekly synthesis

The strongest practical pattern this week is not a new model. It is a boundary architecture:

`private/local capability -> narrow MCP surface -> explicit authorization -> optional ZK predicate -> metered effect -> auditable receipt`

This is unusually compatible with current ChitAkasha infrastructure and with quota discipline: improve routing, boundaries, and local execution before spending more scarce cloud reasoning.
