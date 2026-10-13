# DP-01B — Host Resource Adapter + Runtime Source Escrow

**Tracking:** [MIN-51](https://linear.app/mindrock/issue/MIN-51/dp-01b-preserve-deployed-collector-and-add-host-health-adapters) · [MIN-44](https://linear.app/mindrock/issue/MIN-44/dp-01-append-only-ledger-provenance-and-low-cost-host-collectors) (E1 HOST_DONE) · [#511](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/511).

**Status:** Implementation tested with isolated fixtures; **NOT yet installed on Darwin or Wolfram**. Live E1 remains authoritative. Nothing here changes `main`, models, quota controls, firewall, Tailscale, SSH, sudo or existing launchd programs. Deploy only with real host receipts.

## Deliverables

- `event_ledger.py`: append-only extension accepting strict, sanitized `host.snapshot` events in addition to existing three event types. Older records remain schema-compatible; old ledger hashes do not change.
- `host_adapter.py`: read-only local snapshots on Darwin/Wolfram: 1/5/15-minute load, logical CPUs, swap (`sysctl vm.swapusage`), disk capacity, Tailscale backend state (no peer data), loopback Forgejo/Ollama **TCP liveness only**, registration (not execution) of known launchd labels. Missing/blocked metrics are `null` and `READ_BLOCKED`, *never zero*. Roles are predefined `darwin` / `wolfram`; do not treat a role label alone as cryptographic host identity.
- `source_attest.py`: SHA-256 + conservative secret/identifier heuristics for the actual deployed Wolfram `push_first_collector.py`; **does not print source** or grant permission to publish it. Rejects symlinks, huge/nonregular/unstable files. `HUMAN_REVIEW_REQUIRED` even for zero scanner matches.
- `test_host_adapter.py`: mocked host-source tests, node-role gates, changed-content conflicts, redaction, journal reconstruction, source fingerprint/secret behavior. Everything standard-library Python and zero API/LLM calls.

**Known actual deployment:** Wolfram launchd `com.chitakasha.token-governor-push` runs `$HOME/token-governor/push_first_collector.py` SHA-256 `a916cdffa81312b12ff1761dc5f81fbb30dcb04670c52ad02e08eeee07f22f81`. It is **not** reference `push_quota.py`; do not replace it. Darwin Event Ledger user LaunchAgent `org.chitakasha.darwin-prometheus-ledger` ran unattended 2026-10-13 at 16:14 PDT.

## Phase 0 — Existing-source continuity gate (Darwin Codex)

1. Use the exact new review branch and commit. Fetch read-only. On Darwin, inspect existing `~/darwin-prometheus/event_ledger.py` and its current hash, the loaded `org.chitakasha.darwin-prometheus-ledger` plist, the last natural receipt, the real SQLite schema and chain tip. Don't modify source during this step.
2. In a disposable temporary directory, copy the new `event_ledger.py`, `host_adapter.py`, `source_attest.py`, `test_host_adapter.py`, original E1 tests. Run all tests on the actual macOS/Python environment. Verify **current production** journal via old E1 reader first, then via new extended reader pointed at the existing journal **without appending**. On verification mismatch, STOP, leave production intact.
3. Safe fake test: use a disposable ledger and `python3 host_adapter.py collect --node darwin | python3 host_adapter.py ingest --root "$TEMP_LEDGER" --expected-node darwin`. Verify, project, checkpoint, verify. The collected record is real local host metrics but deposited only in the disposable ledger. Do NOT substitute synthetic quota sample in production.

## Phase 1 — Darwin real sample (separate reviewed bounded change)

After dual-read verification and backup of only code file (not journal), copy new `event_ledger.py` plus `host_adapter.py` into Darwin `~/darwin-prometheus` with a clear local rollback plan. Do **not** replace `run_cycle.py` or its launchd plist. Run:

```sh
umask 077
python3 "$HOME/darwin-prometheus/host_adapter.py" collect --node darwin \
  | python3 "$HOME/darwin-prometheus/host_adapter.py" ingest \
    --expected-node darwin
python3 "$HOME/darwin-prometheus/event_ledger.py" verify
python3 "$HOME/darwin-prometheus/event_ledger.py" project
python3 "$HOME/darwin-prometheus/event_ledger.py" checkpoint
python3 "$HOME/darwin-prometheus/event_ledger.py" verify
```

Inspect exit codes of **both** pipe stages (`pipefail` where supported), count exactly one genuinely new `host.snapshot`, check `ledger.sqlite3` projection and permissions; prove prior quota and host events are unchanged. If the new schema extension fails on the real journal, stop, preserve evidence and don't revert journal data. Note that the new event type makes older E1 source code unable to verify a ledger with a host.snapshot; **retain a copy of the new reader and do not roll back to the old reader after writing the new type** without a proper migration protocol. This is an irreversible format-compatibility gate.

## Phase 2 — Wolfram source escrow, no deployment change

The **already authorized Wolfram→Darwin SSH** route works; inbound Wolfram SSH does not. Run all source access in Wolfram Codex's local session. Do not read or copy private keys, cookies or raw CodexBar JSON.

```sh
# Wolfram, local read-only. This tool shows only SHA+review flags.
python3 "$HOME/darwin-prometheus/source_attest.py" \
  --file "$HOME/token-governor/push_first_collector.py" \
  --expected-sha256 a916cdffa81312b12ff1761dc5f81fbb30dcb04670c52ad02e08eeee07f22f81
```

`source_attest.py` requires `event_ledger.py` only for optional `host_adapter collect`, not for code attestation. If tool is not on Wolfram, copy *this verified text source* locally without altering live collector. At a trusted private destination on Darwin, initiate a **Wolfram-originated** transfer by SSH/SCP of the single actual deployed source file, and compare SHA-256 on BOTH sides. Restrict transfer location to a private folder (`0700`) and file (`0600`). Manually review the entire file and local scan results for hardcoded secrets, even if heuristic count is zero. The provided scanner is NOT proof there are no credentials.

If Forgejo repo/branch access and permissions are actually verified, commit *sanitized review material* in an unpublished private Forgejo review branch (or original if cleared). Never upload original uninspected source to public GitHub, any issue, ChatGPT attachments or Google Drive. No automatic merge or hot-replace. If no verified private route exists, keep an encrypted/local private copy and emit `READ_BLOCKED_PUBLICATION`.

## Phase 3 — Wolfram resource telemetry (opt-in, no daemon yet)

After success on Darwin, copy only the approved sidecar **`host_adapter.py` and updated `event_ledger.py`** to a separate user-owned staging folder on Wolfram. Read-only collect:

```sh
python3 /path/to/staged/host_adapter.py collect --node wolfram
```

Inspect *sanitized* result locally. If user authorizes delivery, invoke existing strictly authenticated outbound SSH with `BatchMode=yes`, `StrictHostKeyChecking=yes`, `ForwardAgent=no`, **no** agent forwarding or new port. On Darwin call the exact `host_adapter.py ingest --expected-node wolfram` through SSH stdin, then verify with the journal. Do NOT add a new hourly agent yet. Do not assume `--node` means authorized host identity; only use verified peer SSH key / explicit expected role. Capture `SOURCE_READ_LOCAL` vs `READ_BLOCKED` by field.

## Exit criteria

1. Darwin E1 ledger still verifies after new-format test, source unchanged except audited reader extension.
2. At least one real `host.snapshot` from Darwin (and optionally Wolfram) is appended and projected with successful verified checkpoint; service states clearly labeled as **liveness/configuration**, not functional health.
3. Source-attestation hash matches actual running collector; content disclosure only with verified private review destination after secrets audit.
4. Older E1 events remain verifiable with the **new** reader; format compatibility and rollback implications explicitly recorded.
5. Manual verified receipt posted into #511 / MIN-51; no cloud Work quota claims or model changes.

**No DONE before these are tested ON Darwin/Wolfram; isolated tests only establish fixture PASS.**
