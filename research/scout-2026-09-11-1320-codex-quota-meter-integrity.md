# Research Scout finding — Codex quota meter integrity risk

Date: 2026-09-11 13:20 America/Los_Angeles
Status: decision-relevant negative feasibility / telemetry caveat

## Finding

Current public evidence weakens the assumption that the displayed Codex quota meter is a clean ground-truth burn signal during the Sep 9–11 incident window.

OpenAI Codex issue #44703 (opened 2026-09-11) reports allowance decreasing while idle/relaunching, reproduced by the reporter on two separate accounts (Plus and Pro). The issue is labeled `bug` and `rate-limits` and links several contemporaneous reports (#44199, #44663, #44673, #44685) involving sudden depletion, reset-date mismatch, and possible overcounting. This is user-reported evidence, not an OpenAI-confirmed root cause.

Primary source: https://github.com/openai/codex/issues/44703

## Decision impact

`research/quota-governor-v0.md` correctly says never estimate missing counters and to use multi-hour quota snapshots. However, until the incident is resolved, a falling displayed percentage should not by itself be interpreted as measured workload burn or used to infer `b_observed` with high confidence.

Conservative policy amendment candidate:

- preserve Luna / Light as downstream default;
- do not increase capacity from apparently generous quota;
- do not attribute unexplained quota drops to a particular Research/Codex lane without corroborating active-run evidence;
- annotate affected snapshots as `meter_integrity_uncertain` when they occur during a known reporting incident;
- prefer paired evidence: displayed snapshots + actual active task/run records;
- continue web/Git/local research under pressure rather than guessing real usage.

## Falsification / exit condition

Treat this caveat as temporary. Remove or downgrade it when either:

1. OpenAI closes/clarifies the incident with a root cause showing the displayed meter remained accurate, or
2. repeated controlled idle-vs-active observations over a stable period show the meter tracks only real workload again.

## Cost / authority

No Codex execution requested. No quota percentage was estimated. No infrastructure mutation performed beyond this research note.