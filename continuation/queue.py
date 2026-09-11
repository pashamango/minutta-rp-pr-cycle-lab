from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


def _key(task_id: str, source_digest: str, lease_id: str) -> str:
    raw = f"{task_id}\n{source_digest}\n{lease_id}".encode()
    return hashlib.sha256(raw).hexdigest()


def enqueue(root: Path, *, task_id: str, source_digest: str, lease_id: str,
            run_dir: Path) -> Path:
    """Persist a replay request; duplicate bindings are harmless and idempotent."""
    if not all(isinstance(v, str) and v for v in (task_id, source_digest, lease_id)):
        raise ValueError("invalid continuation binding")
    path = Path(root) / (_key(task_id, source_digest, lease_id) + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"protocol": "chitakasha-continuation/v1", "task_id": task_id,
               "source_digest": source_digest, "lease_id": lease_id,
               "run_dir": str(run_dir), "status": "pending"}
    if path.exists():
        existing = json.loads(path.read_text())
        if {existing.get(k) for k in ("task_id", "source_digest", "lease_id")} != {task_id, source_digest, lease_id}:
            raise ValueError("continuation binding collision")
        return path
    tmp = path.with_suffix(f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(payload, sort_keys=True) + "\n")
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)
    return path


def pending(root: Path):
    return [json.loads(p.read_text()) for p in sorted(Path(root).glob("*.json"))
            if json.loads(p.read_text()).get("status") == "pending"]


def acknowledge(root: Path, task_id: str, source_digest: str, lease_id: str) -> Path:
    path = Path(root) / (_key(task_id, source_digest, lease_id) + ".json")
    value = json.loads(path.read_text())
    if any(value.get(k) != v for k, v in (("task_id", task_id), ("source_digest", source_digest), ("lease_id", lease_id))):
        raise ValueError("continuation binding mismatch")
    value["status"] = "acknowledged"
    path.write_text(json.dumps(value, sort_keys=True) + "\n")
    return path
