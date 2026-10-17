# NICLI Dispatcher v0.1 — Deterministic Control Plane & Shadow Admission

NICLI Dispatcher v0.1 (`nicli_dispatcher`) implements the MIN-72 / MIN-74 (NICLI-B) control-plane specification and MIN-75 (NICLI-C) shadow-admission gates using the Python standard library.

## Key Architecture & Guarantees

1. **Pinned Model Policy**:
   - Model is pinned to **Gemini 3.8 Flash Medium**.
   - No automatic model escalation, fallback, billing, credits, subagents, or Codex.
   - Zero model inference calls when the queue is empty, paused, or blocked by admission/quota.

2. **Dual-Lane Auth & Free-Tier Quota Isolation**:
   - Strict mapping between auth modes and quota buckets:
     - `api_key` $\rightarrow$ `ai-studio-free-tier` (strictly free-tier only; fails closed if billing or overages are enabled).
     - `antigravity_google_ai_pro` $\rightarrow$ `antigravity-google-ai-pro` (managed subscription lane; rejects billing overages).
   - Cross-lane mixing is rejected at configuration and runtime.
   - Unknown or exhausted quota fails closed without retrying indefinitely.

3. **Deterministic Shadow-Admission Gates**:
   A candidate Linear issue is admitted **only** if all gates pass:
   - **Identifier Safety**: Alphanumeric ID matching `^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$` and team key in `{"MIN", "Mindrock"}`.
   - **Status**: Must be in `Todo` status.
   - **Veto & Hold Guard**: Neither the issue nor its parent may contain `Human-Hold`, `VETO: Human-Hold`, `Icebox`, `Canceled`, or `Duplicate`.
   - **Role Requirement**: Must carry `Role: Builder-Ready`.
   - **Role Conflict Prevention**: Neither the issue nor its parent may carry `Role: Architect-Needed`.
   - **Parent PM Watch**: Parent issue must exist and carry `Role: PM-Watch`.
   - **Governance Provenance**: Parent IC decision reference and R4 handoff references must be present.
   - **Dependency Gate**: All `blocked_by` dependencies must have status `Done`.
   - **Concrete Execution Spec**: `source_repo`, `source_commit`, and `acceptance_commands` are mandatory.

4. **SQLite Transactional Leases & Crash Isolation**:
   - Monotonic fencing generation per lease claim.
   - Global $\text{WIP} = 1$ concurrency ceiling.
   - **Crash isolation gate**: If a worker crashes or expires, predecessor process must be confirmed stopped and isolated before a successor attempt may claim a lease.
   - Stale fencing generations cannot heartbeat or report results.

5. **Boundary Rechecks**:
   - Boundary 1: Recheck live Linear issue state immediately prior to lease claim.
   - Boundary 2: Recheck live Linear issue state immediately prior to publishing review branch (aborts on mid-flight veto or spec mutation).

6. **Credential Separation & Protected Branches**:
   - Dispatcher keychain handle, worker keychain handle, and publisher keychain handle are strictly disjoint.
   - Worker job manifest contains **zero** Linear or publisher tokens.
   - Scoped publisher strictly rejects protected branches (`main`, `master`, `release`, `production`).

7. **Honest Completion (`END != DONE`)**:
   - Exit code 0 is necessary but not sufficient.
   - Builder ends at `In Review + QA-Needed` with `END=True` and `DONE=False`.
   - Builder **never** self-certifies `DONE`.
   - Only an independent reviewer (`GPT` or `Muse`) PASS receipt with rerun verification tests sets `DONE=True`.

---

## Shadow-Admission CLI

### Usage

Run shadow admission against a JSON fixture:

```sh
# Run via python module
python3 -m nicli_dispatcher shadow-admit --input fixtures/shadow_admission_fixture.json

# Run with explicit deterministic timestamp and formatted output
python3 -m nicli_dispatcher shadow-admit \
  --input fixtures/shadow_admission_fixture.json \
  --now 2026-10-16T23:30:00Z

# Inspect component metadata
python3 -m nicli_dispatcher version
```

### JSON Schema

The CLI produces structured JSON conforming to `NICLI_SHADOW_ADMISSION/v1`:

```json
{
  "schema": "NICLI_SHADOW_ADMISSION/v1",
  "generated_at": "2026-10-16T23:30:00Z",
  "pinned_model": "Gemini 3.8 Flash Medium",
  "cli_version": "0.1.0",
  "auth_mode": "api_key",
  "quota_bucket": "ai-studio-free-tier",
  "max_wip": 1,
  "summary": {
    "total_evaluated": 6,
    "admitted_count": 1,
    "rejected_count": 5,
    "model_calls": 0,
    "rejections": {
      "MIN-69": "UNMET_DEPENDENCY",
      "MIN-70": "MISSING_REPOSITORY_OR_ACCEPTANCE",
      "MIN-71": "VETO_OR_HOLD",
      "MIN-72": "CONFLICTING_ROLE_STATE",
      "MIN-73": "NOT_TODO_STATUS"
    }
  },
  "decisions": [...]
}
```

---

## Verification & Testing

Execute the test suites:

```sh
# Dedicated NICLI Dispatcher unit and CLI tests
python3 -m pytest -p no:cacheprovider tests/test_nicli_dispatcher.py tests/test_nicli_cli.py

# Full repository test suite (54 tests)
python3 -m pytest -p no:cacheprovider
```
