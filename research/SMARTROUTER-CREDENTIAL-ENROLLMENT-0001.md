# SMARTROUTER-CREDENTIAL-ENROLLMENT-0001

## Result

`AUTH_REQUIRED_WITH_READY_CEREMONY`

The repository now binds the exact Gemini principal, project, key display name,
local handle, and policy; it explicitly rejects wrong identities and ambiguous
key metadata. With no authorized management credential available to this
bounded run, the SecurityManager deposit and live probe remain unperformed.

## Ceremony

Authenticate `pavel.cherkashin@vestor.in` with Google Cloud CLI OAuth, then rerun
the enrollment command. The default browser account `minutta@gmail.com` is not
acceptable. No key value is printed, logged, persisted, or returned.

## Validation and rollback

Run `python3 -m pytest -q tests/test_smart_router_enrollment.py`.
Rollback is deleting this task branch/PR; `origin/main` is unchanged.

## Limits

No live provider call, quota counter, Keychain write, key creation, billing, IAM,
or external publication was performed. A review PR is required before merge.
