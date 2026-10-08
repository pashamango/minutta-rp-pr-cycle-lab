"""Small, deterministic Prometheus BLOCKER_ANALYSIS/v1 adapter."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class BlockerAnalysis:
    type: str
    task_id: str
    source_digest: str
    lease_id: str
    semantic_objective: str
    last_verified_good_transition: str
    first_failed_or_missing_transition: str
    existing_artifacts: List[str]
    existing_evidence: List[str]
    blocker_class: str
    semantic_work_status: str
    retry_safety: str
    minimum_missing: Dict[str, str]
    next_safe_continuation: str
    requires_pasha: bool
    confidence: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def auth_required(*, task_id: str, source_digest: str, lease_id: str) -> Dict[str, Any]:
    """Diagnose a clean process ending at an external-auth boundary."""
    return BlockerAnalysis(
        type="BLOCKER_ANALYSIS/v1", task_id=task_id, source_digest=source_digest,
        lease_id=lease_id, semantic_objective="run one bounded public synthetic inference",
        last_verified_good_transition="founder_charter -> runner_submit(local_lane)",
        first_failed_or_missing_transition="runner_submit(external_lane) -> provider_call",
        existing_artifacts=["project-office/fixtures/vimana-pilot.json", "sovereign_worker/runner.py"],
        existing_evidence=["local runner deterministic tests pass", "Gemini adapter report: AUTH_REQUIRED"],
        blocker_class="authority", semantic_work_status="partial", retry_safety="continuation_only",
        minimum_missing={"capability": "", "authority": "human-authorized Gemini credential", "dependency": "", "representation": ""},
        next_safe_continuation="continue local Gemma lane; after credential installation run one sanitized public probe",
        requires_pasha=True, confidence="high",
    ).to_dict()
