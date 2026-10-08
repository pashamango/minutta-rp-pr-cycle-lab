"""Dependency-free synthetic typed authority chain."""
from dataclasses import dataclass
from enum import Enum
import hashlib

class SessionState(str, Enum):
    LOCKED="LOCKED"; ACTIVE="ACTIVE"; REAUTH_REQUIRED="REAUTH_REQUIRED"; REVOKED="REVOKED"
@dataclass(frozen=True)
class SyntheticState:
    boot_id:str; capabilityd_digest:str; policy_digest:str; machine_identity:str; tailnet_identity:str; session_epoch:int=1
    @property
    def digest(self): return hashlib.sha256("|".join((self.boot_id,self.capabilityd_digest,self.policy_digest,self.machine_identity,self.tailnet_identity)).encode()).hexdigest()
@dataclass(frozen=True)
class MandateLease: mandate_digest:str; device_id:str; policy_digest:str; allowed_classes:frozenset; parent_expires_at:int
@dataclass(frozen=True)
class Approval: nonce:str; mandate_digest:str; state_digest:str; device_id:str; policy_digest:str; allowed_classes:frozenset; session_epoch:int; expires_at:int
@dataclass(frozen=True)
class TaskLeaseRequest: task_id:str; source_sha256:str; execution_lease:str; capability_class:str; requested_expires_at:int
@dataclass(frozen=True)
class IssuedTaskCapability: task_id:str; source_sha256:str; execution_lease:str; capability_class:str; session_epoch:int; expires_at:int; parent_expires_at:int
class FakeApprovalVerifier:
    def __init__(self, approvals=()): self.approvals=set(approvals)
    def verify(self, approval):
        key=(approval.nonce,approval.mandate_digest,approval.state_digest,approval.device_id,approval.policy_digest,approval.allowed_classes,approval.session_epoch,approval.expires_at)
        if key not in self.approvals:return False
        self.approvals.remove(key);return True
class CapabilitySession:
    def __init__(self,state,verifier): self.state=self.bound_state=state;self.verifier=verifier;self.state_name=SessionState.LOCKED;self.revoked=False;self._caps={}
    def authorize(self,approval,mandate,now):
        if self.revoked:self.state_name=SessionState.REVOKED;return False
        if self.state!=self.bound_state:return False
        if (approval.state_digest!=self.state.digest or approval.mandate_digest!=mandate.mandate_digest or approval.device_id!=mandate.device_id or approval.policy_digest!=mandate.policy_digest or approval.allowed_classes!=mandate.allowed_classes or approval.session_epoch!=self.bound_state.session_epoch or now>=approval.expires_at or approval.expires_at>mandate.parent_expires_at or not self.verifier.verify(approval)):return False
        self.state_name=SessionState.ACTIVE;self.mandate=mandate;return True
    def issue(self,request,now):
        if self.state_name!=SessionState.ACTIVE or self.revoked or now>=self.mandate.parent_expires_at or request.capability_class not in self.mandate.allowed_classes or request.requested_expires_at>self.mandate.parent_expires_at:return None
        cap=IssuedTaskCapability(request.task_id,request.source_sha256,request.execution_lease,request.capability_class,self.bound_state.session_epoch,request.requested_expires_at,self.mandate.parent_expires_at);self._caps[id(cap)]=cap;return cap
    def execute(self,capability,*,task_id,source_sha256,execution_lease,capability_class,now):
        return self.state_name==SessionState.ACTIVE and not self.revoked and self._caps.get(id(capability)) is capability and now<capability.expires_at and now<capability.parent_expires_at and (capability.task_id,capability.source_sha256,capability.execution_lease,capability.capability_class,capability.session_epoch)==(task_id,source_sha256,execution_lease,capability_class,self.bound_state.session_epoch)
    def revoke(self):self.revoked=True;self.state_name=SessionState.REVOKED;self._caps.clear()
    def observe(self,state):
        if self.revoked:return
        if state!=self.state:self.bound_state=state;self.state_name=SessionState.REAUTH_REQUIRED;self._caps.clear()
        self.state=state
__all__=["Approval","CapabilitySession","FakeApprovalVerifier","IssuedTaskCapability","MandateLease","SessionState","SyntheticState","TaskLeaseRequest"]
