# STORAGE-0002C resumable Documents migration

The user LaunchAgent `com.chitakasha.documents-migration` runs one source-preserving worker. Private paths, errors, checkpoints, and manifests stay in `~/ChitAkasha-Storage/migrations/documents-0002/`; the repository contains no source inventory.

Sanitized status (counts only):

```sh
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
  ~/ChitAkasha-Storage/migrations/documents-0002/bin/documents_resumable.py \
  --state ~/ChitAkasha-Storage/migrations/documents-0002 status
```

Stop and restart gracefully:

```sh
launchctl kill SIGTERM gui/$(id -u)/com.chitakasha.documents-migration
launchctl kickstart gui/$(id -u)/com.chitakasha.documents-migration
```

The worker never writes under `~/Documents`. It uses a durable directory queue and verified file rows, an exclusive advisory lock, atomic/fsynced status replacement, SQLite FULL synchronous transactions, three attempts per unresolved entry, one-at-a-time I/O, and a 120-second per-file read alarm. A stopped run resumes pending work and skips verified files.

`phase=converging` is only a candidate boundary. Publication of a final root remains disabled in this acquisition worker; a subsequent bounded completion pass must perform dual-lineage reconciliation, deterministic regeneration, CAS audit, and reconstruction verification. This prevents the acquisition process from prematurely claiming a final Documents root.
