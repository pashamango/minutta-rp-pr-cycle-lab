"""Deterministic, lease-safe local market scheduler core.

The Forge adapter is intentionally injected: polling and dispatch are policy
decisions, while network credentials and runner APIs remain outside this core.
"""
from dataclasses import dataclass, replace
import json, sqlite3, time

@dataclass(frozen=True)
class Job:
    task_id: str; priority: str; host_class: str; source_digest: str; lease_id: str = ""; status: str = "ready"

@dataclass(frozen=True)
class Host:
    name: str; state: str; active_job: str = ""; last_seen: float = 0.0

class Scheduler:
    def __init__(self, db_path=":memory:", idle_threshold=300):
        self.db = sqlite3.connect(db_path); self.idle_threshold = idle_threshold
        self.db.execute("create table if not exists events (id integer primary key, kind text, payload text)")
        self.jobs = {}; self.hosts = {}
    def observe(self, hosts): self.hosts = {h.name: h for h in hosts}; return self.snapshot()
    def enqueue(self, job): self.jobs.setdefault(job.task_id, job)
    def _eligible(self, job, host):
        return job.status == "ready" and (job.host_class in (host.name, "either")) and not host.active_job
    def reconcile(self, now=None):
        now = time.time() if now is None else now; decisions=[]
        for name, host in sorted(self.hosts.items()):
            if host.state != "available" or host.active_job: continue
            if host.last_seen and now-host.last_seen > self.idle_threshold:
                self._event("idle", {"host": name, "age": now-host.last_seen})
            candidates = [j for j in self.jobs.values() if self._eligible(j, host)]
            candidates.sort(key=lambda j: ({"P0":0,"P1":1,"P2":2}.get(j.priority,9), j.task_id))
            if candidates:
                job=candidates[0]; lease=f"{job.task_id}:{name}:{job.source_digest[:12]}"
                self.jobs[job.task_id]=replace(job,status="leased",lease_id=lease)
                self.hosts[name]=replace(host,active_job=job.task_id)
                d={"host":name,"task_id":job.task_id,"lease_id":lease}; self._event("dispatch",d); decisions.append(d)
        return decisions
    def complete(self, host, task_id, status):
        job=self.jobs[task_id]; self.jobs[task_id]=replace(job,status=status)
        self.hosts[host]=replace(self.hosts[host],active_job=""); self._event("completion", {"host":host,"task_id":task_id,"status":status})
    def snapshot(self): return {"hosts":{n:h.__dict__ for n,h in self.hosts.items()},"queue":{n:j.__dict__ for n,j in self.jobs.items()}}
    def _event(self, kind, payload): self.db.execute("insert into events(kind,payload) values(?,?)",(kind,json.dumps(payload,sort_keys=True))); self.db.commit()
