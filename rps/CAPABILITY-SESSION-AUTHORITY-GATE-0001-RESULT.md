# Capability session authority gate result

- protocol: `CAPABILITY_SESSION_AUTHORITY_GATE_RESULT/v1`
- verdict: `SYNTHETIC_AUTHORITY_GATE_READY / CRYPTOGRAPHIC_AND_PRODUCTION_CUSTODY_ABSENT`
- continuity commit: `ef32b8be4d807a9dc6128e659b4d62c9a110c81e`
- implementation commit: `1f222be4a6c26ddc8841de40ddfc13f030f00028`
- predecessor: issue `226`; independent review: `5193572926`
- completion asserted: `false` for cryptographic or production custody

The synthetic gate now keeps observation separate from authority issuance. `observe()` cannot activate a locked or reauthentication-required session; drift requires a fresh, verifier-consumed approval bound to state digest, scope, nonce, epoch, and expiry. Capabilities are checked against task/source/lease/class/epoch and cannot outlive the parent session. Expiry, revocation, scope mismatch, replay, cross-state, stale-epoch, and restored-old-observation cases fail closed. Sleep/wake and Python/venv replacement are non-triggers while state remains unchanged.

Observed commands and counts:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_capability_session -v`: `8 passed`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: `125 passed`
- `git diff --check`: run before publication

Limitations: this remains dependency-free synthetic code. It does not provide real WebAuthn/passkey, Keychain/Secure Enclave, code-signing, MDM, capabilityd, or production credential custody. No completion oracle, dispatcher change, protected-resource probe, merge, or main push was performed.
