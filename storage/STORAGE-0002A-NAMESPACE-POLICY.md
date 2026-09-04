# ChitAkasha new-write namespace policy

The local cutover epoch is stored privately at
`~/ChitAkasha-Storage/migrations/new-write-cutover-v1.json`. From that epoch,
ChitAkasha-controlled task work and generated artifacts default to
`~/ChitAkasha-Storage/workspaces/`; mutable Git checkouts belong under
`workspaces/git/` and are not CAS objects. Existing `~/Documents` data remains
an untouched old-data migration source.

Future reconciliation is conflict preserving: import an old-only item; retain a
new-only item; deduplicate equal path/hash pairs; and preserve both versions plus
an explicit conflict record for equal paths with different hashes. Neither
lineage silently overwrites the other.

Completed non-Git artifacts may be explicitly published with:

```sh
python3 storage/tools/cas.py --namespace "$HOME/ChitAkasha-Storage" publish \
  --name task-artifacts --ref tasks/example /bounded/artifact/path
```

The helper verifies objects and the immutable manifest/root before atomically
updating the named mutable ref. It does not auto-ingest Git worktrees.
