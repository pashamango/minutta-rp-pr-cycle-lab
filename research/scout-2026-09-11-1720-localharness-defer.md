# Research Scout — LocalHarness: promising quota-saving harness, defer candidate

Date: 2026-09-11 17:20 America/Los_Angeles
Outcome: `DEFER / NO_NEW_CANDIDATE`

## Question

Does `ahwurm/localharness` create a sufficiently strong new opportunity to add another candidate to the Research Market backlog today?

## Evidence

Primary repository: https://github.com/ahwurm/localharness

Observed repository state during this Scout pass:
- public MIT-licensed Python project;
- created 2026-05-24; pushed/updated 2026-09-11;
- 33 stars, 3 forks, 4 open issues at observation time;
- model-agnostic agent layer over OpenAI-compatible local inference (vLLM, Ollama, LM Studio, llama.cpp);
- YAML-defined hierarchical agents;
- deny-first permissions that can narrow through hierarchy;
- per-project SQLite memory and append-only JSONL event history;
- MCP support;
- built-in benchmark corpus;
- explicit autoresearch loop (`propose -> gate -> promote`);
- local recurring-job positioning: no cloud metering/rate limit for unattended work;
- runtime documentation claims exact token counting for supported paths and live validation across multiple local runtimes, with benchmark runs presently strongest on vLLM;
- project documents a structural prompt-injection defense by separating untrusted-web agents from host-mutating tools.

Relevant local context:
- `research/quota-governor-v0.md` already directs specialist work toward web/Git/local lanes under Codex pressure and keeps Luna/Light as the default when Codex is admitted.
- Active Issue #126 (`LOCAL-MARKET-SCHEDULER-0001`) is already P0 and aims to build a deterministic local scheduler using Forgejo runners with no routine LLM heartbeat.
- Existing Scout candidate #96 already evaluates A2A/ACP interoperability for Codex workers.
- Today already has three explicit Scout opportunity candidates (#106, #107, #110), meeting the stated 1–3/day target without filler.

## Assessment

LocalHarness is technically relevant because it bundles several mechanisms that map well to current needs: local recurring execution, deny-first tool policy, project-scoped memory, MCP, event logs, and self-evaluation. Its strongest strategic value would be as a **reference or later comparison baseline** for moving recurring specialist work off scarce cloud-agent quota.

However, creating a new candidate now would be premature for three reasons:

1. **Overlap with active P0 work.** Issue #126 is already establishing the local deterministic scheduling/control plane. Introducing a competing harness evaluation now risks distracting from that architectural proof rather than complementing it.
2. **Maturity uncertainty.** The project is active but still small (33 stars/3 forks at observation); several attractive claims are self-reported in its README and have not been independently reproduced on Wolfram/Minutta hardware.
3. **Backlog discipline.** Three Scout candidates already exist today. A fourth is not justified unless materially stronger than current candidates.

## Decision consequence

Do **not** create a LocalHarness candidate Issue today. Keep it as a comparison/reference target for a future moment when either:

- P0 local scheduler #126 reaches a stable result and needs an agent-harness execution layer; or
- a bounded benchmark is needed to decide whether PentAGI/current local agent loops are losing materially to harness design rather than model quality.

At that point, the smallest useful test would be a read-only benchmark on an already-running local OpenAI-compatible endpoint, comparing one identical task/model across the current harness and LocalHarness while measuring task success, tool-call reliability, wall time, context/tokens when observable, permission failures, and recovery behavior. No infrastructure replacement should precede that comparison.

## Option-value view

Potential option value: **medium-high**.
Time-to-first-useful-result if later admitted: **day**.
Complexity/risk: **medium**, mainly integration/maturity and overlap with current control-plane architecture.
Codex/local-compute cost: **low**, preferably local-only; no model step-up required.

Why-now signal: active development and exact overlap with quota-saving local-agent concerns make it worth tracking, but not worth creating competing WIP today.

## Verdict

`DEFER / NO_NEW_CANDIDATE`

No CLAIM, execution, installation, deployment, model escalation, or infrastructure mutation is authorized by this note.