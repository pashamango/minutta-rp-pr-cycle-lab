"""Dependency-free synthetic canonical mandate and capability session."""
from dataclasses import dataclass
from enum import Enum
import hashlib, json

class SessionState(str, Enum):
    LOCKED="LOCKED"; ACTIVE="ACTIVE"; REAUTH_REQUIRED="REAUTH_REQUIRED"; REVOKED="REVOKED"

@dataclass(frozen=True)
class SyntheticState:
    boot_id:str; capabilityd_digest:str; policy_digest:str; machine_identity:str; tailnet_identity:str; session_epoch:int=1
    @property
    def digest(self): return hashlib.sha256(json.dumps(self.__dict__,sort_keys=True,separators=(",",":")).encode()).hexdigest()

@dataclass(frozen=True)
class MandatePayload:
    principal:str; device_id:str; state_digest:str; policy_digest:str; allowed_classes:frozenset; session_epoch:int; issued_at:int; expires_at:int
    def canonical_bytes(self):
        return json.dumps({"principal":self.principal,"device_id":self.device_id,"state_digest":self.state_digest,"policy_digest":self.policy_digest,"allowed_classes":sorted(self.allowed_classes),"session_epoch":self.session_epoch,"issued_at":self.issued_at,"expires_at":self.expires_at},sort_keys=True,separators=(",",":")).encode()
    @property
    def digest(self): return hashlib.sha256(self.canonical_bytes()).hexdigest()

@dataclass(frozen=True)
class MandateLease:
    payload:MandatePayload
    @property
    def mandate_digest(self): return self.payload.digest
    @property
    def device_id(self): return self.payload.device_id
    @property
    def policy_digest(self): return self.payload.policy_digest
    @property
    def allowed_classes(self): return self.payload.allowed_classes
    @property
    def parent_expires_at(self): return self.payload.expires_at

@dataclass(frozen=True)
class ApprovalProof: nonce:str; mandate_digest:str
Approval=ApprovalProof
@dataclass(frozen=True)
class TaskLeaseRequest: task_id:str; source_sha256:str; execution_lease:str; capability_class:str; requested_expires_at:int
@dataclass(frozen=True)
class IssuedTaskCapability: task_id:str; source_sha256:str; execution_lease:str; capability_class:str; session_epoch:int; expires_at:int; parent_expires_at:int

class FakeApprovalVerifier:
    def __init__(self, approvals=()): self.approvals=set(approvals)
    def verify(self,proof):
        key=(proof.nonce,proof.mandate_digest)
        if key not in self.approvals:return False
        self.approvals.remove(key);return True

class CapabilitySession:
    def __init__(self,state,verifier): self.state=self.bound_state=state;self.verifier=verifier;self.state_name=SessionState.LOCKED;self.revoked=False;self._caps={};self._last_epoch=0
    def authorize(self,proof,mandate,now):
        p=mandate.payload
        if (self.revoked or self.state!=self.bound_state or proof.mandate_digest!=p.digest or p.state_digest!=self.state.digest or p.device_id!=self.state.machine_identity or p.policy_digest!=self.state.policy_digest or p.session_epoch!=self.bound_state.session_epoch or (self.state_name==SessionState.REAUTH_REQUIRED and p.session_epoch<=self._last_epoch) or now<p.issued_at or now>=p.expires_at or not self.verifier.verify(proof)): return False
        self.state_name=SessionState.ACTIVE;self.mandate=mandate;self._last_epoch=p.session_epoch;return True
    def issue(self,request,now):
        if self.state_name!=SessionState.ACTIVE or self.revoked or now>=self.mandate.parent_expires_at or request.capability_class not in self.mandate.allowed_classes or request.requested_expires_at>self.mandate.parent_expires_at or request.requested_expires_at<=now:return None
        cap=IssuedTaskCapability(request.task_id,request.source_sha256,request.execution_lease,request.capability_class,self.bound_state.session_epoch,request.requested_expires_at,self.mandate.parent_expires_at);self._caps[id(cap)]=cap;return cap
    def execute(self,capability,*,task_id,source_sha256,execution_lease,capability_class,now):
        return self.state_name==SessionState.ACTIVE and not self.revoked and self._caps.get(id(capability)) is capability and now<capability.expires_at and now<capability.parent_expires_at and (capability.task_id,capability.source_sha256,capability.execution_lease,capability.capability_class,capability.session_epoch)==(task_id,source_sha256,execution_lease,capability_class,self.bound_state.session_epoch)
    def revoke(self): self.revoked=True;self.state_name=SessionState.REVOKED;self._caps.clear()
    def observe(self,state):
        if self.revoked:return
        if state!=self.state:self.bound_state=state;self.state_name=SessionState.REAUTH_REQUIRED;self._caps.clear()
        self.state=state
__all__=["Approval","ApprovalProof","CapabilitySession","FakeApprovalVerifier","IssuedTaskCapability","MandateLease","MandatePayload","SessionState","SyntheticState","TaskLeaseRequest"]
