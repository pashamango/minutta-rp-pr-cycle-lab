"""Durable lease-bound continuation checkpoints; semantic settlement stays local."""
from __future__ import annotations
import json, os, tempfile, hashlib
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

class LeaseError(ValueError): pass
def _time(v):
    d=datetime.fromisoformat(v.replace("Z","+00:00"))
    if d.tzinfo is None: raise LeaseError("timestamps must include timezone")
    return d.astimezone(timezone.utc)
@dataclass(frozen=True)
class CommanderLease:
    principal:str; scope:str; mandate_digest:str; created_at:str; deadline:str; budget:int|None=None; revoked:bool=False
@dataclass(frozen=True)
class ReporterCheckpoint:
    task_id:str; source_digest:str; child_lease_id:str; commander_role_lease_id:str; outcome_digest:str; reporter_authority:str; reporter_version:str; state:str="REPORTER_VALIDATED"
    @classmethod
    def from_record(cls, record, module_sha256, role_id):
        required={"protocol","task_id","source_sha256","child_lease_id","issue_number","outcome_status","outcome_sha256","terminal_receipt_state","receipt_key","evidence_validation","reporter_authority","reporter_version","reporter_module_sha256","created_at","remote_state","record_sha256"}
        if set(record)!=required or record.get("protocol")!="chitakasha-reporter-validation/v1": raise LeaseError("invalid reporter validation record")
        unsigned=dict(record); actual=unsigned.pop("record_sha256")
        expected="sha256:"+hashlib.sha256(json.dumps(unsigned,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        if actual!=expected or record["reporter_module_sha256"]!=module_sha256 or not record["reporter_authority"] or not record["reporter_version"]: raise LeaseError("invalid reporter provenance")
        return cls(record["task_id"],record["source_sha256"],record["child_lease_id"],role_id,record["outcome_sha256"],record["reporter_authority"],record["reporter_version"])
class CommanderStore:
    transitions=("CLAIMED","EXECUTION_CHECKPOINT","OUTCOME_CANDIDATE")
    def __init__(self,path:Path,role_lease_id="commander-role"): self.path=Path(path); self.role_lease_id=role_lease_id
    def _read(self):
        if not self.path.exists(): return {"role":None,"children":{},"checkpoints":{},"reservations":0}
        try:
            d=json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(d,dict) or not isinstance(d.get("children",{}),dict): raise ValueError
            return d
        except Exception as e: raise LeaseError("corrupt or truncated state") from e
    def _write(self,d):
        self.path.parent.mkdir(parents=True,exist_ok=True); fd,n=tempfile.mkstemp(prefix=self.path.name+".",dir=self.path.parent)
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as h: json.dump(d,h,sort_keys=True,separators=(",",":")); h.write("\n"); h.flush(); os.fsync(h.fileno())
            os.replace(n,self.path)
            try: fd=os.open(self.path.parent,os.O_RDONLY); os.fsync(fd); os.close(fd)
            except OSError: pass
        finally:
            if os.path.exists(n): os.unlink(n)
    def create_role(self,role):
        d=self._read()
        if d["role"] is not None: raise LeaseError("role already exists")
        if _time(role.deadline)<=_time(role.created_at): raise LeaseError("deadline must follow creation")
        d["role"]={**asdict(role),"role_lease_id":self.role_lease_id}; self._write(d)
    def _resume(self,p,s,m,now):
        d=self._read(); raw=d.get("role")
        if raw is None: raise LeaseError("missing role")
        role=CommanderLease(**{k:raw[k] for k in ("principal","scope","mandate_digest","created_at","deadline","budget","revoked")})
        if role.revoked: raise LeaseError("role revoked")
        if raw.get("role_lease_id") != self.role_lease_id: raise LeaseError("role lease ID drift")
        if _time(now)>=_time(role.deadline): raise LeaseError("role expired")
        if (p,s,m)!=(role.principal,role.scope,role.mandate_digest): raise LeaseError("role binding mismatch")
        return role
    def resume(self,*a): return self._resume(*a)
    def revoke(self):
        d=self._read()
        if not d.get("role"): raise LeaseError("missing role")
        d["role"]["revoked"]=True; self._write(d)
    def start_child(self,task_id,source_digest,lease_id,principal,scope,mandate_digest,now):
        role=self._resume(principal,scope,mandate_digest,now); d=self._read()
        if task_id in d["children"]: raise LeaseError("child already exists")
        if role.budget is not None and d.get("reservations",0)>=role.budget: raise LeaseError("budget exhausted")
        d["reservations"]=d.get("reservations",0)+1; d["children"][task_id]={"source_digest":source_digest,"lease_id":lease_id,"state":"CLAIMED","sequence":0}; self._write(d)
    def advance(self,task_id,state,principal,scope,mandate_digest,now):
        self._resume(principal,scope,mandate_digest,now); d=self._read(); c=d["children"].get(task_id)
        if not c or state not in self.transitions or self.transitions.index(state)!=c["sequence"]+1: raise LeaseError("non-monotonic child transition")
        c["state"]=state; c["sequence"]+=1; self._write(d)
    def accept_reporter_checkpoint(self,checkpoint,principal,scope,mandate_digest,now):
        self._resume(principal,scope,mandate_digest,now); d=self._read(); c=d["children"].get(checkpoint.task_id)
        if not c or (c["source_digest"],c["lease_id"])!=(checkpoint.source_digest,checkpoint.child_lease_id): raise LeaseError("checkpoint binding mismatch")
        if checkpoint.commander_role_lease_id!=self.role_lease_id or not checkpoint.reporter_authority or not checkpoint.reporter_version or checkpoint.state!="REPORTER_VALIDATED": raise LeaseError("untrusted reporter checkpoint")
        if len(checkpoint.outcome_digest)!=64: raise LeaseError("invalid outcome digest")
        if c["state"]=="SETTLED":
            if d["checkpoints"].get(checkpoint.task_id)!=asdict(checkpoint): raise LeaseError("conflicting replay")
            return "already_settled"
        if c["state"]!="OUTCOME_CANDIDATE": raise LeaseError("settlement before validation")
        d["checkpoints"][checkpoint.task_id]=asdict(checkpoint); c["state"]="SETTLED"; c["sequence"]+=1; self._write(d); return "settled"
    def consume_validation_record(self, path, reporter_module, principal, scope, mandate_digest, now):
        """Read only the explicitly supplied checkpoint and settle atomically."""
        try: record=json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception as exc: raise LeaseError("corrupt or truncated validation record") from exc
        checkpoint=ReporterCheckpoint.from_record(record, hashlib.sha256(Path(reporter_module).read_bytes()).hexdigest(), self.role_lease_id)
        return self.accept_reporter_checkpoint(checkpoint, principal, scope, mandate_digest, now)
    def settle_child(self,*a,**k): raise LeaseError("bare settlement disabled; submit reporter checkpoint")
    def resumable_children(self): return sorted(k for k,v in self._read()["children"].items() if v["state"]!="SETTLED")
