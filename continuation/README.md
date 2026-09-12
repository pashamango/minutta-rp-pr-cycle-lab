# Persistent commander lease prototype

This isolated prototype stores a role lease separately from child leases and
atomically persists monotonic child checkpoints. Resume revalidates principal,
scope, mandate digest, deadline, and revocation. Child settlement is explicit
and idempotent; process exit and Prometheus observations are not settlement.

The tests are synthetic state-machine tests only. They do not exercise the
installed mailbox, a real scheduler, GitHub, or production runtime.
