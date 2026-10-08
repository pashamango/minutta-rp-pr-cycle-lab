# CAPABILITY-SESSION-SYNTHETIC-0001 result

```yaml
protocol: CAPABILITY_SESSION_RESULT/v1
task_id: CAPABILITY-SESSION-SYNTHETIC-0001
source_sha256: 6150629a1ea3444e3f8a5bb8199c50ef5fc3ef9fbda4bf00ab103a306b1bcf86
lease_id: db25e32643674d78ba12efab0538003a
continuity_sha: 0657f1ded22ece746bc648a4abc6a942eb6815b5
implementation_sha: df65e3d
completion_asserted: false
verdict: SYNTHETIC_SESSION_CORE_READY / PRODUCTION_CUSTODY_ABSENT
```

## Evidence

Exact command: `python3 -m unittest tests.test_capability_session -v`

Observed: 4 tests, 0 failures. The tests cover the unchanged positive path,
exact task/source/lease/class/epoch scope, expiry, explicit revocation, boot
ID, capabilityd digest, policy digest, machine identity, tailnet identity,
scope expansion, stale nonce, replay, and unchanged injected state for
sleep/wake and Python replacement.

`python3 -m unittest discover -v` reports 0 tests because this repository's
test directories are not package-recursive; it is not used as a success signal.

## Limitations

This is an offline injected-state model with a fake approval verifier. It has
no machine identity custody, cryptographic issuer, Keychain/Secure Enclave,
passkey, daemon, protected-resource probe, reboot observer, or production
completion oracle. The result is therefore synthetic readiness only.
