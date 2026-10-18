# Muse Review Request: NICLI Dispatcher v0.1 (REWORK / Clean Package)

**Task Reference**: MIN-74 / SIMSIM — Clean Release Candidate (REWORK per Muse QA Receipt v1)  
**Branch**: `minutta/min-74-nicli-b-deterministic-linear-dispatcher-leases-and-isolated`  
**Base Commit SHA**: `59df886447be56bc15bab73ac4556e4518548385`  
**Date**: 2026-10-18  
**Pinned Model**: Gemini 3.8 Flash Medium  

---

## Notice on Delivery & Authority Boundaries

> [!IMPORTANT]
> **REVIEW_READY_PENDING is a local review artifact only.**
> In compliance with MIN-74 / MIN-75 constraints:
> - No daemon process is running.
> - No uncoordinated remote Git push has been executed.
> - No unauthorized Linear mutations or state transitions have been performed.
> - No credentials or keychains have been altered.
> - No protected branches (`main`, `master`, `release`, `production`) have been modified.
> - The builder has NOT self-approved QA (END=True, DONE=False).
> - **Authority Gate (D2)**: The reviewer (Muse) assesses artifacts and returns an independent verdict (`PASS` / `REWORK`). Transition of MIN-74 to `DONE=True` is strictly gated on Pavel's explicit authorization.

---

## Builder Receipt

```json
{
  "schema": "NICLI_RUN_RECEIPT/v1",
  "issue_id": "MIN-74",
  "builder": "Gemini 3.8 Flash Medium",
  "host_id": "darwin-pilot",
  "auth_mode": "api_key",
  "quota_bucket": "ai-studio-free-tier",
  "source_commit": "aa500fe224f2991d18011254e04ef76ea5858678",
  "final_commit": "59df886447be56bc15bab73ac4556e4518548385",
  "status": "COMPLETED_AWAITING_QA",
  "linear_projection": "In Review + QA-Needed",
  "END": true,
  "DONE": false,
  "blocker": null,
  "reviewer_receipt_ref": null,
  "note": "Builder execution complete. END=True recorded; DONE=False preserved until independent Muse reviewer PASS receipt and Pavel sign-off."
}
```

---

## REWORK Resolution Summary (Addressing Muse QA Receipt v1)

| Discrepancy | Muse Finding | Clean Package Resolution |
|:---|:---|:---|
| **D1 (Provenance)** | Host/lane unverified vs Antigravity Pro claim | Builder explicitly operates on `darwin-pilot` via `api_key` (`ai-studio-free-tier`). Dual-lane isolation (`api_key` vs `antigravity_google_ai_pro`) verified by test suite. |
| **D2 (Reviewer Authority)** | Request suggested reviewer executes `DONE=True` | Clarified: Reviewer delivers `verdict: PASS`. Transition to `DONE=True` is reserved exclusively for Pavel. |
| **D3 (Duration)** | Mismatch between claimed duration and `tests.log` | Exact duration (`0.10s`) aligned bit-for-bit with `tests.log`. |
| **D4 (Linear Status)** | Outdated status projection | Linear issue MIN-74 updated to `In Review` with `Role: QA-Needed`. |
| **D5 (Packaging Gap)** | 5 non-component tests broke `pytest` on archive collection | Scoped release bundle includes only the 14 self-contained component tests (`test_nicli_dispatcher.py` + `test_nicli_cli.py`). Pytest passes 14/14 with zero missing dependencies. |

---

## Test Commands & Results

### Dedicated NICLI Dispatcher & CLI Tests

```sh
python3 -m pytest -p no:cacheprovider tests/test_nicli_dispatcher.py tests/test_nicli_cli.py
```

**Result**: `14 passed in 0.10s` (100% pass rate)
- 9 dedicated core tests:
  - Empty queue & admission rejections make zero model calls
  - Duplicate / concurrent claims & WIP=1 ceiling
  - Crash restart requires predecessor isolation & fences stale generation
  - Changed spec & veto detected at claim / publish boundaries
  - Unknown / exhausted quota & billing fail closed
  - Timeout, full disk, and HTTP 401/403/429 controls
  - Missing artifact & exit 0 with failed tests never claim DONE
  - Credential separation, protected branch guard & independent QA DONE transition
  - Dual-lane auth/quota isolation (`api_key` vs `antigravity_google_ai_pro`)
