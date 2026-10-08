"""Immutable values used by the Maintainer Agent policy core."""

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Tuple


class RiskClass(IntEnum):
    R0 = 0
    R1 = 1
    R2 = 2
    R3 = 3


class AuditVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INDETERMINATE = "INDETERMINATE"


class CaseState(str, Enum):
    OBSERVED = "OBSERVED"
    SNAPSHOTTED = "SNAPSHOTTED"
    AUDITING = "AUDITING"
    PASS = "PASS"
    FAIL = "FAIL"
    INDETERMINATE = "INDETERMINATE"
    ELIGIBLE = "ELIGIBLE"
    SUBMITTED = "SUBMITTED"
    ENQUEUED = "ENQUEUED"
    MERGED = "MERGED"
    MERGE_FAILED = "MERGE_FAILED"
    VERIFIED = "VERIFIED"


class OperationState(str, Enum):
    PENDING = "PENDING"
    MERGED = "MERGED"
    ENQUEUED = "ENQUEUED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"


class ArtifactState(str, Enum):
    UNMERGED = "UNMERGED"
    MERGED = "MERGED"
    CONFLICTED = "CONFLICTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class PullRequestSnapshot:
    repository: str
    pr_number: int
    base_branch: str
    head_sha: str
    base_sha: str
    policy_root: str
    author_identity: str
    changed_paths: Tuple[str, ...]


@dataclass(frozen=True)
class AuditReceipt:
    auditor_identity: str
    verdict: AuditVerdict
    repository: str
    pr_number: int
    head_sha: str
    base_sha: str
    policy_root: str
    deterministic_checks_complete: bool
    semantic_checks_complete: bool
    unresolved_objections: Tuple[str, ...] = ()


@dataclass(frozen=True)
class MergeObservation:
    operation_state: OperationState
    artifact_state: ArtifactState
    merge_oid: str | None
    observed_pr_head_sha: str
    observed_base_head_sha: str
