"""Dependency-free synthetic Sovereign Capability Session kernel."""
from dataclasses import dataclass
from enum import Enum


class SessionState(str, Enum):
    LOCKED = "LOCKED"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    REAUTH_REQUIRED = "REAUTH_REQUIRED"
    REVOKED = "REVOKED"


@dataclass(frozen=True)
class SyntheticState:
    boot_id: str
    capabilityd_digest: str
    policy_digest: str
    machine_identity: str
    tailnet_identity: str
    session_epoch: int = 1


@dataclass(frozen=True)
class Approval:
    nonce: str
    task_id: str
    lease_id: str
    session_epoch: int
    capability_class: str = "read"


@dataclass(frozen=True)
class TaskLease:
    task_id: str
    source_sha256: str
    lease_id: str
    capability_class: str
    session_epoch: int
    expires_at: int


class FakeApprovalVerifier:
    def __init__(self, approvals=()):
        self.approvals = set(approvals)

    def verify(self, approval):
        key = (approval.nonce, approval.task_id, approval.lease_id, approval.session_epoch)
        if key not in self.approvals:
            return False
        self.approvals.remove(key)
        return True


class CapabilitySession:
    def __init__(self, state, verifier):
        self.state = state
        self.bound_state = state
        self.verifier = verifier
        self.state_name = SessionState.LOCKED
        self.revoked = False

    def authorize(self, approval, lease, now):
        if self.revoked:
            self.state_name = SessionState.REVOKED
            return False
        if not self._same_authority() or lease.session_epoch != self.bound_state.session_epoch:
            self.state_name = SessionState.REAUTH_REQUIRED
            return False
        if (now >= lease.expires_at or approval.task_id != lease.task_id or
                approval.lease_id != lease.lease_id or
                approval.capability_class != lease.capability_class):
            self.state_name = SessionState.DEGRADED
            return False
        if not self.verifier.verify(approval):
            self.state_name = SessionState.DEGRADED
            return False
        self.state_name = SessionState.ACTIVE
        return True

    def execute(self, capability, *, task_id, source_sha256, lease_id, capability_class, now):
        if self.state_name != SessionState.ACTIVE or self.revoked:
            return False
        return (now < capability.expires_at and
                (capability.task_id, capability.source_sha256, capability.lease_id,
                 capability.capability_class, capability.session_epoch) ==
                (task_id, source_sha256, lease_id, capability_class, self.bound_state.session_epoch))

    def revoke(self):
        self.revoked = True
        self.state_name = SessionState.REVOKED

    def observe(self, state):
        if self.revoked:
            return
        if state.boot_id != self.bound_state.boot_id or state.capabilityd_digest != self.bound_state.capabilityd_digest:
            self.state_name = SessionState.REAUTH_REQUIRED
        elif state.policy_digest != self.bound_state.policy_digest or state.machine_identity != self.bound_state.machine_identity or state.tailnet_identity != self.bound_state.tailnet_identity:
            self.state_name = SessionState.REAUTH_REQUIRED
        else:
            self.state_name = SessionState.ACTIVE
        self.state = state

    def _same_authority(self):
        return self.state == self.bound_state


__all__ = ["Approval", "CapabilitySession", "FakeApprovalVerifier", "SessionState", "SyntheticState", "TaskLease"]
