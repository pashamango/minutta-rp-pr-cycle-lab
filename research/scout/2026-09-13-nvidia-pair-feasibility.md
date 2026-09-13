# Research Scout — NVIDIA PAIR fleet feasibility

Date: 2026-09-13
Priority: P3 observation / NO EXECUTION AUTHORIZED
Disposition: negative near-term feasibility for current heterogeneous fleet; monitor, do not allocate Codex.

## Finding

NVIDIA PAIR beta is now a credible local inference router: it exposes one local endpoint and distributes independent inference requests across compatible LAN nodes running Ollama or LM Studio while keeping prompts/files/context on the local network. However, it does **not** pool VRAM or combine machines into one virtual GPU; nodes remain separate and handle parallel requests.

NVIDIA's published validated configurations currently require macOS Tahoe with **Mac M4 or newer**, or supported RTX/DGX systems. That makes Darwin (MacBookPro13,2 / Intel) ineligible, and it likely prevents PAIR from serving as the desired whole-home heterogeneous router today. Minutta's RTX 3090 class is within the stated RTX 20-series-or-newer GPU family, but a single eligible node provides little routing value by itself.

## Decision impact

Do not spend scarce Codex quota integrating PAIR into NICLI/PentAGI yet. PAIR is a stronger vendor-supported baseline than ad-hoc LAN scheduling, but its present hardware boundary excludes a key always-on node and it cannot make multiple smaller-memory machines behave like one large-memory inference device.

This leaves heterogeneous/open alternatives (for example SwarmLLM-style routing/sharding) relevant for the current fleet, while PAIR should be rechecked if NVIDIA broadens macOS support or another compatible RTX/M4 node is added.

## Evidence

Primary NVIDIA PAIR page / FAQ (accessed 2026-09-13):
- https://www.nvidia.com/en-in/ai-on-rtx/personal-ai-router/

Key published facts:
- single endpoint for local inference across RTX, DGX Spark, and macOS devices;
- launch support for Ollama and LM Studio;
- local-network privacy design;
- validated Mac hardware: M4 or newer;
- RTX: GeForce RTX 20 Series or newer;
- nodes remain separate systems; PAIR explicitly does not combine them into one virtual GPU.

## Smallest future falsification

Recheck the official compatibility table before any integration work. Only create an executable successor if either (a) Intel/older Mac support appears, or (b) the fleet gains at least two PAIR-compatible nodes and parallel-request routing is a measured bottleneck.

## Cost / option value

- Codex cost now: none.
- Local-compute cost now: none.
- Recheck cost: very low.
- Option value: medium if fleet compatibility changes; low for current topology.
