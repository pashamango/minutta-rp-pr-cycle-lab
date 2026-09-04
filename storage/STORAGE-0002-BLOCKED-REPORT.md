# STORAGE-0002 Blocked Report

STORAGE-0002 was stopped during bounded source discovery. No Documents source
entry was deleted, moved, renamed, overwritten, or evicted; no iCloud setting
was changed; no remote replica was created; and no mutable CAS ref was updated.

## Sanitized observations

- Logical source: `~/Documents`.
- The logical source is a directory on the local Data volume.
- Finder preferences report iCloud Desktop and Documents synchronization enabled.
- Free space at discovery time: 145,137,328,128 bytes.
- A 30-second metadata-only walk could not complete top-level enumeration and
  returned interrupted-system-call errors.
- A separately bounded 15-second `brctl status` request timed out.
- An authorized user-level `brctl download ~/Documents` request failed with
  `NSCocoaErrorDomain Code=257`: the directory could not be opened because the
  process did not have permission to view it.

No filenames, account identifiers, source contents, or private manifest data are
included in this report.

## Completeness status

```text
Documents source discovered: BLOCKED
complete enumeration: BLOCKED
regular files byte-materialized: NOT STARTED
unresolved regular files: UNKNOWN (enumeration unavailable)
CAS ingest: NOT STARTED
CAS digest verification: NOT STARTED
convergence/reconciliation: NOT STARTED
private manifest: NOT CREATED
root deterministic: NOT CREATED
recoverability verification: NOT STARTED
source modified/deleted: NO
final Documents root: NOT CREATED
```

Exact blocker: the executing mailbox process lacks permission to enumerate and
request hydration of the logical Documents tree. A future retry requires the
mailbox execution context to have macOS access to Documents (for example via an
explicit Privacy & Security approval) and a successful bounded top-level
enumeration before capacity can be assessed safely. This report does not request
or perform that approval.
