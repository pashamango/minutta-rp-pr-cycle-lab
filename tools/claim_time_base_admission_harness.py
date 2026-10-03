"""Deterministic model of claim-time launch-base admission."""

from dataclasses import dataclass


class AdmissionError(ValueError):
    pass


@dataclass(frozen=True)
class Admission:
    task_id: str
    source_sha256: str
    lease_id: str
    claim_time_base_sha: str


def admit(admission, *, task_id, source_sha256, lease_id, remote_main, known_heads,
          task_ref=None, trace=None):
    trace = trace if trace is not None else []
    trace.append("CLAIMED")
    trace.append(f"CAPTURE_BASE:{admission.claim_time_base_sha}")
    if (task_id, source_sha256, lease_id) != (admission.task_id, admission.source_sha256,
                                               admission.lease_id):
        trace.append("REJECT:BOUND_MISMATCH")
        raise AdmissionError("immutable binding mismatch")
    if task_ref is not None and (task_ref not in known_heads or task_ref != admission.claim_time_base_sha):
        trace.append("REJECT:TASK_REF_CONFLICT")
        raise AdmissionError("task ref conflict")
    if admission.claim_time_base_sha not in known_heads:
        trace.append("REJECT:INACCESSIBLE_BASE")
        raise AdmissionError("launch base inaccessible")
    if remote_main != admission.claim_time_base_sha:
        trace.append(f"REMOTE_MAIN_DESCENDANT:{remote_main}")
    trace.append(f"PUBLISH_BOUND_REF:{admission.claim_time_base_sha}")
    trace.append("REMOTE_VERIFY:PASS")
    trace.append("ADMISSION:SUCCESS")
    return admission.claim_time_base_sha
