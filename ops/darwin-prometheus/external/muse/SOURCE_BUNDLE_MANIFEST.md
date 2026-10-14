# DP-01C — Muse bridge source artifact manifest

**Code-review state: SOURCE_ZIP_ONLY; GitHub review branch contains handoff docs but not the Python source or Grafana JSON yet.** The originating ChatGPT session created a local artifact `simsim-muse-dp01c-v0.1.zip` (not accessible by a GitHub URL). The user can transfer it to Darwin Codex through the ChatGPT download link.

ZIP SHA-256: `0fab448614cfd441d4a87fc6d479898a4e4a2e50230b192ab8f3beac9a49906d`

Archive contents:
- `muse_bridge.py`: isolated Muse JSON validator, append-only hash-chain, replayable SQLite and Prometheus textfile export, Python stdlib only
- `test_muse_bridge.py`: 18 automated fixture and CLI tests (18/18 PASS in sandbox)
- `fixture_synthetic.json`: synthetic non-user data
- `grafana_dashboard.json`: Prometheus dashboard template; **not deployed**
- `RUNBOOK.md`, `EXECUTE_DARWIN_WOLFRAM.md`

Actual connected Google Drive source was read, ingested only into the assistant's isolated test ledger, chain VERIFIED, SQLite PROJECTED; 2026-10-13 JSON SHA-256 `95562d42cc6c002074bc4314c7e683863de73320d1531eabb8d4a389d717edbb`. Muse's numbers remain **EXTERNAL_AGENT_TESTIMONY**; early 20:20 PDT source is PRELIMINARY, not a verified 23:30 batch.

**Critical:** Do not infer that the ZIP contents or parser are installed on Darwin. The ChatGPT Google Drive connector is NOT an OAuth token or filesystem mount accessible from Darwin or Wolfram. Verify actual sync and SSH transport on host before claiming `SOURCE_READ` there. No changes to E1, DP-01B shadow, Wolfram collector, Work models, VPN or protected main.

Next: Darwin Codex verifies artifact digest, reruns tests and real CLI smoke, checks signed/known source data, then commits reviewed source into this branch. Do not publish raw Muse JSON or Wolfram source as part of a public code review.
