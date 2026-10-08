"""Pure authority evaluator. This module performs no network or merge action."""

from dataclasses import dataclass
from fnmatch import fnmatch
from typing import Mapping, Sequence, Tuple

from .model import (
    ArtifactState,
    AuditReceipt,
    AuditVerdict,
    CaseState,
    MergeObservation,
    OperationState,
    PullRequestSnapshot,
    RiskClass,
)


@dataclass(frozen=True)
class Decision:
    eligible: bool
    risk_class: RiskClass
    reasons: Tuple[str, ...]


_ALLOWED_TRANSITIONS = {
    CaseState.OBSERVED: {CaseState.SNAPSHOTTED},
    CaseState.SNAPSHOTTED: {CaseState.AUDITING},
    CaseState.AUDITING: {CaseState.PASS, CaseState.FAIL, CaseState.INDETERMINATE},
    CaseState.PASS: {CaseState.ELIGIBLE, CaseState.SNAPSHOTTED},
    CaseState.FAIL: {CaseState.SNAPSHOTTED},
    CaseState.INDETERMINATE: {CaseState.SNAPSHOTTED},
    CaseState.ELIGIBLE: {CaseState.SUBMITTED, CaseState.SNAPSHOTTED},
    CaseState.SUBMITTED: {
        CaseState.ENQUEUED,
        CaseState.MERGED,
        CaseState.MERGE_FAILED,
    },
    CaseState.ENQUEUED: {CaseState.MERGED, CaseState.MERGE_FAILED},
    CaseState.MERGED: {CaseState.VERIFIED},
    CaseState.MERGE_FAILED: {CaseState.SNAPSHOTTED},
    CaseState.VERIFIED: set(),
}


def transition(current: CaseState, target: CaseState) -> CaseState:
    if target not in _ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"invalid transition: {current.value} -> {target.value}")
    return target


def _matches_any(path: str, patterns: Sequence[str]) -> bool:
    return any(fnmatch(path, pattern) for pattern in patterns)


def classify_risk(policy: Mapping[str, object], paths: Sequence[str]) -> RiskClass:
    protected = tuple(policy.get("protected_paths", ()))
    if any(_matches_any(path, protected) for path in paths):
        return RiskClass.R3

    risk = RiskClass.R0
    for rule in policy.get("risk_rules", ()):  # type: ignore[assignment]
        pattern = str(rule["pattern"])
        if any(fnmatch(path, pattern) for path in paths):
            risk = max(risk, RiskClass[str(rule["risk_class"])])
    return risk


def evaluate_merge_authority(
    policy: Mapping[str, object],
    snapshot: PullRequestSnapshot,
    receipt: AuditReceipt,
    *,
    current_head_sha: str,
    current_base_sha: str,
    current_policy_root: str,
    required_checks_pass: bool,
    unresolved_threads: int,
    merge_identity: str,
) -> Decision:
    """Return authority only when every independent proof remains current."""
    reasons = []
    risk = classify_risk(policy, snapshot.changed_paths)
    ceiling = RiskClass[str(policy.get("autonomous_ceiling", "R0"))]

    if not policy.get("enabled", False):
        reasons.append("POLICY_DISABLED")
    if snapshot.repository != policy.get("repository"):
        reasons.append("REPOSITORY_OUT_OF_SCOPE")
    if snapshot.base_branch not in policy.get("base_branches", ()):
        reasons.append("BRANCH_OUT_OF_SCOPE")
    if receipt.repository != snapshot.repository or receipt.pr_number != snapshot.pr_number:
        reasons.append("RECEIPT_SUBJECT_MISMATCH")
    if receipt.verdict is not AuditVerdict.PASS:
        reasons.append("AUDIT_NOT_PASS")
    if not receipt.deterministic_checks_complete:
        reasons.append("DETERMINISTIC_EVIDENCE_INCOMPLETE")
    if not receipt.semantic_checks_complete:
        reasons.append("SEMANTIC_EVIDENCE_INCOMPLETE")
    if receipt.unresolved_objections:
        reasons.append("UNRESOLVED_OBJECTIONS")
    if snapshot.author_identity == receipt.auditor_identity:
        reasons.append("SELF_REVIEW")
    if merge_identity in {snapshot.author_identity, receipt.auditor_identity}:
        reasons.append("IDENTITY_SEPARATION_VIOLATION")
    if receipt.head_sha != snapshot.head_sha or current_head_sha != snapshot.head_sha:
        reasons.append("HEAD_SHA_DRIFT")
    if receipt.base_sha != snapshot.base_sha or current_base_sha != snapshot.base_sha:
        reasons.append("BASE_SHA_DRIFT")
    if receipt.policy_root != snapshot.policy_root or current_policy_root != snapshot.policy_root:
        reasons.append("POLICY_ROOT_DRIFT")
    if not required_checks_pass:
        reasons.append("REQUIRED_CHECKS_NOT_PASS")
    if unresolved_threads != 0:
        reasons.append("UNRESOLVED_THREADS")
    if risk is RiskClass.R3:
        reasons.append("CONSTITUTIONAL_FIREWALL")
    elif risk > ceiling:
        reasons.append("AUTONOMOUS_CEILING_EXCEEDED")

    return Decision(not reasons, risk, tuple(reasons))


def merge_is_verified(snapshot: PullRequestSnapshot, observation: MergeObservation) -> bool:
    """Queue admission and operation success are insufficient without artifact readback."""
    return (
        observation.operation_state is OperationState.MERGED
        and observation.artifact_state is ArtifactState.MERGED
        and bool(observation.merge_oid)
        and observation.observed_pr_head_sha == snapshot.head_sha
        and bool(observation.observed_base_head_sha)
    )
