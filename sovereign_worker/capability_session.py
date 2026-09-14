"""Dependency-free synthetic session authority gate."""
from dataclasses import dataclass
from enum import Enum
import hashlib

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
    @property
    def digest(self):
        return hashlib.sha256("|".join((self.boot_id, self.capabilityd_digest, self.policy_digest, self.machine_identity, self.tailnet_identity)).encode()).hexdigest()

@dataclass(frozen=True)
class Approval:
    nonce: str
    task_id: str
    lease_id: str
    session_epoch: int
    capability_class: str = "read"
    state_digest: str = ""
    expires_at: int = 2**63 - 1

@dataclass(frozen=True)
class TaskLease:
    task_id: str
    source_sha256: str
    lease_id: str
    capability_class: str
    session_epoch: int
    expires_at: int
    parent_expires_at: int = 2**63 - 1

class FakeApprovalVerifier:
    def __init__(self, approvals=()): self.approvals = set(approvals)
    def verify(self, approval):
        full = (approval.nonce, approval.task_id, approval.lease_id, approval.session_epoch, approval.capability_class, approval.state_digest, approval.expires_at)
        legacy = (approval.nonce, approval.task_id, approval.lease_id, approval.session_epoch)
        key = full if full in self.approvals else legacy
        if key not in self.approvals: return False
        self.approvals.remove(key)
        return True

class CapabilitySession:
    def __init__(self, state, verifier):
        self.state = self.bound_state = state
        self.verifier = verifier
        self.state_name = SessionState.LOCKED
        self.revoked = False
        self._approval_required = True

    def authorize(self, approval, lease, now):
        if self.revoked:
            self.state_name = SessionState.REVOKED; return False
        if (self.state_name == SessionState.REAUTH_REQUIRED or self.state != self.bound_state or
                lease.session_epoch != self.bound_state.session_epoch or approval.session_epoch != self.bound_state.session_epoch):
            self.state_name = SessionState.REAUTH_REQUIRED; return False
        if (now >= lease.expires_at or now >= approval.expires_at or approval.task_id != lease.task_id or
                approval.lease_id != lease.lease_id or approval.capability_class != lease.capability_class or
                lease.expires_at > lease.parent_expires_at or (approval.state_digest and approval.state_digest != self.state.digest)):
            self.state_name = SessionState.DEGRADED; return False
        if not self.verifier.verify(approval):
            self.state_name = SessionState.DEGRADED; return False
        self.state_name = SessionState.ACTIVE; self._approval_required = False; return True

    def execute(self, capability, *, task_id, source_sha256, lease_id, capability_class, now):
        if self.state_name != SessionState.ACTIVE or self.revoked or self._approval_required: return False
        return (now < capability.expires_at and now < capability.parent_expires_at and
                (capability.task_id, capability.source_sha256, capability.lease_id, capability.capability_class, capability.session_epoch) ==
                (task_id, source_sha256, lease_id, capability_class, self.bound_state.session_epoch))

    def revoke(self): self.revoked = True; self.state_name = SessionState.REVOKED

    def observe(self, state):
        if self.revoked: return
        if state != self.state:
            self.bound_state = state; self.state_name = SessionState.REAUTH_REQUIRED; self._approval_required = True
        self.state = state

__all__ = ["Approval", "CapabilitySession", "FakeApprovalVerifier", "SessionState", "SyntheticState", "TaskLease"]
