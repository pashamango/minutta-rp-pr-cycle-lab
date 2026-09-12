# PERSISTENT-COMMANDER-LEASE-0003

Predecessor: `1e17cdc92c82bede219bd92372279dfbd7662900`.

This successor binds settlement to a durable `chitakasha-reporter-validation/v1`
record emitted only after the real reporter completes its existing admission,
fresh-source, outcome, and receipt path. Commander ingestion validates the
canonical record digest and reporter module digest, then atomically advances
`OUTCOME_CANDIDATE` to settled. Public callers cannot perform the reporter
transition, and persisted role lease IDs are checked on restart.

Validation: `python3 -m unittest discover -s tests -v` — 31 tests, 31 passed,
0 failed, 0 errors; exit 0.

Trust boundary: repository-level software provenance is tested. This is not
cryptographic resistance to a malicious process with equivalent filesystem or
account authority. The checkpoint root and reporter module are explicit
configuration inputs; signing/capability isolation is not implemented.

Rollback is the single successor commit/branch; remove or revert that commit
after preserving the prior head. No production runtime, active role lease,
external service, or expired mandate was changed. The validation record is the
minimal Evidence Recognition entry distinguishing `Spend -> Evidence` from
`Spend -> NO_RESULT`; dashboard implementation is out of scope.
