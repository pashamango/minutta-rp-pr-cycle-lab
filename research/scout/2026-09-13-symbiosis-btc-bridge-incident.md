# Research Scout — Symbiosis BTC bridge incident

Date: 2026-09-13
Priority: decision-relevant negative feasibility / architecture risk
Execution authority: NONE

## Finding

Symbiosis reported a Bitcoin Bridge security incident at approximately 04:28 UTC on 2026-09-11. BTC routes were halted while the team said EVM/TRON/TON routes and Octopools remained operational. The team reported recovering ~15 BTC into a team-controlled multisig and said final loss accounting was still in progress. Secondary on-chain reporting attributed the incident to abnormal syBTC minting and estimated roughly $336k WBTC loss; treat that figure/mechanism as unconfirmed until a primary postmortem is published.

Pre-incident Symbiosis materials described the BTC bridge as non-custodial, using syBTC internally plus MPC/TSS signing, and emphasized multiple audits and no prior major incidents. The incident therefore falsifies any design assumption that audit count + non-custodial UX + threshold signing is sufficient evidence for bridge-level settlement safety.

## Decision impact

For Night Miracle / Open Money / any BTC↔stablecoin settlement experiment, do not treat a third-party BTC bridge as a trustless settlement primitive. Keep bridge adapters behind a replaceable, fail-closed boundary and require route-specific risk state. A bridge route should be independently disableable without halting unrelated settlement paths.

No recommendation to use Symbiosis until: (1) primary postmortem/root cause is published, (2) affected route is restored, and (3) remediation can be mapped to the failure mode.

## Smallest follow-up test

No Codex needed. Monitor only for the primary postmortem and remediation diff. When published, compare exploit class against our proposed bridge/settlement invariants: mint authorization, asset conservation, signer threshold, replay/idempotency, route isolation, and emergency halt semantics.

## Quota / cost

Codex cost: none.
Local compute: none.
Web/Git research only, consistent with `research/quota-governor-v0.md` (Luna/Light default; do not consume scarce Codex for scouting when web/Git is sufficient).

## Sources

- Symbiosis BTC bridge product/architecture page (pre-incident snapshot): https://symbiosis.finance/bridge-btc
- Incident report relayed from Symbiosis statement by ChainCatcher: https://www.api.chaincatcher.com/en/article/2289281
- Symbiosis statement mirrored in OKX Orbit/PANews feed: https://www.okx.com/en-us/orbit/user/872855970597515265
- Secondary on-chain estimate/mechanism (unconfirmed): https://www.lookonchain.com/feeds/72707

## Scout verdict

NEGATIVE FEASIBILITY SIGNAL. Do not create an execution candidate. Preserve as an architectural constraint and watch for the primary postmortem.
