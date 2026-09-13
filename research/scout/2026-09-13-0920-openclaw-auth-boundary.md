# Research Scout — OpenClaw authorization-boundary signal

Date: 2026-09-13
Verdict: **decision-relevant negative evidence; no new candidate Issue**

## Signal

OpenClaw's public security page lists a fresh cluster of authorization/policy-boundary advisories published 2026-09-11, including:

- `GHSA-rx8p-qcpv-c7vr` — Prometheus diagnostics could omit `operator.read` enforcement.
- `GHSA-xvwp-wmh2-fq48` — Discord asset uploads could skip sender media policy.
- `GHSA-5j57-84cx-r295` — iOS deep-link logs could expose unattended credentials.
- `GHSA-m78m-7h3q-q938` — browser relay authentication could exhaust shared pending capacity.

Primary source: https://github.com/openclaw/openclaw/security

Upstream `v2026.9.4` is current and was published 2026-09-11; GitHub release metadata shows continuing artifact/signature/evidence publication through 2026-09-13.

Primary release source: https://github.com/openclaw/openclaw/releases/tag/v2026.9.4

This is not an isolated historical pattern. Earlier 2026 advisories included:

- pairing-scoped device tokens able to mint broader `operator.admin` authority and reach node RCE (`GHSA-4jpw-hj22-2xmc`);
- plugin subagent routes bypassing normal gateway authorization through synthetic admin scopes (`GHSA-xw77-45gv-p728`);
- `operator.write` reaching persistent memory-dreaming admin configuration (`GHSA-5gjc-grvm-m88j`).

## Why it matters here

This is external empirical support for the architectural rule already being implemented in the active Commander/settlement work:

`agent/gateway scope metadata != authority to cause a privileged effect`

The recurring failure mode is **authority expansion or policy omission at composed boundaries**: plugin -> subagent, pairing -> token rotation, write -> admin configuration, diagnostics -> read policy, media action -> filesystem policy.

That directly argues against treating any general agent gateway (including a mature one) as the constitutional trust root. Gateway/tool scopes may be useful hints/capabilities, but the final mutation/settlement boundary should independently verify the exact effect, issuer/certificate, task/source/lease binding, and fail closed on unknown or narrower policy.

## Decision impact

**Do not create a new execution candidate.** The useful action is already represented by active P1 work (#203/#204/#208 family) that removes caller-controlled settlement bypasses and moves positive settlement toward issuer-authenticated evidence. A new opportunity Issue would be duplicate WIP and would compete with the existing repair.

Instead, preserve these OpenClaw advisories as external regression-design input for later review. The most reusable adversarial test classes are:

1. narrow scope must never mint or imply a broader scope;
2. plugin/subagent indirection must not synthesize privileged authority;
3. config-persistent effects require stronger authority than ordinary writes;
4. diagnostics/read paths must enforce read scope independently;
5. action-specific policy (e.g. media/file boundary) must be rechecked at the effect boundary, not inferred from an upstream action grant.

## Opportunity / option-value assessment

No standalone candidate: **NO-OP on backlog creation** because overlap with active P1 is high.

Strategic value is still high as falsification evidence: a very large, security-conscious open-source agent platform repeatedly encountering authorization-composition defects makes our separation of `reasoning`, `transport`, `authority`, and `effect` less speculative and more like a necessary systems invariant.

## Quota discipline

Web/Git research only. No Codex execution allocated. `research/quota-governor-v0.md` remains controlling: Luna/Light is downstream default, no silent model step-up, and missing quota counters are not estimated.
