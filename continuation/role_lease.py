"""Fail-closed role continuation with atomic JSON checkpoints.

This is a pure local primitive. It does not claim child completion: only a
caller supplied reporter settlement may move a child to ``settled``.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


class LeaseError(ValueError):
    """Raised when a role or child binding is not admissible."""


def _time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise LeaseError("timestamps must include timezone")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class CommanderLease:
    principal: str
    scope: str
    mandate_digest: str
    created_at: str
    deadline: str
    budget: int | None = None
    revoked: bool = False


@dataclass(frozen=True)
class OutcomeCheckpoint:
    task_id: str
    source_digest: str
    lease_id: str
    state: str
    sequence: int


class CommanderStore:
    """Persist one role, child claims, and monotonic settlement checkpoints."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def _read(self) -> dict:
        if not self.path.exists():
            return {"role": None, "children": {}, "checkpoints": {}}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, value: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=self.path.name + ".", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(value, handle, sort_keys=True, separators=(",", ":"))
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(name, self.path)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def create_role(self, role: CommanderLease) -> None:
        data = self._read()
        if data["role"] is not None:
            raise LeaseError("role already exists")
        if _time(role.deadline) <= _time(role.created_at):
            raise LeaseError("deadline must follow creation")
        data["role"] = asdict(role)
        self._write(data)

    def revoke(self) -> None:
        data = self._read()
        if data["role"] is None:
            raise LeaseError("missing role")
        data["role"]["revoked"] = True
        self._write(data)

    def resume(self, principal: str, scope: str, mandate_digest: str, now: str) -> CommanderLease:
        data = self._read()
        raw = data["role"]
        if raw is None:
            raise LeaseError("missing role")
        role = CommanderLease(**raw)
        if role.revoked:
            raise LeaseError("role revoked")
        if _time(now) >= _time(role.deadline):
            raise LeaseError("role expired")
        if (principal, scope, mandate_digest) != (role.principal, role.scope, role.mandate_digest):
            raise LeaseError("role binding mismatch")
        return role

    def start_child(self, task_id: str, source_digest: str, lease_id: str,
                    principal: str, scope: str, mandate_digest: str, now: str) -> None:
        self.resume(principal, scope, mandate_digest, now)
        data = self._read()
        if task_id in data["children"]:
            raise LeaseError("child already exists")
        data["children"][task_id] = {"source_digest": source_digest, "lease_id": lease_id,
                                       "state": "claimed"}
        data["checkpoints"][task_id] = asdict(OutcomeCheckpoint(
            task_id, source_digest, lease_id, "claimed", 0))
        self._write(data)

    def settle_child(self, task_id: str, source_digest: str, lease_id: str) -> None:
        data = self._read()
        child = data["children"].get(task_id)
        if child is None or (child["source_digest"], child["lease_id"]) != (source_digest, lease_id):
            raise LeaseError("child binding mismatch")
        checkpoint = data["checkpoints"][task_id]
        if checkpoint["state"] == "settled":
            return
        if checkpoint["state"] != "claimed":
            raise LeaseError("non-monotonic child transition")
        checkpoint.update(state="settled", sequence=checkpoint["sequence"] + 1)
        child["state"] = "settled"
        self._write(data)

    def resumable_children(self) -> list[str]:
        data = self._read()
        return sorted(task for task, child in data["children"].items() if child["state"] != "settled")

