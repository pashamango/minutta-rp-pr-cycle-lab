"""Publish task evidence before allowing independent reporter settlement.

This module deliberately does not classify a task.  It only makes execution
evidence durable and addressable; a reporter remains the settlement authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Iterable


class PublicationError(ValueError):
    pass


@dataclass(frozen=True)
class ReporterDecision:
    status: str
    publication_identity: str


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


class EvidencePublisher:
    """A deterministic, restart-safe publisher rooted at a Git worktree."""

    def __init__(self, worktree: Path, evidence_root: str = "evidence/published"):
        self.worktree = Path(worktree)
        self.root = self.worktree / evidence_root

    def publish(self, *, task_id: str, source_digest: str, lease_id: str,
                artifacts: Iterable[dict], checks: Iterable[dict],
                outcome_ref: str, fail: bool = False) -> dict:
        self._validate_binding(task_id, source_digest, lease_id)
        task_root = self.root / task_id
        if task_root.exists():
            other_leases = [p.name for p in task_root.iterdir() if p.is_dir() and p.name != lease_id]
            if other_leases:
                raise PublicationError("task already bound to a different lease")
        manifest = {
            "protocol": "evidence-publication/v1",
            "task_id": task_id,
            "source_digest": source_digest,
            "lease_id": lease_id,
            "artifact_refs": self._refs(artifacts),
            "check_refs": self._refs(checks),
            "outcome_ref": outcome_ref,
        }
        encoded = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode()
        identity = _sha256_bytes(encoded)
        directory = self.root / task_id / lease_id
        path = directory / "manifest.json"
        journal = directory / "publication.json"
        directory.mkdir(parents=True, exist_ok=True)
        if fail:
            record = {"protocol": "evidence-publication/v1", "status": "publication_failed",
                      "task_id": task_id, "source_digest": source_digest, "lease_id": lease_id,
                      "error": "synthetic publication failure; retryable"}
            journal.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
            raise PublicationError("publication_failed: retryable")
        if path.exists() and path.read_bytes() != encoded:
            raise PublicationError("publication identity collision")
        path.write_bytes(encoded)
        blob = subprocess.run(["git", "hash-object", str(path)], cwd=self.worktree,
                              check=True, capture_output=True, text=True).stdout.strip()
        record = {"protocol": "evidence-publication/v1", "status": "EVIDENCE_PUBLISHED",
                  **manifest, "artifact_manifest_sha256": identity,
                  "published_git_blob": blob, "publication_identity": identity}
        journal.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        return record

    def resume(self, task_id: str, lease_id: str) -> dict:
        path = self.root / task_id / lease_id / "publication.json"
        if not path.exists():
            raise PublicationError("no durable publication state")
        record = json.loads(path.read_text())
        if record.get("status") != "EVIDENCE_PUBLISHED":
            raise PublicationError("publication is not complete; retry publication")
        return record

    @staticmethod
    def settle(publication: dict, status: str) -> ReporterDecision:
        if status not in {"completed", "blocked"}:
            raise PublicationError("reporter must independently choose completed or blocked")
        return ReporterDecision(status, publication["publication_identity"])

    @staticmethod
    def _validate_binding(task_id: str, source_digest: str, lease_id: str) -> None:
        if not task_id or len(source_digest) != 64 or any(c not in "0123456789abcdef" for c in source_digest):
            raise PublicationError("invalid task/source binding")
        if len(lease_id) != 32 or any(c not in "0123456789abcdef" for c in lease_id):
            raise PublicationError("invalid lease binding")

    @staticmethod
    def _refs(values: Iterable[dict]) -> list[dict]:
        result = []
        for value in values:
            if not isinstance(value, dict) or set(value) != {"type", "ref"}:
                raise PublicationError("invalid evidence reference")
            ref = value["ref"]
            if not isinstance(ref, str) or not ref or ref.startswith("/") or ".." in Path(ref).parts:
                raise PublicationError("unsafe evidence reference")
            result.append({"type": value["type"], "ref": ref})
        return result
