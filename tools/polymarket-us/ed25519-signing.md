# Polymarket US Request Signing Protocol (Ed25519)

**Status:** VERIFIED against Official PyPI SDK & GitHub Source  
**Target API:** Polymarket US Retail API (`https://api.polymarket.us`)  
**Cryptographic Primitive:** Ed25519 (RFC 8032 / Edwards-curve Digital Signature Algorithm over Curve25519)  
**Host Authority:** Wolfram Enclave (`pavel@mindrock.capital`)  

---

## 1. Verified Scheme Specification

### A. Message Construction
Every authenticated HTTP request to `api.polymarket.us` requires an Ed25519 signature computed over a strictly constructed message string:

$$\text{message} = \text{timestamp\_ms} \parallel \text{METHOD} \parallel \text{path}$$

* **`timestamp_ms`**: Current UTC epoch time in milliseconds as an ASCII string without punctuation (e.g., `"1700000000000"`).
* **`METHOD`**: HTTP method verb in uppercase ASCII (e.g., `"GET"`, `"POST"`, `"DELETE"`).
* **`path`**: Request path component (e.g., `"/v1/account/balances"`, `"/v1/orders"`).
* **Delimiters**: **NONE**. No separators, spaces, or colons.
* **Body Inclusion**: **NO**. Request bodies (JSON payloads) are **not** included in the signed string.
* **Query Parameters**: **NO**. Query string parameters (`?limit=10&active=true`) are **not** included in `path`.

### B. Required Request Headers
```http
X-PM-Access-Key: <Key ID UUID>
X-PM-Timestamp:  <Current UTC epoch timestamp in milliseconds>
X-PM-Signature:  <Base64-encoded 64-byte Ed25519 signature>
```

### C. Server Clock Tolerance
* The server verifies that $|t_{\text{server}} - t_{\text{client}}| \le 30.0\text{ seconds}$ ($\pm 30{,}000\text{ ms}$).
* Timestamps exceeding this tolerance result in immediate HTTP `401 Unauthorized` / `AuthenticationError`.

### D. Key Material Encoding
* Developer Portal provides a Base64 string upon API key generation (`https://polymarket.us/developer`).
* Base64 decoding produces either:
  * **32 bytes**: Raw Ed25519 private seed.
  * **64 bytes**: Concatenated 32-byte seed + 32-byte public key. The signer strictly slices the **first 32 bytes** as the private seed.

---

## 2. Official Source Citations & Proof

Verification conducted against the official Polymarket US SDK distribution:
* **PyPI Package:** `polymarket-us` version **`2.4.1`**
* **Wheel SHA-256:** `d1ee7880d45b536d8261af75eee208eac8df1207a2406036d52e26d64cac95e8`
* **GitHub Repository:** [`Polymarket/polymarket-us-python`](https://github.com/Polymarket/polymarket-us-python)
* **Pinned Commit SHA:** `6fde8f2b6ea88198a199b38f7b6d8951d015a06a`

### Direct Source Mapping:
1. **`polymarket_us/auth.py` (lines 26-44):**
   ```python
   timestamp = str(int(time.time() * 1000))
   message = f"{timestamp}{method}{path}"

   secret_key_bytes = base64.b64decode(secret_key)
   if len(secret_key_bytes) == 64:
       secret_key_bytes = secret_key_bytes[:32]

   signing_key = SigningKey(secret_key_bytes)
   signed = signing_key.sign(message.encode())
   signature_b64 = base64.b64encode(signed.signature).decode()

   return {
       "X-PM-Access-Key": key_id,
       "X-PM-Timestamp": timestamp,
       "X-PM-Signature": signature_b64,
   }
   ```
2. **`polymarket_us/client.py` (lines 165-172):**
   ```python
   if authenticated:
       headers.update(
           create_auth_headers(self.key_id, self.secret_key, method, path)
       )
   response = self._http.request(
       method, url, params=params, json=body, headers=headers
   )
   ```
   *Notice that `path` is passed into `create_auth_headers`, while `params` (query parameters) and `json` (body) are passed directly to `httpx.request` and are excluded from signature generation.*

---

## 3. Five-Step Learning Plan for Agents & Operators

### Step 1: Ed25519 Cryptographic Foundation
Understand Edwards-curve Digital Signature Algorithm (RFC 8032).
* Seed is 32 bytes (256 bits).
* Deterministic signature: same $(seed, message)$ always yields identical 64-byte signature. No random nonce $(k)$ leakage.
* Verify using standard RFC 8032 test vectors.

### Step 2: Protocol Header Conformance
Learn why Polymarket US differs from Polymarket International (CLOB API):
* Polymarket International uses Ethereum EIP-712 / HMAC signatures (`POLY_SIGNATURE`, `POLY_TIMESTAMP`, `POLY_NONCE`, `POLY_API_KEY`).
* Polymarket US uses pure Ed25519 headers (`X-PM-Access-Key`, `X-PM-Timestamp`, `X-PM-Signature`).
* Do not mix SDKs or schemes across the two platforms.

### Step 3: Zero-Trust Key Isolation
Never allow API keys to leave the local machine (Wolfram):
* Key material is loaded exclusively from environment variables or macOS Keychain.
* Key material is never written to disk, never committed to git, never logged in CI/CD, and never passed over remote networks.
* Representation masking (`__repr__`) prevents inadvertent leakage in debug tracebacks.

### Step 4: Clock Synchronization & Skew Guard
Detect and fail loud on clock skew:
* Polymarket US enforces a strict $\pm 30$ second acceptance window.
* Local runner performs NTP offset verification.
* Any skew exceeding 30s raises `ClockSkewError` before any request is dispatched, preventing failed trades and API throttling.

### Step 5: Safe Operator Verification (Non-Mutating Canary)
Execute read-only verification before placing orders:
* Call harmless endpoints: `GET /v1/account/balances` or `GET /v1/portfolio/positions`.
* Confirm HTTP 200 OK without risking capital or order placement.