- 5 dedicated CLI tests:
  - Version & metadata command
  - Candidate JSON shape parsing (array, object, wrapper)
  - Fixture shadow-admission evaluation
  - Auth mode & quota bucket validation
  - Bit-for-bit execution determinism

---

## Deterministic Shadow-Admission Fixture & Execution

### Execution Command

```sh
python3 -m nicli_dispatcher shadow-admit \
  --input fixtures/shadow_admission_fixture.json \
  --now 2026-10-16T23:30:00Z
```

### Evaluation Summary

| Candidate | Status | Reason / Blocker | Admission Verdict |
|:---|:---|:---|:---:|
| **MIN-68** | Todo | Meets IC/R4, Role: Builder-Ready, parent Role: PM-Watch, repo/commit/acceptance | **ADMITTED** |
| **MIN-69** | Todo | Dependency on MIN-68 is incomplete | `UNMET_DEPENDENCY` |
| **MIN-70** | Todo | Missing source_repo / acceptance_commands | `MISSING_REPOSITORY_OR_ACCEPTANCE` |
| **MIN-71** | Todo | Carries `Human-Hold` veto | `VETO_OR_HOLD` |
| **MIN-72** | Todo | Parent MIN-67 has `Role: Architect-Needed` | `CONFLICTING_ROLE_STATE` |
| **MIN-73** | In Progress | Task status is `In Progress` (not `Todo`) | `NOT_TODO_STATUS` |

**Zero model calls** were made during evaluation.

---

## Release Artifacts & SHA-256 Hashes

| Relative Path | SHA-256 Digest |
|:---|:---|
| `nicli_dispatcher/__init__.py` | `eb8d3784a78f68b66d030a75632a990408ec946541b93ed0fc51abe9cf3bdf84` |
| `nicli_dispatcher/core.py` | `b2e12a8df04ba58bbf21f7c97f0a581a02ad51c5b1d9422ef4a988eacc9a9077` |
| `nicli_dispatcher/cli.py` | `28d7df34e9733ae1a3abfac19cb9130da9a8a6f0b1adeedef0852998b5a1a57c` |
| `nicli_dispatcher/__main__.py` | `d7a6ca28a5fef3ee042638e898b527b171b2232ad6ce7d13d269a1d42809e6fe` |
| `nicli_dispatcher/README.md` | `10ad775e09b8c88f69b5cb648ff53c4ada2a1291e3f6d2a850a1c503cd90500e` |
| `tools/nicli-shadow-admission` | `16779bd6b08b7b971862a804a4ec06d2d4b925cf5399e6b6bb553f262d626a84` |
| `fixtures/shadow_admission_fixture.json` | `e91c5b10595d88ae86ba1f0f18e5ec0cce131d45145235e40c1922cd32a8ef16` |
| `artifacts/shadow_admission_output.json` | `e6b208816423ba9f6d3938304543ef40e60658c7332c25fdb4b0a0176458d327` |
| `tests/test_nicli_dispatcher.py` | `0167301a9baeb85803a131aead629b809697a60f4e4c8e68cde452342c20016f` |
| `tests/test_nicli_cli.py` | `3b5c735c9160287a27ba407f16b8238ea8997d4d6af5561f8167606b7f987ff8` |
| `tests.log` | `60673c1b2ce44861ac6cd1c2b580d31f4c6cf0855d374deea9e0240b05d426a0` |
| `README.md` | `8334612df5837826a11218b880852eb51a2a88af79d804cd9fd5b54934a5479c` |
| `ARTIFACT_SHA256_HASHES.json` | `fbfc4129dfd0644d4e34ca7fc60e062cf01f2fe601b30b1e6ef76e8729041065` |
| `RELEASE_MANIFEST_v0.1.json` | `4912b0fbd8bb93f1b1097b55c3764e66a8bc966d428af134084cbacccc9ee6c1` |

---

## Instructions for Independent Muse Reviewer

1. Unpack clean package `MIN74-release.zip`.
2. Verify artifact SHA-256 hashes against `ARTIFACT_SHA256_HASHES.json` and `RELEASE_MANIFEST_v0.1.json`.
3. Rerun acceptance checks: `python3 -m pytest -p no:cacheprovider tests/test_nicli_dispatcher.py tests/test_nicli_cli.py` (or `pytest tests/`).
4. Rerun deterministic shadow admission on the fixture.
5. If all checks verify cleanly, generate an independent `ReviewerReceipt(verdict="PASS", checks_rerun=True)` and submit for Pavel's final sign-off.
