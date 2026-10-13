# DP-01 / #511 — Deployed Runtime Provenance, 2026-10-13

**Evidence class:** USER_SUPPLIED_HOST_RECEIPT (Wolfram Codex); this ChatGPT session did **not** independently retrieve the local receipt JSON, inspect the macOS launchctl job, read the running source code, or query Darwin SQLite. All operational claims below are reported by the user from on-host Codex.

## Discovered runtime (not the synthetic reference installer)

| Field | Wolfram active deployment (host-reported) | Source-tree reference |
|---|---|---|
| launchd label | `com.chitakasha.token-governor-push` | `org.chitakasha.token-governor-push` |
| GUI user domain | `gui/501` | unset / installer-dependent |
| running entrypoint | `$HOME/token-governor/push_first_collector.py` | `$HOME/token-governor/push_quota.py` |
| running entrypoint SHA-256 | `a916cdffa81312b12ff1761dc5f81fbb30dcb04670c52ad02e08eeee07f22f81` | not comparable, different implementation |
| running `governor.py` | matches reviewed reference (per host report) | `ops/token-governor/governor.py` |
| `push_quota.py` on Wolfram | absent; **not** expected for active job | exists in this review branch |
| control chain | push_first_collector.py -> governor.py probe -> outbound strictly authenticated SSH -> Darwin governor.py ingest | push_quota.py -> governor.py probe -> SSH -> Darwin governor.py ingest |
| last observed source update | `2026-10-13T22:46:09Z` | n/a |
| last delivery | `2026-10-13T22:46:16Z` | n/a |
| Darwin Governor SQLite | three genuine observations, owner-only 0600 (reported) | n/a |
| launchd exit | 0 (reported) | n/a |

Earlier two distinct source update times were `2026-10-13T21:45:29Z` and `2026-10-13T21:45:56Z`. The third `22:46:09Z` update is 60m13s after the second, a strong indication of approximately hourly cadence. **It does not by itself demonstrate a Darwin Event Ledger unattended launchd run**, nor independently prove the absence of manual intervention on Wolfram.

## Disposition

- `WOLFRAM_RUNTIME_PROVENANCE=IDENTIFIED`.
- `REFERENCE_IDENTITY=DIFFERENT_IMPLEMENTATION`, **not** corrupted/missing service.
- The absence of `$HOME/token-governor/push_quota.py` is a path-specific `MISSING`, **not** proof of a broken or tampered running process.
- **Do not reinstall, overwrite, restart, migrate, or disable** the functioning Wolfram push collector to force reference hash equality.
- Keep separate `CODE_REFERENCE` vs `DEPLOYED_RUNTIME` hashes. Never claim reference source is deployed unless content hash agrees.
- CodexBar readings are `UNVERIFIED_FOR_WORK`, and attribution stays `UNATTRIBUTED_CLOUD_WORK`.

## Follow-up: preserve the actual deployed source

1. On Wolfram, *read-only*: independently verify `launchctl print gui/501/com.chitakasha.token-governor-push`, the job plist and resolved entrypoint, plus `shasum -a 256` of actual script. Record only sanitized command metadata and hash, not environment variables or credentials.
2. Obtain a private, least-privilege copy of the **actual source file**, first checking it for secrets, local identities, tokens, access keys and credential-bearing comments. Do not blindly publish private source or full logs. Prefer Darwin canonical Forgejo review branch; alternatively prepare a redacted patch and get separate review. No direct push to protected main.
3. Preserve the live file unmodified while comparing source to reviewed `ops/token-governor/push_quota.py`. Add regression tests based on actual transport semantics; do not conflate matching outputs with identical code.
4. On Darwin, read-only run `event_ledger.py sync-governor`, verify chain and checkpoint and replay projection; record whether the third real quota observation reached the **ledger**, separately from the Governor SQLite ingestion. Verify a later **natural** Darwin LaunchAgent run with an independent timestamp. Do not kickstart just to claim unattended success.
5. Optional future: pin code source digest, launchd ProgramArguments and signed/manifests in the event ledger as an attestation, without leaking absolute private home paths; guard against misleading hash checks of absent paths.

Tracking: GitHub Issue #511, Linear MIN-44 (Event Ledger) and MIN-45 (quota truth). Remote Login remains OFF; existing outbound strict SSH remains the only confirmed host-to-host route.

**DP-01 installation:** PARTIAL until on-host later unattended Darwin ledger run is documented. **DP-02 Work quota:** UNVERIFIED. This file is a provenance record, not source-code restoration.
