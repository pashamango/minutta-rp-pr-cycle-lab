# CLAIM_TIME_BASE_REGRESSION_RESULT/v1

- task_id: `CLAIM-TIME-BASE-ADMISSION-REGRESSION-0001`
- source_sha256: `796e7104dd00cf603411e1d6637906ee89d206954e163ba7fe7add4a25964a4d`
- lease_id: `7da6ff77e42c44099af8e7d440a9f083`
- claim_time_base_sha: `1b1f209fb34bf3f994f656bc5eea69fc55d1c6e8`
- continuity_sha: `3512ed6`
- implementation_sha: `32c121b8022c164b0ff1fae74b2e86a54dfb2137`
- final_sha: `c4d39997efa05753424eacf9a88459f987da809d`
- verdict: `EXTERNAL_PREFLIGHT_BOUNDARY_LOCALIZED`
- exact_reproduction_213_214: `not rerun; prior unpublished Darwin artifacts were not inspected or reconstructed`
- implementation_status: `no repository moving-main equality gate found`
- first_broken_transition: `EXTERNAL_PREFLIGHT_BOUNDARY`
- minimum_runtime_representation: `verified immutable claim-time base, remote descendant/ref ancestry, and bound task/source/lease admission receipt`
- privacy_boundary: `no secrets, credentials, Keychain, service, scheduler, or production runner access`
- rollback_boundary: `revert this branch/PR; main and protected PRs were not modified`

## Ordered deterministic trace

`CLAIMED -> CAPTURE_BASE:B -> REMOTE_MAIN_DESCENDANT:M -> PUBLISH_BOUND_REF:B -> REMOTE_VERIFY:PASS -> ADMISSION:SUCCESS`

The harness proves `B != M` and preserves the B-derived bound ref. Negative
controls reject binding mismatch, altered/unknown task refs, and inaccessible
bases. This is a repository-controlled model, not installed runtime settlement.
