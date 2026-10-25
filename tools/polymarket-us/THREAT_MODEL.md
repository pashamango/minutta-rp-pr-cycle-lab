# Threat Model & Security Architecture: Polymarket US API Key

**Security Baseline:** $35M Portfolio Enclave ($10M Equity + $25M Credit Line)  
**Host Target:** Wolfram Local Enclave (`pavel@mindrock.capital`)  
**Scope:** Ed25519 Request Signer & Key Material Management  
**Classification:** HIGH RISK / INSTITUTIONAL ENCLAVE  

---

## 1. Key Capabilities & Scope of Authority

The Polymarket US API Key (`X-PM-Access-Key` UUID + Ed25519 private seed) possesses **FULL TRADING AND ACCOUNT AUTHORITY**:

1. **Order Execution & Market Making:**
   * Submit arbitrary Limit, Market, and RFQ orders across all active markets (`POST /v1/orders`).
   * Cancel open orders (`DELETE /v1/orders/{order_id}`, `DELETE /v1/orders`).
   * Trade against any market book at any price.
2. **Capital Drainage Risks (Adverse Fill Attacks):**
   * While direct automated wire/crypto withdrawals may require secondary confirmation, an attacker with order placement capability can **completely drain an account** within minutes by executing cross-trades / wash trades at off-market prices against attacker-controlled counterparties.
3. **Information Disclosure & Portfolio Intelligence:**
   * Query real-time balances, credit utilization, and margin limits (`GET /v1/account/balances`).
   * Inspect all open positions, fill history, and trading strategies (`GET /v1/portfolio/positions`, `GET /v1/portfolio/activities`).

**Conclusion:** Compromise of this key is functionally equivalent to complete loss of funds ($35M blast radius).

---

## 2. Why the Key NEVER Leaves Wolfram

1. **Air-Gapping from Autonomous Cloud Agents (Muse / External LLMs):**
   * Autonomous cloud agents (e.g., Muse, Gemini Cloud, Claude Cloud) operate in multi-tenant environments with web search, prompt contexts, and third-party APIs.
   * If the private key enters an LLM context or cloud memory, it is vulnerable to prompt injection, transcript exposure, accidental logging, and cloud account compromise.
   * By constitutional mandate (AGENTS.md Section 10A), cloud agents generate market intelligence and weight matrices; signing **MUST** execute exclusively on Pavel's physical hardware (Wolfram).
2. **Zero Remote Network Transmission:**
   * The private seed is never sent over SSH, HTTP, WebSocket, or RPC.
   * Only the resulting cryptographic signatures and headers (`X-PM-*`) leave the host inside outbound HTTPS calls directly to `api.polymarket.us`.
3. **Local Enclave Protections on macOS Wolfram:**
   * Key material is stored either in memory during runtime or in the macOS Keychain (`security` framework).
   * Key material is never stored in plain-text disk files, git repositories, `/tmp`, shell history (`.zsh_history`), or environment dumps.

---

## 3. Threat Matrix & Attack Vectors

| Threat Vector | Severity | Mitigations Implemented |
|---|---|---|
| **Memory / Log Leakage** | Critical | `__repr__` and `__str__` scrub secrets. Exceptions do not echo key bytes. |
| **Shell History Leakage** | High | CLI strictly rejects keys as command-line arguments. Keys are read via environment variable or Keychain pipe. |
| **Clock Skew Replay / Rejection** | Medium | Built-in SNTP clock skew verification detects offsets $> \pm 30\text{s}$ and aborts immediately. |
| **Signature Forgery / Tampering** | Critical | Pure Ed25519 (RFC 8032) deterministic signatures over canonical string `{timestamp}{METHOD}{path}`. |
| **Unauthorized Subagent Access** | High | Isolated workspace sandbox; subagents operate in read-only mode with zero network and no access to host Keychain. |
| **Compromised Dependency (Supply Chain)** | High | Pinned package versions (`cryptography>=50.0.0`, `polymarket-us==2.4.1`), zero extraneous dependencies in signing path. |

---

## 4. Emergency Revocation Procedure

If a key is suspected of exposure, follow this **IMMEDIATE RUNBOOK (Target: < 60 seconds)**:

### Phase 1: Revocation in Portal (The Kill Switch)
1. Navigate immediately to [https://polymarket.us/developer](https://polymarket.us/developer).
2. Authenticate via Pavel's primary credentials.
3. Locate the compromised Key ID under **API Keys**.
4. Click **Revoke Key** and confirm.
   * *Effect:* Polymarket API gateways immediately reject all subsequent requests bearing this Key ID with HTTP `401 Unauthorized`.

### Phase 2: Local Purge on Wolfram
1. Remove environment variables from active shell sessions:
   ```bash
   unset POLYMARKET_KEY_ID
   unset POLYMARKET_SECRET_KEY
   ```
2. Delete the item from macOS Keychain:
   ```bash
   security delete-generic-password -s "polymarket-us" -a "<COMPROMISED_KEY_ID>"
   ```
3. Verify local environment is scrubbed:
   ```bash
   env | grep -i POLYMARKET
   # (Must return empty)
   ```

### Phase 3: Emergency Position Audit
1. Open the Polymarket US web interface.
2. Check **Active Orders** and click **Cancel All Open Orders**.
3. Review **Recent Activity** for unexpected fills.
