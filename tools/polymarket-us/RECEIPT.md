# Production Signer Verification Receipt (MIN-98)

**Receipt ID:** `receipt-min98-polymarket-us-ed25519-v1`  
**Generated At:** 2026-10-25T19:08:00Z  
**Executing Agent:** `agy@wolfram` (Autonomous Builder)  
**Ticket ID:** Linear `MIN-98` (`run-e937f7860ab8`)  
**Target Reviewer:** `Muse` (`Role: QA-Needed`)  
**Verdict Candidate:** `PASS` (Ready for Independent QA Review)  

---

## 1. What Was Verified

1. **Official SDK Specification & Source Code Audit:**
   * Package: `polymarket-us` on PyPI
   * Version Pinned: `2.4.1`
   * Release Artifact: `polymarket_us-2.4.1-py3-none-any.whl`
   * Artifact SHA-256: `d1ee7880d45b536d8261af75eee208eac8df1207a2406036d52e26d64cac95e8`
   * GitHub Repository: `https://github.com/Polymarket/polymarket-us-python`
   * Commit SHA: `6fde8f2b6ea88198a199b38f7b6d8951d015a06a`
   * Source Citation:
     * `polymarket_us/auth.py` lines 9–44 (`create_auth_headers`)
     * `polymarket_us/client.py` lines 162–172
     * `tests/test_auth.py` lines 1–76

2. **Signing Scheme Conformance:**
   * **Message Formula:** `{timestamp_ms}{METHOD}{path}`
   * **Timestamp Unit:** Milliseconds epoch string (`str(int(time.time() * 1000))`)
   * **Body / Query Parameters:** Strictly excluded from the signed message string
   * **Headers Generated:** `X-PM-Access-Key`, `X-PM-Timestamp`, `X-PM-Signature`
   * **Server Clock Window:** $\pm 30.0\text{ seconds}$ tolerance
   * **Key Parsing:** Base64 string; if 64 bytes, uses first 32 bytes as private seed

3. **Zero-Network Unit & Integration Testing:**
   * `signer.py --self-test` executed on Wolfram: **PASS** (5/5 checks passed, zero network used)
   * `signer_reference.py --self-test` executed on Wolfram: **PASS** (zero network used)
   * `test_signer.py`: 18 tests executed in $0.009\text{s}$: **18/18 PASSED** (socket connections intercepted and blocked)

4. **Security & Threat Model Documentation:**
   * Full threat model written (`THREAT_MODEL.md`) covering $35M portfolio risks, wash-trading vector, blast radius, and 60-second emergency revocation procedure.
   * Operator runbook written (`OPERATOR_RUNBOOK.md`) for Pavel covering Developer Portal generation ceremony, macOS Keychain storage, and harmless read-only canary verification (`GET /v1/account/balances` and `GET /v1/portfolio/positions`).
   * Code review checklist attached (`CODE_REVIEW_CHECKLIST.md`).

---

## 2. Artifact Registry & SHA-256 Checksums

| File Path | SHA-256 Checksum |
|---|---|
| `tools/polymarket-us/signer.py` | `91bdeaf2f2b462bb3a583d50dddb540c8171a25b5fa6b0209b3dc70d32cd4272` |
| `tools/polymarket-us/signer_reference.py` | `79e845f0fe5749a87e10f3e7456b765b08c5eaee5ab89caedfbb3fa48c6bafa4` |
| `tools/polymarket-us/test_signer.py` | `67a82144de3d54dd53231f14d35b7bea9f88c501a1104cfc115db2aa54225edb` |
| `tools/polymarket-us/ed25519-signing.md` | `9c8efbedc8d49b869ddd63946d0a0385c66df916df0ccb2d401032f7d5eb9a1d` |
| `tools/polymarket-us/THREAT_MODEL.md` | `cdd6f4131242132ec9cdbb06734c304bad5362c3675f5fd34059c4a3e3ae9835` |
| `tools/polymarket-us/OPERATOR_RUNBOOK.md` | `324f802386cb8f918d28763128bd1a42c032fdf39ae008bd40dfa28db6e8626f` |
| `tools/polymarket-us/CODE_REVIEW_CHECKLIST.md` | `b8c9be9203259a6702668382ac2fa559cd72c280e878154a5841ca7120be4b7a` |
| Wheel: `polymarket_us-2.4.1-py3-none-any.whl` | `d1ee7880d45b536d8261af75eee208eac8df1207a2406036d52e26d64cac95e8` |

---

## 3. Protocol Phi Envelope (Φ-0.1)

```json
<!-- phi-envelope:
{
  "proto": "phi-0.1",
  "sender": "did:key:z6MkqWolframAgyBuilder#agy@wolfram",
  "recipient": "did:key:z6MkpMuseCuratorCloud#muse@mindrock.capital",
  "mandate_id": "MIN-98-POLYMARKET-US-SIGNER-0001",
  "intent": "HANDOFF_FOR_QA",
  "ticket": "MIN-98",
  "run_id": "run-e937f7860ab8",
  "evidence": {
    "wheel_sha256": "d1ee7880d45b536d8261af75eee208eac8df1207a2406036d52e26d64cac95e8",
    "upstream_commit": "6fde8f2b6ea88198a199b38f7b6d8951d015a06a",
    "self_test_verdict": "PASS",
    "unit_tests_passed": 18,
    "unit_tests_failed": 0,
    "network_used": false
  }
}
-->
```
