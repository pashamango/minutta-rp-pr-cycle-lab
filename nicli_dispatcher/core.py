"""Deterministic Linear dispatcher, SQLite transactional leases, and isolated worker harness.

Implements the MIN-72 / MIN-74 (NICLI-B) control-plane specification using only
the Python standard library and synthetic/injected transports:
- Zero model calls when the queue is empty, paused, or blocked by admission/quota.
- Initial WIP = 1 across the dispatcher store.
- Durable SQLite transactional leases with monotonic fencing generations and
  explicit predecessor stop/isolation gating before replacement after crash/expiry.
- Boundary rechecks for mid-flight Human-Hold veto and task spec revision changes.
- Strict free-tier quota and explicit CLI/model pinning (no auto fallback or billing).
- Strict credential separation between dispatcher (Linear read/report), worker
  (no Linear/publisher secrets), and scoped branch publisher (no protected-main writes).
- Append-only NICLI_RUN_RECEIPT/v1 provenance receipts where END != DONE and
  builder cannot self-certify DONE without durable artifacts, passing acceptance
  tests, and an independent GPT/Muse reviewer PASS receipt.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime as dt
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
from typing import Any, Callable, Iterable, Protocol

UTC = dt.timezone.utc
NICLI_JOB_SCHEMA = "NICLI_JOB/v1"
NICLI_RECEIPT_SCHEMA = "NICLI_RUN_RECEIPT/v1"
PROTECTED_BRANCHES = frozenset({"main", "master", "release", "production"})
ALLOWED_REVIEWER_ROLES = frozenset({"GPT", "Muse"})
ALLOWED_AUTH_LANES = {
    "api_key": "ai-studio-free-tier",
    "antigravity_google_ai_pro": "antigravity-google-ai-pro",
}
VETO_LABELS = frozenset({"Human-Hold", "VETO: Human-Hold", "Icebox"})
VETO_STATUSES = frozenset({"Icebox", "Canceled", "Duplicate"})
CONFLICT_ROLE_LABELS = frozenset({"Role: Architect-Needed"})
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SAFE_BRANCH_RE = re.compile(r"^(?:minutta|agent/[a-z0-9_-]+)/[A-Za-z0-9._-]+$")


class DispatcherError(RuntimeError):
    """Structured control-plane error with a machine-checkable code."""

    def __init__(self, code: str, message: str = ""):
        super().__init__(message or code)
        self.code = code


def _iso_utc(value: str) -> dt.datetime:
    if not isinstance(value, str) or not value:
        raise DispatcherError("INVALID_TIMESTAMP", "timestamp required")
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise DispatcherError("INVALID_TIMESTAMP", "timezone required")
    return parsed.astimezone(UTC)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise DispatcherError("UNSAFE_ARTIFACT_PATH", str(path))
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class LinearIssueSnapshot:
    issue_id: str
    uuid: str
    team_key: str
    status: str
    title: str
    description: str
    labels: tuple[str, ...]
    updated_at: str
    parent_id: str | None = None
    parent_status: str | None = None
    parent_labels: tuple[str, ...] = ()
    ic_decision_ref: str | None = None
    handoff_refs: tuple[str, ...] = ()
    blocked_by: tuple[dict[str, str], ...] = ()
    source_repo: str | None = None
    source_commit: str | None = None
    allowed_paths: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    acceptance_commands: tuple[str, ...] = ()
    git_branch_name: str | None = None


@dataclass(frozen=True)
class AdmissionDecision:
    admitted: bool
    issue_id: str
    task_revision_hash: str
    blocker_code: str | None = None
    detail: str | None = None


@dataclass(frozen=True)
class QuotaState:
    bucket: str
    status: str  # "AVAILABLE", "UNKNOWN", "EXHAUSTED"
    remaining_requests: int | None
    free_only: bool = True
    billing_enabled: bool = False
    overage_billing_enabled: bool = False
    auto_model_upgrade: bool = False
    subscription_tier: str | None = None


@dataclass(frozen=True)
class HostResourceState:
    host_id: str
    disk_free_bytes: int
    rss_Headroom_bytes: int
    memory_pressure: bool = False


@dataclass(frozen=True)
class DispatcherConfig:
    host_id: str
    explicit_model: str
    cli_version: str
    auth_mode: str = "api_key"
    quota_bucket: str = "ai-studio-free-tier"
    allow_auto_model_upgrade: bool = False
    reviewer_role: str = "GPT"
    max_wip: int = 1
    poll_interval_s: int = 60
    lease_ttl_s: int = 960
    wall_timeout_s: int = 900
    max_turns: int = 12
    max_attempts: int = 1
    min_disk_free_bytes: int = 2 * 1024 * 1024 * 1024
    max_rss_bytes: int = 4 * 1024 * 1024 * 1024
    cpu_limit_cores: int = 2
    dispatcher_credential_handle: str = "keychain://mindrock/linear-dispatcher-readonly"
    publisher_credential_handle: str = "keychain://mindrock/git-scoped-publisher"
    worker_credential_handle: str = "keychain://mindrock/gemini-worker-api-key"

    def validate(self) -> None:
        if self.max_wip != 1:
            raise DispatcherError("INVALID_WIP_CONFIG", "initial pilot requires max_wip == 1")
        if self.auth_mode not in ALLOWED_AUTH_LANES:
            raise DispatcherError(
                "UNSUPPORTED_AUTH_MODE",
                "worker requires explicit api_key or antigravity_google_ai_pro auth_mode",
            )
        if self.quota_bucket != ALLOWED_AUTH_LANES[self.auth_mode]:
            raise DispatcherError(
                "QUOTA_BUCKET_MISMATCH",
                f"auth_mode {self.auth_mode} must use quota_bucket {ALLOWED_AUTH_LANES[self.auth_mode]}",
            )
        if self.allow_auto_model_upgrade:
            raise DispatcherError("AUTO_MODEL_UPGRADE_FORBIDDEN", "automatic model upgrades are forbidden")
        if not self.explicit_model or not self.cli_version:
            raise DispatcherError("UNPINNED_MODEL_OR_CLI", "explicit_model and cli_version required")
        if self.reviewer_role not in ALLOWED_REVIEWER_ROLES:
            raise DispatcherError("INVALID_REVIEWER_ROLE", "reviewer_role must be GPT or Muse")
        handles = {
            self.dispatcher_credential_handle,
            self.publisher_credential_handle,
            self.worker_credential_handle,
        }
        if len(handles) != 3:
            raise DispatcherError("CREDENTIAL_SEPARATION_VIOLATION", "dispatcher, worker, and publisher handles must be distinct")


@dataclass(frozen=True)
class NicliJob:
    schema: str
    issue_id: str
    parent_id: str
    ic_decision_ref: str
    handoff_refs: tuple[str, ...]
    task_revision_hash: str
    source_repo: str
    source_commit: str
    workspace: str
    allowed_paths: tuple[str, ...]
    capabilities: tuple[str, ...]
    acceptance_commands: tuple[str, ...]
    artifact_destination: str
    reviewer_role: str
    explicit_model: str
    cli_version: str
    auth_mode: str
    quota_bucket: str
    wall_timeout_s: int
    max_turns: int
    disk_limit_bytes: int
    rss_limit_bytes: int
    cpu_limit_cores: int
    attempt_id: str
    lease_generation: int

    def to_worker_manifest(self) -> dict[str, Any]:
        """Return untrusted-workspace-safe job payload without Linear/publisher credentials."""
        payload = asdict(self)
        for key in list(payload):
            if isinstance(payload[key], tuple):
                payload[key] = list(payload[key])
        return payload


@dataclass(frozen=True)
class LeaseRecord:
    issue_id: str
    task_revision_hash: str
    attempt_id: str
    lease_generation: int
    state: str  # "ACTIVE", "RELEASED", "COMPLETED", "FAILED", "FENCED"
    claimed_at: str
    heartbeat_at: str
    expires_at: str
    worker_stopped_isolated: bool


@dataclass(frozen=True)
class WorkerOutcome:
    exit_code: int
    models_observed: tuple[str, ...]
    turns_used: int
    timed_out: bool = False
    http_status: int | None = None
    retry_after_s: int | None = None
    disk_full: bool = False
    tool_receipts: tuple[dict[str, Any], ...] = ()
    artifact_paths: tuple[str, ...] = ()
    tests_run_and_results: tuple[dict[str, str], ...] = ()
    usage_observed_or_unknown: dict[str, Any] | str = "UNKNOWN"
    host_resource_peak: dict[str, int] = field(default_factory=lambda: {"rss_bytes": 0, "disk_bytes": 0})


@dataclass(frozen=True)
class ReviewerReceipt:
    receipt_id: str
    reviewer_role: str
    issue_id: str
    attempt_id: str
    lease_generation: int
    task_revision_hash: str
    artifact_manifest_sha256: str
    verdict: str  # "PASS", "REWORK", "BLOCKED"
    checks_rerun: bool
    reviewed_at: str


@dataclass(frozen=True)
class NicliRunReceipt:
    schema: str
    issue_id: str
    host_id: str
    attempt_id: str
    lease_generation: int
    source_commit: str
    task_revision_hash: str
    cli_version: str
    model_requested: str
    models_observed: tuple[str, ...]
    auth_mode: str
    started_at: str
    ended_at: str
    exit_code: int | None
    termination_reason: str
    tool_receipts: tuple[dict[str, Any], ...]
    artifact_refs_and_sha256: dict[str, str]
    tests_run_and_results: tuple[dict[str, str], ...]
    usage_observed_or_unknown: dict[str, Any] | str
    host_resource_peak: dict[str, int]
    END: bool
    DONE: bool
    blocker: str | None
    reviewer_receipt_ref: str | None
    retry_backoff_s: int | None = None
    review_branch: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["models_observed"] = list(self.models_observed)
        data["tool_receipts"] = list(self.tool_receipts)
        data["tests_run_and_results"] = list(self.tests_run_and_results)
        return data


class LinearReadTransport(Protocol):
    def list_candidate_issues(self, cursor: str | None = None, limit: int = 50) -> tuple[list[LinearIssueSnapshot], str | None]: ...
    def get_issue(self, issue_id: str) -> LinearIssueSnapshot: ...


class WorkerHarness(Protocol):
    def run(self, job: NicliJob, worker_credential_handle: str) -> WorkerOutcome: ...


def compute_task_revision_hash(snapshot: LinearIssueSnapshot) -> str:
    payload = {
        "issue_id": snapshot.issue_id,
        "uuid": snapshot.uuid,
        "team_key": snapshot.team_key,
        "status": snapshot.status,
        "title": snapshot.title,
        "description": snapshot.description,
        "labels": sorted(snapshot.labels),
        "parent_id": snapshot.parent_id,
        "parent_labels": sorted(snapshot.parent_labels),
        "ic_decision_ref": snapshot.ic_decision_ref,
        "handoff_refs": list(snapshot.handoff_refs),
        "source_repo": snapshot.source_repo,
        "source_commit": snapshot.source_commit,
        "allowed_paths": list(snapshot.allowed_paths),
        "capabilities": sorted(snapshot.capabilities),
        "acceptance_commands": list(snapshot.acceptance_commands),
    }
    return _sha256_text(_canonical_json(payload))


def evaluate_admission(snapshot: LinearIssueSnapshot) -> AdmissionDecision:
    rev_hash = compute_task_revision_hash(snapshot)
    if not SAFE_ID_RE.fullmatch(snapshot.issue_id):
        return AdmissionDecision(False, snapshot.issue_id, rev_hash, "INVALID_ISSUE_ID", "unsafe issue identifier")
    if snapshot.team_key not in {"MIN", "Mindrock"}:
        return AdmissionDecision(False, snapshot.issue_id, rev_hash, "WRONG_TEAM", snapshot.team_key)
    if snapshot.status in VETO_STATUSES or VETO_LABELS.intersection(snapshot.labels) or VETO_LABELS.intersection(snapshot.parent_labels):
        return AdmissionDecision(False, snapshot.issue_id, rev_hash, "VETO_OR_HOLD", "issue or parent has veto/hold state")
    if snapshot.status != "Todo":
        return AdmissionDecision(False, snapshot.issue_id, rev_hash, "NOT_TODO_STATUS", snapshot.status)
    if "Role: Builder-Ready" not in snapshot.labels:
        return AdmissionDecision(False, snapshot.issue_id, rev_hash, "MISSING_BUILDER_READY", "Role: Builder-Ready label required")
    if CONFLICT_ROLE_LABELS.intersection(snapshot.labels) or CONFLICT_ROLE_LABELS.intersection(snapshot.parent_labels):
        return AdmissionDecision(
            False,
            snapshot.issue_id,
            rev_hash,
            "CONFLICTING_ROLE_STATE",
            "Architect-Needed label present on task or parent",
        )
    if not snapshot.parent_id or "Role: PM-Watch" not in snapshot.parent_labels:
        return AdmissionDecision(False, snapshot.issue_id, rev_hash, "MISSING_PARENT_PM_WATCH", "parent must carry Role: PM-Watch")
    if not snapshot.ic_decision_ref or not snapshot.handoff_refs:
        return AdmissionDecision(False, snapshot.issue_id, rev_hash, "MISSING_IC_OR_R4_HANDOFF", "parent IC decision and R4 handoff required")
    for blocker in snapshot.blocked_by:
        if blocker.get("status") != "Done":
            return AdmissionDecision(
                False,
                snapshot.issue_id,
                rev_hash,
                "UNMET_DEPENDENCY",
                f"blocked by {blocker.get('id', 'unknown')} ({blocker.get('status', 'unstarted')})",
            )
    if not snapshot.source_repo or not snapshot.source_commit or not snapshot.acceptance_commands:
        return AdmissionDecision(
            False,
            snapshot.issue_id,
            rev_hash,
            "MISSING_REPOSITORY_OR_ACCEPTANCE",
            "source_repo, source_commit, and acceptance_commands are mandatory",
        )
    return AdmissionDecision(True, snapshot.issue_id, rev_hash)


class LeaseStore:
    """SQLite transactional lease store with monotonic fencing and crash isolation gates."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.execute("PRAGMA journal_mode=WAL")
            con.execute(
                """CREATE TABLE IF NOT EXISTS control (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )"""
            )
            con.execute(
                """CREATE TABLE IF NOT EXISTS leases (
                    issue_id TEXT PRIMARY KEY,
                    task_revision_hash TEXT NOT NULL,
                    attempt_id TEXT NOT NULL,
                    lease_generation INTEGER NOT NULL,
                    state TEXT NOT NULL,
                    claimed_at TEXT NOT NULL,
                    heartbeat_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    worker_stopped_isolated INTEGER NOT NULL DEFAULT 0,
                    attempts_count INTEGER NOT NULL DEFAULT 1
                )"""
            )
            con.execute(
                """CREATE TABLE IF NOT EXISTS receipts (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_id TEXT NOT NULL,
                    attempt_id TEXT NOT NULL,
                    lease_generation INTEGER NOT NULL,
                    receipt_json TEXT NOT NULL,
                    receipt_sha256 TEXT NOT NULL UNIQUE
                )"""
            )
            con.execute("INSERT OR IGNORE INTO control(key, value) VALUES('fencing_seq', '0')")
            con.execute("INSERT OR IGNORE INTO control(key, value) VALUES('paused', '0')")
            con.commit()
        try:
            os.chmod(self.db_path, 0o600)
        except OSError:
            pass

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(str(self.db_path), timeout=5.0, isolation_level=None)
        con.execute("PRAGMA busy_timeout=5000")
        return con

    def is_paused(self) -> bool:
        with self._connect() as con:
            row = con.execute("SELECT value FROM control WHERE key='paused'").fetchone()
            return bool(row and row[0] == "1")

    def set_paused(self, paused: bool) -> None:
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            con.execute("UPDATE control SET value=? WHERE key='paused'", ("1" if paused else "0",))
            con.commit()

    def get_lease(self, issue_id: str) -> LeaseRecord | None:
        with self._connect() as con:
            row = con.execute(
                """SELECT issue_id, task_revision_hash, attempt_id, lease_generation,
                          state, claimed_at, heartbeat_at, expires_at, worker_stopped_isolated
                   FROM leases WHERE issue_id=?""",
                (issue_id,),
            ).fetchone()
            if not row:
                return None
            return LeaseRecord(
                issue_id=row[0],
                task_revision_hash=row[1],
                attempt_id=row[2],
                lease_generation=int(row[3]),
                state=row[4],
                claimed_at=row[5],
                heartbeat_at=row[6],
                expires_at=row[7],
                worker_stopped_isolated=bool(row[8]),
            )

    def claim_lease(
        self,
        *,
        issue_id: str,
        task_revision_hash: str,
        attempt_id: str,
        now: str,
        ttl_s: int,
        max_wip: int = 1,
        max_attempts: int = 1,
    ) -> LeaseRecord:
        now_dt = _iso_utc(now)
        expires_iso = (now_dt + dt.timedelta(seconds=ttl_s)).isoformat().replace("+00:00", "Z")
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            try:
                existing = con.execute(
                    """SELECT task_revision_hash, attempt_id, lease_generation, state,
                              claimed_at, heartbeat_at, expires_at, worker_stopped_isolated, attempts_count
                       FROM leases WHERE issue_id=?""",
                    (issue_id,),
                ).fetchone()
                if existing:
                    ex_rev, ex_att, ex_gen, ex_state, _, _, ex_exp, ex_iso, ex_count = existing
                    if ex_state == "COMPLETED" and ex_rev == task_revision_hash:
                        raise DispatcherError("ALREADY_COMPLETED", f"{issue_id} already completed for this revision")
                    if ex_state == "ACTIVE":
                        if _iso_utc(ex_exp) > now_dt:
                            if ex_rev != task_revision_hash:
                                raise DispatcherError("SPEC_REVISION_CHANGED", "active lease holds older revision")
                            raise DispatcherError("ALREADY_CLAIMED", f"{issue_id} already has an active lease")
                        if not ex_iso:
                            raise DispatcherError(
                                "PREDECESSOR_NOT_ISOLATED",
                                "expired lease cannot be replaced before predecessor worker is stopped and isolated",
                            )
                    elif not ex_iso and ex_state not in {"RELEASED", "COMPLETED"}:
                        raise DispatcherError(
                            "PREDECESSOR_NOT_ISOLATED",
                            "prior failed/fenced attempt must be stopped and isolated before replacement",
                        )
                    if ex_rev == task_revision_hash and int(ex_count) >= max_attempts:
                        raise DispatcherError("MAX_ATTEMPTS_EXCEEDED", f"max_attempts={max_attempts} reached for revision")

                active_rows = con.execute(
                    "SELECT issue_id, expires_at, worker_stopped_isolated FROM leases WHERE state='ACTIVE' AND issue_id != ?",
                    (issue_id,),
                ).fetchall()
                for other_id, other_exp, other_iso in active_rows:
                    if _iso_utc(other_exp) > now_dt or not other_iso:
                        if len(active_rows) >= max_wip:
                            raise DispatcherError("WIP_LIMIT_REACHED", f"WIP={max_wip} occupied by {other_id}")

                seq_row = con.execute("SELECT value FROM control WHERE key='fencing_seq'").fetchone()
                next_gen = int(seq_row[0]) + 1
                con.execute("UPDATE control SET value=? WHERE key='fencing_seq'", (str(next_gen),))
                attempts_count = 1
                if existing and existing[0] == task_revision_hash:
                    attempts_count = int(existing[8]) + 1

                con.execute(
                    """INSERT INTO leases(
                        issue_id, task_revision_hash, attempt_id, lease_generation,
                        state, claimed_at, heartbeat_at, expires_at, worker_stopped_isolated, attempts_count
                    ) VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?, 0, ?)
                    ON CONFLICT(issue_id) DO UPDATE SET
                        task_revision_hash=excluded.task_revision_hash,
                        attempt_id=excluded.attempt_id,
                        lease_generation=excluded.lease_generation,
                        state='ACTIVE',
                        claimed_at=excluded.claimed_at,
                        heartbeat_at=excluded.heartbeat_at,
                        expires_at=excluded.expires_at,
                        worker_stopped_isolated=0,
                        attempts_count=excluded.attempts_count""",
                    (issue_id, task_revision_hash, attempt_id, next_gen, now, now, expires_iso, attempts_count),
                )
                con.commit()
                return LeaseRecord(
                    issue_id=issue_id,
                    task_revision_hash=task_revision_hash,
                    attempt_id=attempt_id,
                    lease_generation=next_gen,
                    state="ACTIVE",
                    claimed_at=now,
                    heartbeat_at=now,
                    expires_at=expires_iso,
                    worker_stopped_isolated=False,
                )
            except Exception:
                con.rollback()
                raise

    def verify_fencing(self, *, issue_id: str, attempt_id: str, lease_generation: int, now: str) -> LeaseRecord:
        now_dt = _iso_utc(now)
        lease = self.get_lease(issue_id)
        if lease is None:
            raise DispatcherError("LEASE_NOT_FOUND", issue_id)
        if lease.lease_generation != lease_generation or lease.attempt_id != attempt_id:
            raise DispatcherError(
                "STALE_FENCING_GENERATION",
                f"expected gen={lease.lease_generation}/attempt={lease.attempt_id}, got gen={lease_generation}/attempt={attempt_id}",
            )
        if lease.state != "ACTIVE":
            raise DispatcherError("LEASE_NOT_ACTIVE", f"lease state is {lease.state}")
        if _iso_utc(lease.expires_at) <= now_dt:
            raise DispatcherError("LEASE_EXPIRED", f"lease expired at {lease.expires_at}")
        return lease

    def heartbeat(self, *, issue_id: str, attempt_id: str, lease_generation: int, now: str, ttl_s: int) -> LeaseRecord:
        now_dt = _iso_utc(now)
        expires_iso = (now_dt + dt.timedelta(seconds=ttl_s)).isoformat().replace("+00:00", "Z")
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            try:
                row = con.execute(
                    "SELECT attempt_id, lease_generation, state, expires_at, task_revision_hash, claimed_at, worker_stopped_isolated FROM leases WHERE issue_id=?",
                    (issue_id,),
                ).fetchone()
                if not row:
                    raise DispatcherError("LEASE_NOT_FOUND", issue_id)
                if row[0] != attempt_id or int(row[1]) != lease_generation:
                    raise DispatcherError("STALE_FENCING_GENERATION", "heartbeat fencing mismatch")
                if row[2] != "ACTIVE" or _iso_utc(row[3]) <= now_dt:
                    raise DispatcherError("LEASE_EXPIRED", "cannot heartbeat expired or inactive lease")
                con.execute(
                    "UPDATE leases SET heartbeat_at=?, expires_at=? WHERE issue_id=? AND lease_generation=?",
                    (now, expires_iso, issue_id, lease_generation),
                )
                con.commit()
                return LeaseRecord(
                    issue_id=issue_id,
                    task_revision_hash=row[4],
                    attempt_id=attempt_id,
                    lease_generation=lease_generation,
                    state="ACTIVE",
                    claimed_at=row[5],
                    heartbeat_at=now,
                    expires_at=expires_iso,
                    worker_stopped_isolated=bool(row[6]),
                )
            except Exception:
                con.rollback()
                raise

    def confirm_worker_stopped_and_isolated(self, *, issue_id: str, lease_generation: int) -> None:
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            cur = con.execute(
                """UPDATE leases
                   SET worker_stopped_isolated=1,
                       state=CASE WHEN state='ACTIVE' THEN 'FENCED' ELSE state END
                   WHERE issue_id=? AND lease_generation=?""",
                (issue_id, lease_generation),
            )
            if cur.rowcount != 1:
                con.rollback()
                raise DispatcherError("STALE_FENCING_GENERATION", "cannot isolate unknown lease generation")
            con.commit()

    def transition_lease(self, *, issue_id: str, attempt_id: str, lease_generation: int, new_state: str, stopped_isolated: bool = True) -> None:
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT attempt_id, lease_generation FROM leases WHERE issue_id=?",
                (issue_id,),
            ).fetchone()
            if not row or row[0] != attempt_id or int(row[1]) != lease_generation:
                con.rollback()
                raise DispatcherError("STALE_FENCING_GENERATION", "lease transition rejected due to stale generation")
            con.execute(
                "UPDATE leases SET state=?, worker_stopped_isolated=? WHERE issue_id=? AND lease_generation=?",
                (new_state, 1 if stopped_isolated else 0, issue_id, lease_generation),
            )
            con.commit()

    def append_receipt(self, receipt: NicliRunReceipt) -> str:
        encoded = _canonical_json(receipt.to_dict())
        digest = _sha256_text(encoded)
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            con.execute(
                """INSERT INTO receipts(issue_id, attempt_id, lease_generation, receipt_json, receipt_sha256)
                   VALUES (?, ?, ?, ?, ?)""",
                (receipt.issue_id, receipt.attempt_id, receipt.lease_generation, encoded, digest),
            )
            con.commit()
        return digest

    def list_receipts(self, issue_id: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as con:
            if issue_id:
                rows = con.execute(
                    "SELECT receipt_json FROM receipts WHERE issue_id=? ORDER BY seq ASC",
                    (issue_id,),
                ).fetchall()
            else:
                rows = con.execute("SELECT receipt_json FROM receipts ORDER BY seq ASC").fetchall()
            return [json.loads(r[0]) for r in rows]


class ScopedPublisher:
    """Dedicated review-branch publisher separated from worker credentials."""

    def __init__(self, publisher_credential_handle: str):
        if not publisher_credential_handle:
            raise DispatcherError("MISSING_PUBLISHER_CREDENTIAL", "publisher handle required")
        self.credential_handle = publisher_credential_handle
        self.published_branches: list[dict[str, Any]] = []

    def publish_review_branch(
        self,
        *,
        lease: LeaseRecord,
        job: NicliJob,
        branch_name: str,
        workspace_dir: Path,
        artifact_rel_paths: Iterable[str],
    ) -> tuple[str, dict[str, str]]:
        if branch_name in PROTECTED_BRANCHES or not SAFE_BRANCH_RE.fullmatch(branch_name):
            raise DispatcherError("PROTECTED_OR_INVALID_BRANCH", f"refusing to publish branch '{branch_name}'")
        workspace_root = workspace_dir.expanduser().resolve()
        artifacts_hashed: dict[str, str] = {}
        for rel in artifact_rel_paths:
            if not rel or rel.startswith("/") or ".." in Path(rel).parts:
                raise DispatcherError("UNSAFE_ARTIFACT_PATH", rel)
            full_path = workspace_root / rel
            if not full_path.exists() or full_path.is_symlink() or not full_path.is_file():
                raise DispatcherError("MISSING_ARTIFACT", f"missing or unsafe artifact: {rel}")
            if workspace_root not in full_path.resolve().parents:
                raise DispatcherError("UNSAFE_ARTIFACT_PATH", f"artifact escapes workspace: {rel}")
            artifacts_hashed[rel] = _sha256_file(full_path)
        if not artifacts_hashed:
            raise DispatcherError("MISSING_ARTIFACT", "at least one durable artifact is required")
        record = {
            "issue_id": job.issue_id,
            "attempt_id": lease.attempt_id,
            "lease_generation": lease.lease_generation,
            "task_revision_hash": job.task_revision_hash,
            "branch": branch_name,
            "artifacts": artifacts_hashed,
            "credential_handle_used": self.credential_handle,
        }
        self.published_branches.append(record)
        return branch_name, artifacts_hashed


class NicliDispatcher:
    """Single lightweight deterministic Linear dispatcher with bounded worker harness."""

    def __init__(
        self,
        *,
        config: DispatcherConfig,
        store: LeaseStore,
        linear: LinearReadTransport,
        worker: WorkerHarness,
        publisher: ScopedPublisher,
        workspace_root: Path,
    ):
        config.validate()
        if publisher.credential_handle == config.worker_credential_handle:
            raise DispatcherError("CREDENTIAL_SEPARATION_VIOLATION", "publisher and worker cannot share credentials")
        self.config = config
        self.store = store
        self.linear = linear
        self.worker = worker
        self.publisher = publisher
        self.workspace_root = Path(workspace_root).expanduser().resolve()
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.model_invocations = 0

    def _paginated_candidates(self, max_pages: int = 10) -> list[LinearIssueSnapshot]:
        cursor: str | None = None
        results: list[LinearIssueSnapshot] = []
        for _ in range(max_pages):
            page, next_cursor = self.linear.list_candidate_issues(cursor=cursor, limit=50)
            results.extend(page)
            if not next_cursor:
                return results
            cursor = next_cursor
        raise DispatcherError("PAGINATION_LIMIT_EXCEEDED", "candidate queue exceeded bounded pagination")

    def _check_quota_and_host(self, quota: QuotaState, host: HostResourceState) -> None:
        if quota.auto_model_upgrade or self.config.allow_auto_model_upgrade:
            raise DispatcherError("AUTO_MODEL_UPGRADE_FORBIDDEN", "automatic model upgrades are forbidden")
        if quota.billing_enabled or quota.overage_billing_enabled:
            raise DispatcherError("BILLING_FORBIDDEN", "paid billing or paid overages are forbidden")
        if self.config.auth_mode == "api_key" and not quota.free_only:
            raise DispatcherError("BILLING_FORBIDDEN", "AI Studio API key worker requires free_only=True")
        if quota.bucket != self.config.quota_bucket:
            raise DispatcherError("QUOTA_BUCKET_MISMATCH", "quota state bucket does not match configured worker lane")
        if self.config.auth_mode == "antigravity_google_ai_pro" and quota.subscription_tier != "google_ai_pro":
            raise DispatcherError(
                "UNSUPPORTED_SUBSCRIPTION_TIER",
                "Antigravity worker requires explicit google_ai_pro subscription tier",
            )
        if quota.status == "UNKNOWN" or quota.remaining_requests is None:
            raise DispatcherError("QUOTA_UNKNOWN", "unknown remaining quota is UNKNOWN, not unlimited")
        if quota.status != "AVAILABLE" or quota.remaining_requests <= 0:
            raise DispatcherError("QUOTA_EXHAUSTED", "quota exhausted; stopping before worker launch")
        if host.memory_pressure or host.disk_free_bytes < self.config.min_disk_free_bytes:
            self.store.set_paused(True)
            raise DispatcherError("HOST_DISK_FULL_OR_PRESSURE", "host resource pressure; new worker paused")

    def _isolated_workspace(self, issue_id: str, attempt_id: str) -> Path:
        if not SAFE_ID_RE.fullmatch(issue_id) or not SAFE_ID_RE.fullmatch(attempt_id):
            raise DispatcherError("UNSAFE_WORKSPACE_PATH", "invalid issue_id or attempt_id")
        target = self.workspace_root / issue_id / attempt_id
        for parent in (*reversed(target.parents), target):
            if parent.exists() and parent.is_symlink():
                raise DispatcherError("UNSAFE_WORKSPACE_PATH", "symlink in workspace hierarchy")
        target.mkdir(parents=True, exist_ok=False, mode=0o700)
        return target

    def poll_and_dispatch(
        self,
        *,
        now: str,
        quota: QuotaState,
        host: HostResourceState,
        attempt_id_factory: Callable[[], str] | None = None,
    ) -> dict[str, Any]:
        """Run one deterministic poll cycle. Never invokes a model when queue is empty or gated."""
        if self.store.is_paused():
            return {"status": "PAUSED", "model_calls": 0}

        candidates = self._paginated_candidates()
        if not candidates:
            return {"status": "IDLE_EMPTY_QUEUE", "model_calls": 0}

        admitted_snapshot: LinearIssueSnapshot | None = None
        admission: AdmissionDecision | None = None
        rejections: dict[str, str] = {}
        for item in candidates:
            decision = evaluate_admission(item)
            if decision.admitted:
                admitted_snapshot = item
                admission = decision
                break
            rejections[item.issue_id] = decision.blocker_code or "REJECTED"

        if admitted_snapshot is None or admission is None:
            return {"status": "NO_ELIGIBLE_TASKS", "model_calls": 0, "rejections": rejections}

        # Check quota and host pressure only when a candidate is otherwise eligible, before claiming or calling model.
        self._check_quota_and_host(quota, host)

        # Boundary 1: Re-fetch live issue from Linear before claiming lease to detect mid-flight edits or veto.
        fresh_before_claim = self.linear.get_issue(admitted_snapshot.issue_id)
        fresh_decision = evaluate_admission(fresh_before_claim)
        if not fresh_decision.admitted:
            return {
                "status": "BLOCKED_AT_CLAIM_BOUNDARY",
                "issue_id": admitted_snapshot.issue_id,
                "blocker": fresh_decision.blocker_code,
                "model_calls": 0,
            }
        if fresh_decision.task_revision_hash != admission.task_revision_hash:
            return {
                "status": "BLOCKED_AT_CLAIM_BOUNDARY",
                "issue_id": admitted_snapshot.issue_id,
                "blocker": "SPEC_REVISION_CHANGED",
                "model_calls": 0,
            }

        attempt_id = (attempt_id_factory or (lambda: f"att-{os.urandom(6).hex()}"))()
        lease = self.store.claim_lease(
            issue_id=fresh_before_claim.issue_id,
            task_revision_hash=fresh_decision.task_revision_hash,
            attempt_id=attempt_id,
            now=now,
            ttl_s=self.config.lease_ttl_s,
            max_wip=self.config.max_wip,
            max_attempts=self.config.max_attempts,
        )

        work_dir = self._isolated_workspace(lease.issue_id, lease.attempt_id)
        job = NicliJob(
            schema=NICLI_JOB_SCHEMA,
            issue_id=fresh_before_claim.issue_id,
            parent_id=fresh_before_claim.parent_id or "",
            ic_decision_ref=fresh_before_claim.ic_decision_ref or "",
            handoff_refs=fresh_before_claim.handoff_refs,
            task_revision_hash=lease.task_revision_hash,
            source_repo=fresh_before_claim.source_repo or "",
            source_commit=fresh_before_claim.source_commit or "",
            workspace=str(work_dir),
            allowed_paths=fresh_before_claim.allowed_paths,
            capabilities=fresh_before_claim.capabilities,
            acceptance_commands=fresh_before_claim.acceptance_commands,
            artifact_destination=str(work_dir / "artifacts"),
            reviewer_role=self.config.reviewer_role,
            explicit_model=self.config.explicit_model,
            cli_version=self.config.cli_version,
            auth_mode=self.config.auth_mode,
            quota_bucket=self.config.quota_bucket,
            wall_timeout_s=self.config.wall_timeout_s,
            max_turns=self.config.max_turns,
            disk_limit_bytes=self.config.min_disk_free_bytes,
            rss_limit_bytes=self.config.max_rss_bytes,
            cpu_limit_cores=self.config.cpu_limit_cores,
            attempt_id=lease.attempt_id,
            lease_generation=lease.lease_generation,
        )
        (work_dir / "nicli-job.json").write_text(_canonical_json(job.to_worker_manifest()) + "\n", encoding="utf-8")

        self.model_invocations += 1
        try:
            outcome = self.worker.run(job, self.config.worker_credential_handle)
        except OSError as exc:
            if exc.errno == errno.ENOSPC:
                outcome = WorkerOutcome(
                    exit_code=1,
                    models_observed=(self.config.explicit_model,),
                    turns_used=1,
                    disk_full=True,
                )
            else:
                raise

        return self.settle_worker_outcome(
            job=job,
            outcome=outcome,
            started_at=now,
            ended_at=now,
            branch_name=fresh_before_claim.git_branch_name or f"minutta/{fresh_before_claim.issue_id.lower()}",
        )

    def settle_worker_outcome(
        self,
        *,
        job: NicliJob,
        outcome: WorkerOutcome,
        started_at: str,
        ended_at: str,
        branch_name: str,
    ) -> dict[str, Any]:
        """Verify fencing, boundary spec/veto, model receipts, tests, and artifacts; write NICLI_RUN_RECEIPT/v1."""
        lease = self.store.verify_fencing(
            issue_id=job.issue_id,
            attempt_id=job.attempt_id,
            lease_generation=job.lease_generation,
            now=ended_at,
        )

        termination_reason = "COMPLETED_AWAITING_QA"
        blocker: str | None = None
        backoff_s: int | None = None
        published_branch: str | None = None
        artifact_hashes: dict[str, str] = {}

        # Boundary 2: Recheck live Linear issue for mid-flight Human-Hold veto or spec revision change before publication.
        live_issue = self.linear.get_issue(job.issue_id)
        live_decision = evaluate_admission(live_issue)
        if not live_decision.admitted and live_decision.blocker_code == "VETO_OR_HOLD":
            termination_reason = "ABORTED_VETO_AT_BOUNDARY"
            blocker = "VETO_OR_HOLD"
        elif compute_task_revision_hash(live_issue) != job.task_revision_hash:
            termination_reason = "ABORTED_SPEC_CHANGED_AT_BOUNDARY"
            blocker = "SPEC_REVISION_CHANGED"
        elif outcome.disk_full:
            termination_reason = "FAILED_DISK_FULL"
            blocker = "HOST_DISK_FULL"
            self.store.set_paused(True)
        elif outcome.http_status in {401, 403}:
            termination_reason = f"FAILED_PROVIDER_AUTH_{outcome.http_status}"
            blocker = f"PROVIDER_HTTP_{outcome.http_status}"
            self.store.set_paused(True)
        elif outcome.http_status == 429:
            termination_reason = "FAILED_PROVIDER_RATE_LIMIT_429"
            blocker = "PROVIDER_HTTP_429"
            backoff_s = max(60, min(3600, int(outcome.retry_after_s or 60)))
        elif outcome.timed_out or outcome.turns_used > job.max_turns:
            termination_reason = "TIMED_OUT_OR_TURN_LIMIT"
            blocker = "ATTEMPT_BOUNDS_EXCEEDED"
        elif not outcome.models_observed or any(m != job.explicit_model for m in outcome.models_observed):
            termination_reason = "FAILED_UNAUTHORIZED_MODEL_OBSERVED"
            blocker = "MODEL_RECEIPT_MISMATCH"
        elif outcome.exit_code != 0:
            termination_reason = "WORKER_NONZERO_EXIT"
            blocker = f"EXIT_CODE_{outcome.exit_code}"
        else:
            # Exit code 0 is NOT sufficient: verify required acceptance tests and durable artifacts.
            if not outcome.tests_run_and_results or any(t.get("status") != "pass" for t in outcome.tests_run_and_results):
                termination_reason = "EXIT0_WITH_FAILED_OR_MISSING_TESTS"
                blocker = "TESTS_FAILED"
            else:
                try:
                    published_branch, artifact_hashes = self.publisher.publish_review_branch(
                        lease=lease,
                        job=job,
                        branch_name=branch_name,
                        workspace_dir=Path(job.workspace),
                        artifact_rel_paths=outcome.artifact_paths,
                    )
                except DispatcherError as exc:
                    termination_reason = f"ARTIFACT_PUBLICATION_FAILED:{exc.code}"
                    blocker = exc.code

        lease_state = "COMPLETED" if blocker is None else "FAILED"
        self.store.transition_lease(
            issue_id=job.issue_id,
            attempt_id=job.attempt_id,
            lease_generation=job.lease_generation,
            new_state=lease_state,
            stopped_isolated=True,
        )

        # Builder NEVER self-certifies DONE=True; independent reviewer receipt is required.
        receipt = NicliRunReceipt(
            schema=NICLI_RECEIPT_SCHEMA,
            issue_id=job.issue_id,
            host_id=self.config.host_id,
            attempt_id=job.attempt_id,
            lease_generation=job.lease_generation,
            source_commit=job.source_commit,
            task_revision_hash=job.task_revision_hash,
            cli_version=job.cli_version,
            model_requested=job.explicit_model,
            models_observed=outcome.models_observed,
            auth_mode=job.auth_mode,
            started_at=started_at,
            ended_at=ended_at,
            exit_code=outcome.exit_code,
            termination_reason=termination_reason,
            tool_receipts=outcome.tool_receipts,
            artifact_refs_and_sha256=artifact_hashes,
            tests_run_and_results=outcome.tests_run_and_results,
            usage_observed_or_unknown=outcome.usage_observed_or_unknown,
            host_resource_peak=outcome.host_resource_peak,
            END=True,
            DONE=False,
            blocker=blocker,
            reviewer_receipt_ref=None,
            retry_backoff_s=backoff_s,
            review_branch=published_branch,
        )
        receipt_sha = self.store.append_receipt(receipt)
        return {
            "status": termination_reason,
            "receipt_sha256": receipt_sha,
            "receipt": receipt.to_dict(),
            "linear_projection": "In Review + QA-Needed" if blocker is None else "Blocked",
        }

    def record_independent_qa(
        self,
        *,
        prior_receipt: NicliRunReceipt,
        review: ReviewerReceipt,
    ) -> NicliRunReceipt:
        """Apply an independent GPT/Muse reviewer receipt. Only PASS with verified artifacts sets DONE=True."""
        if review.reviewer_role not in ALLOWED_REVIEWER_ROLES:
            raise DispatcherError("INVALID_REVIEWER_ROLE", review.reviewer_role)
        if (
            review.issue_id != prior_receipt.issue_id
            or review.attempt_id != prior_receipt.attempt_id
            or review.lease_generation != prior_receipt.lease_generation
            or review.task_revision_hash != prior_receipt.task_revision_hash
        ):
            raise DispatcherError("REVIEWER_BINDING_MISMATCH", "reviewer receipt does not match run bindings")
        manifest_sha = _sha256_text(_canonical_json(prior_receipt.artifact_refs_and_sha256))
        if review.artifact_manifest_sha256 != manifest_sha:
            raise DispatcherError("REVIEWER_ARTIFACT_HASH_MISMATCH", "reviewer inspected different artifacts")
        if review.verdict not in {"PASS", "REWORK", "BLOCKED"}:
            raise DispatcherError("INVALID_REVIEW_VERDICT", review.verdict)

        is_done = (
            review.verdict == "PASS"
            and review.checks_rerun
            and prior_receipt.END
            and prior_receipt.blocker is None
            and bool(prior_receipt.artifact_refs_and_sha256)
            and bool(prior_receipt.tests_run_and_results)
            and all(t.get("status") == "pass" for t in prior_receipt.tests_run_and_results)
        )
        blocker = prior_receipt.blocker
        if review.verdict != "PASS":
            blocker = f"QA_{review.verdict}"

        final_receipt = NicliRunReceipt(
            schema=NICLI_RECEIPT_SCHEMA,
            issue_id=prior_receipt.issue_id,
            host_id=prior_receipt.host_id,
            attempt_id=prior_receipt.attempt_id,
            lease_generation=prior_receipt.lease_generation,
            source_commit=prior_receipt.source_commit,
            task_revision_hash=prior_receipt.task_revision_hash,
            cli_version=prior_receipt.cli_version,
            model_requested=prior_receipt.model_requested,
            models_observed=prior_receipt.models_observed,
            auth_mode=prior_receipt.auth_mode,
            started_at=prior_receipt.started_at,
            ended_at=review.reviewed_at,
            exit_code=prior_receipt.exit_code,
            termination_reason=f"QA_{review.verdict}",
            tool_receipts=prior_receipt.tool_receipts,
            artifact_refs_and_sha256=prior_receipt.artifact_refs_and_sha256,
            tests_run_and_results=prior_receipt.tests_run_and_results,
            usage_observed_or_unknown=prior_receipt.usage_observed_or_unknown,
            host_resource_peak=prior_receipt.host_resource_peak,
            END=True,
            DONE=is_done,
            blocker=None if is_done else blocker,
            reviewer_receipt_ref=review.receipt_id,
            retry_backoff_s=prior_receipt.retry_backoff_s,
            review_branch=prior_receipt.review_branch,
        )
        self.store.append_receipt(final_receipt)
        return final_receipt
