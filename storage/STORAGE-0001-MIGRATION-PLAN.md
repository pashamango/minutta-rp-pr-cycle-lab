# STORAGE-0001 Migration Plan

No migration is authorized by STORAGE-0001 or STORAGE-0001-RECOVERY. A future separately approved migration must preserve this exact order:

1. source
2. staging copy
3. hash
4. verify
5. manifest/root
6. replicas
7. verify replicas
8. only then consider detaching old provider

Each source remains untouched through replica verification. Detachment is a distinct approval gate, never an automatic consequence of successful ingest. Failures leave the source authoritative and produce an auditable error without publishing a root that claims unverified data.
