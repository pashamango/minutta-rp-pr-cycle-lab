# STORAGE-0001 Architecture

Namespace: `~/ChitAkasha-Storage/`.

The namespace contains `objects/`, `manifests/`, `roots/`, `refs/`, `indexes/`, `cache/`, `staging/`, and `logs/`. Whole-file bytes are addressed as `objects/sha256/<first-two-hex>/<remaining-hex>`. SHA-256 is canonical content identity; provider paths and IDs belong only in replica metadata.

Manifests use canonical JSON (UTF-8, sorted keys, compact separators, one trailing newline), schema `chitakasha-manifest/v1`, and sorted logical paths. Roots use the same encoding, schema `chitakasha-root/v1`, a sorted manifest identity list, and nullable `previous_root`. Their SHA-256 digest is their identity, making root generation deterministic and optionally chainable.

Git repositories remain Git. A future manifest should identify them by repository identity plus commit/ref, never by flattening `.git` into CAS objects. `indexes/` and `cache/` are derived and rebuildable. `staging/` is temporary ingress; `refs/` are mutable convenience pointers and never identity. No signing key exists. A future signer may sign a root digest and store a detached signature beside replica metadata without changing the root object.

Whole-file objects are the initial policy. The blocked metadata inventory supplied no evidence that content-defined chunking is warranted.
