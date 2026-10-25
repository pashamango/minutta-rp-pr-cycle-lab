# Operator Runbook: Polymarket US Key Generation & Verification

**Audience:** Principal Pavel Cherkashin (`pavel@mindrock.capital`)  
**Enclave Target:** MacBook Wolfram (Master Gateway)  
**Security Level:** Production Trading Enclave ($35M baseline)  

---

## 1. Key Generation Ceremony (Developer Portal)

> [!IMPORTANT]
> The Polymarket US developer portal displays the API Secret Key **EXACTLY ONCE**. If you close or refresh the window without securely saving it, the key is permanently lost and must be revoked and regenerated.

### Step 1: Access the Portal
1. Open your browser on Wolfram and navigate to:
   [https://polymarket.us/developer](https://polymarket.us/developer)
2. Log in using your verified account credentials.
3. Click **API Keys** -> **Create New API Key**.
4. Set a descriptive label (e.g., `wolfram-production-runner-01`).
5. Copy both fields:
   * **Key ID (UUID):** e.g., `a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d`
   * **Secret Key (Base64 string):** e.g., `nWGxne/9WmC6hEr0kuwsxERJxWl7MmkZcDusAxyuf2A=`

---

## 2. Secure Local Storage Options on Wolfram

Choose **Option A (macOS Keychain - Recommended)** or **Option B (Protected Environment)**:

### Option A: Store in macOS Keychain (Recommended)
This stores the secret encrypted in the macOS secure enclave, accessible only by your user account on Wolfram:

```bash
# Set your Key ID and prompt securely for the secret without shell history leakage:
export POLYMARKET_KEY_ID="<YOUR_KEY_ID_UUID>"

# Securely save to macOS Keychain (the prompt prevents secrets in history):
security add-generic-password \
  -s "polymarket-us" \
  -a "$POLYMARKET_KEY_ID" \
  -w
# (Type or paste the Base64 secret key when prompted, then press Enter)
```

To verify the secret was saved:
```bash
security find-generic-password -s "polymarket-us" -a "$POLYMARKET_KEY_ID" -w > /dev/null && echo "Keychain entry verified successfully."
```

### Option B: Ephemeral Environment Variables
For interactive sessions, load the keys directly into your terminal session without writing to disk:

```bash
read -s -p "Enter Polymarket Key ID: " POLYMARKET_KEY_ID && export POLYMARKET_KEY_ID && echo ""
read -s -p "Enter Polymarket Secret Key: " POLYMARKET_SECRET_KEY && export POLYMARKET_SECRET_KEY && echo ""
```

---

## 3. Harmless Read-Only Verification

Before authorizing any trading or daemon execution, run a non-mutating canary check. This confirms that signatures, clock synchronization, and account permissions succeed without placing orders or risking funds.

### Step 1: Pre-Flight Clock Synchronization Check
```bash
/Users/pavelcherkashin/ChitAkasha-Wolfram/venv/bin/python \
  ~/workspace/passive-income/tools/polymarket-us/signer.py --check-clock
```
*Expected output:*
```text
Checking system clock skew against pool.ntp.org...
System clock offset: +0.0012s (Tolerance: +-30.0s) -> OK
```

### Step 2: Test Harmless Account Balances Query (`GET /v1/account/balances`)

#### Using the Signer CLI with curl:
```bash
# If using Keychain:
EVAL_CMD=$(/Users/pavelcherkashin/ChitAkasha-Wolfram/venv/bin/python \
  ~/workspace/passive-income/tools/polymarket-us/signer.py \
  --keychain \
  --sign \
  --method GET \
  --path /v1/account/balances \
  --format curl)

# Execute the curl command:
eval "$EVAL_CMD"
```

#### If using Environment Variables:
```bash
EVAL_CMD=$(/Users/pavelcherkashin/ChitAkasha-Wolfram/venv/bin/python \
  ~/workspace/passive-income/tools/polymarket-us/signer.py \
  --sign \
  --method GET \
  --path /v1/account/balances \
  --format curl)

eval "$EVAL_CMD"
```

*Expected HTTP Response (200 OK):*
```json
{
  "balances": [
    {
      "asset": "USD",
      "available": "...",
      "total": "..."
    }
  ]
}
```

### Step 3: Test Harmless Positions Query (`GET /v1/portfolio/positions`)
```bash
EVAL_CMD=$(/Users/pavelcherkashin/ChitAkasha-Wolfram/venv/bin/python \
  ~/workspace/passive-income/tools/polymarket-us/signer.py \
  --keychain \
  --sign \
  --method GET \
  --path /v1/portfolio/positions \
  --format curl)

eval "$EVAL_CMD"
```

---

## 4. Troubleshooting & Error Responses

| Response / Error | Cause | Resolution |
|---|---|---|
| `HTTP 401 Unauthorized` | Invalid signature or expired key | Check Key ID and verify clock skew (`--check-clock`). |
| `HTTP 400 Bad Request` | Malformed headers or path | Ensure `path` starts with `/` and method matches (`GET`). |
| `ClockSkewError` | System clock is $> \pm 30\text{s}$ off | Synchronize macOS clock: `sudo sntp -sS time.apple.com`. |
| `ConfigurationError` | Missing env vars or Keychain entry | Re-run Section 2 to populate Keychain or environment. |
