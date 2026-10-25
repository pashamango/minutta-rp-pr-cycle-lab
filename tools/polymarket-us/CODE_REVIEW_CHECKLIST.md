# Security & Code Review Checklist: Polymarket US Signer

**Ticket:** MIN-98  
**Component:** `tools/polymarket-us/signer.py`  
**Reviewer Target:** Independent QA (Muse / Codex)  
**Baseline Standard:** Mindrock Agent Constitution (AGENTS.md) Section 10 & Critical Enclave Guidelines  

---

## 1. Secrets & Exposure Audit

- [x] **Zero Hardcoded Secrets in Codebase:**
  - Audited `signer.py`, `signer_reference.py`, `test_signer.py`.
  - Only official public test vectors (RFC 8032 and official SDK dummy strings) are included in test suites.
  - No private keys, API secrets, or credentials exist in code, comments, or documentation.

- [x] **Zero Secret Leakage in Representations (`__repr__` / `__str__`):**
  - `PolymarketSigner.__repr__` explicitly masks private key material: `<PolymarketSigner key_id=... status=ACTIVE>`.
  - Secret key bytes are never displayed in string dumps, exception messages, or stack traces.

- [x] **Zero Secret Leakage via Process List / Shell History:**
  - Signer CLI (`signer.py`) does **not** accept secret keys as command-line arguments (preventing visibility via `ps aux`, `pgrep`, or shell history).
  - Keys are loaded strictly via environment variables (`POLYMARKET_SECRET_KEY`) or macOS Keychain (`security` pipe).

- [x] **Zero Secrets in Disk Files / Scratch Dirs:**
  - No secret files, tokens, or private keys written to disk or `/tmp`.

---

## 2. Key Material Ingestion & Validation

- [x] **Strict Ingestion Sources:**
  - Supported: `PolymarketSigner.from_env()`, `PolymarketSigner.from_keychain()`, `PolymarketSigner.ephemeral()`.
  - Explicit error handling if required environment variables or Keychain accounts are absent (`ConfigurationError`).

- [x] **Base64 Decoding & Length Validation:**
  - Base64 validity validated before parsing.
  - Length check enforces 32-byte seeds (pure seed) or 64-byte keypairs (seed + public key).
  - Truncation to 32 bytes strictly mirrors official SDK implementation (`polymarket_us/auth.py` lines 32-35).
  - Any other byte lengths (e.g. 16, 48, etc.) raise immediate `ConfigurationError`.

---

## 3. Cryptographic Correctness & Scheme Conformance

- [x] **Exact Conformance with Official PyPI SDK:**
  - Message format verified: `{timestamp_ms}{METHOD}{path}` with no delimiters.
  - Body and query parameters strictly excluded from the signed message.
  - Timestamp units verified: milliseconds epoch string (`str(int(time.time() * 1000))`).
  - Headers generated conform to official gateway requirements:
    - `X-PM-Access-Key`
    - `X-PM-Timestamp`
    - `X-PM-Signature`
  - Ed25519 signatures verified against RFC 8032 test vectors 1 and 2.
  - Ephemeral round-trip signing and verification succeeds.
  - Tamper detection verifies invalidation on modified method, path, timestamp, or signature bits.

---

## 4. Clock-Skew Detection & LOUD Failure

- [x] **SNTP Clock Skew Verification:**
  - Built-in SNTP client (`query_ntp_offset`) verifies host offset against NTP servers.
  - Strict enforcement: skew exceeding $\pm 30.0$ seconds raises `ClockSkewError`.
  - Pre-flight CLI check available via `--check-clock`.

---

## 5. Dependency Pinning & Supply Chain Security

- [x] **Minimal Dependency Footprint:**
  - Relies solely on Python standard library + `cryptography` (which is already pinned and validated in the local Wolfram virtual environment).
  - Wheel artifact pinned: `polymarket_us-2.4.1-py3-none-any.whl` (SHA256: `d1ee7880d45b536d8261af75eee208eac8df1207a2406036d52e26d64cac95e8`).
  - GitHub commit pinned: `6fde8f2b6ea88198a199b38f7b6d8951d015a06a`.

---

## 6. Test Suite Zero-Network Enforcement

- [x] **Socket Blocking Fixture:**
  - `BaseZeroNetworkTestCase` in `test_signer.py` actively patches `socket.socket.connect` and `socket.socket.sendto` to raise `RuntimeError` if any network I/O is attempted.
  - All 18 unit tests pass with zero network activity in $< 10\text{ ms}$.
  - Standalone self-test (`--self-test`) executes completely offline without network dependencies.
