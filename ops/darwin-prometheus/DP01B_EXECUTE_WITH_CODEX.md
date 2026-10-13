# Darwin & Wolfram Codex — DP-01B Execution Relay

**Authorization**: User-approved DP-01B via existing mandate. Work only within MIN-51, preserve previously HOST_DONE DP-01 E1 and working Wolfram push-first deployment. No sudo, no model switch, no new inbound SSH, no new ports, no public secrets.

**Repository**: `pashamango/minutta-rp-pr-cycle-lab`, branch `agent/darwin-prometheus/dp-01b-host-adapters-20261013`, folder `ops/darwin-prometheus`.

## Darwin Codex (execute locally)
1. Fetch the above branch and read `DP01B_RUNBOOK.md` and new source. Use native authenticated GitHub/Forgejo access, do not rely on stale checkout.
2. Verify exact commit, 44 Ledger/DP01B tests and 24 Governor/push tests on Darwin in sandbox/staging, not production. Check that the existing Darwin ledger user LaunchAgent and quota service are unchanged. Important: the new `host.snapshot` type is a forward-compatible extension only with the new reader; writing it into production **makes the old reader fail verification**. Require explicit verified format-migration/rollback plan before first production append.
3. On disposable ledger, run local collect/ingest, checkpoint, rebuild and tamper tests. Return `DP01B_STAGING_RECEIPT/v1`, no unapproved production writes.
4. After staging passes and the compatible runtime deployment plan is tested, integrate and run a single bounded real `host.snapshot` on Darwin only; no new agent installation. Verify existing previous 9+ records (count may have grown) and next natural cycle.
5. Receive source attestation/escrow via Wolfram-originated SSH, not Darwin→Wolfram SSH. Do not fetch raw source into a GitHub issue or public chat. Private Forgejo branch only after local secrets review and correct rights.

## Wolfram Codex (execute locally)
1. Read actual `launchctl print gui/501/com.chitakasha.token-governor-push` to confirm the true entrypoint has not changed, without outputting environment/credentials. Re-hash actual `push_first_collector.py`; expected `a916cdffa81312b12ff1761dc5f81fbb30dcb04670c52ad02e08eeee07f22f81`.
2. Stage `source_attest.py`, fingerprint and locally review the original source without publishing it; if safe, send only that one file Wolfram→Darwin private escrow folder using established strict SSH channel, then confirm both SHA values.
3. Optionally stage `host_adapter.py` + compatible `event_ledger.py` in an isolated dir and collect one sanitized Wolfram resource snapshot. Do not activate any new Wolfram launchd service or change CodexBar/auth data. Only deliver snapshot to Darwin after its ingestion gate is ready.

## Receipts
- `DP01B_STAGING_RECEIPT/v1`: fixture tests, reader compatibility, existing ledger unchanged, PII safety, migration blockers.
- `WOLFRAM_SOURCE_ESCROW_RECEIPT/v1`: actual hash, access state, inspection state, verified private destination (not filename or user path in public), no credentials.
- `DP01B_ON_HOST_ACCEPTANCE_RECEIPT/v1`: new event type count, chain before/after, projection, checkpoint, no regression of quota stream, evidence of real read-only service metrics with statuses.

If no independent admin channel exists, do NOT claim machine changed. Use `STAGED` or `BLOCKED`, never `DONE` by inference.
