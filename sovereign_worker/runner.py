from __future__ import annotations
import json, sqlite3, time, urllib.request
from dataclasses import dataclass
from pathlib import Path

PRIVATE_MARKERS = ("private", "secret", "password", "token", "credential", "api_key")
def classify_privacy(prompt, requested=None):
    value = requested or ("private" if any(x in prompt.lower() for x in PRIVATE_MARKERS) else "public")
    if value not in {"public", "private"} or (value == "public" and any(x in prompt.lower() for x in PRIVATE_MARKERS)):
        raise ValueError("ambiguous_privacy_class")
    return value

@dataclass
class Capability:
    provider: str; privacy_class: str; free_only: bool; model_class: str; budget_remaining: float | None; availability: str
    def as_dict(self): return self.__dict__.copy()

class Ollama:
    def __init__(self, url="http://127.0.0.1:11434", model="gemma4:latest", timeout=90): self.url, self.model, self.timeout = url.rstrip("/"), model, timeout
    def capability(self): return Capability("ollama", "private", False, "local", None, "configured")
    def infer(self, prompt):
        body = json.dumps({"model": self.model, "prompt": prompt, "stream": False, "think": False}).encode()
        req = urllib.request.Request(self.url + "/api/generate", body, {"Content-Type": "application/json"}); started = time.monotonic()
        with urllib.request.urlopen(req, timeout=self.timeout) as response: data = json.load(response)
        return data.get("response", ""), {"provider":"ollama", "model":self.model, "latency_ms":round((time.monotonic()-started)*1000), "usage":{k:data[k] for k in ("prompt_eval_count","eval_count") if k in data}}

class Gemini:
    def __init__(self, secret_handle=None): self.secret_handle = secret_handle
    def capability(self): return Capability("gemini", "public", True, "external-free", None, "available" if self.secret_handle else "auth_required")
    def infer(self, prompt):
        if not self.secret_handle: raise PermissionError("AUTH_REQUIRED")
        raise RuntimeError("secret_handle adapter not enabled in this local build")

class Runner:
    def __init__(self, db_path, local=None, external=None, paid=False):
        if paid: raise PermissionError("billing_enabled_requires_separate_authorization")
        self.db_path = str(db_path); Path(db_path).parent.mkdir(parents=True, exist_ok=True); self.local, self.external = local or Ollama(), external or Gemini()
        with sqlite3.connect(self.db_path) as db:
            db.execute("PRAGMA journal_mode=WAL"); db.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, prompt TEXT NOT NULL, privacy TEXT NOT NULL, state TEXT NOT NULL, result TEXT, meta TEXT)"); db.commit()
    def submit(self, job_id, prompt, privacy=None):
        cls = classify_privacy(prompt, privacy)
        with sqlite3.connect(self.db_path) as db: db.execute("INSERT OR IGNORE INTO jobs VALUES (?, ?, ?, 'queued', NULL, NULL)", (job_id, prompt, cls)); db.commit()
    def process(self, job_id):
        with sqlite3.connect(self.db_path) as db:
            row = db.execute("SELECT prompt, privacy, state, result, meta FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not row: raise KeyError(job_id)
            if row[2] in {"completed", "auth_required"}: return {"job_id":job_id,"state":row[2],"result":json.loads(row[3]) if row[3] else None,"meta":json.loads(row[4]) if row[4] else None}
            provider = self.local if row[1] == "private" else self.external
            try: result, meta = provider.infer(row[0]); state = "completed"
            except PermissionError as exc: result, meta, state = None, {"reason":str(exc)}, "auth_required"
            except Exception as exc: result, meta, state = None, {"reason":type(exc).__name__}, "queued"
            db.execute("UPDATE jobs SET state=?, result=?, meta=? WHERE id=? AND state='queued'", (state, json.dumps(result) if result is not None else None, json.dumps(meta), job_id)); db.commit()
            return {"job_id":job_id,"state":state,"result":result,"meta":meta}
    def status(self):
        with sqlite3.connect(self.db_path) as db: counts = dict(db.execute("SELECT state, COUNT(*) FROM jobs GROUP BY state").fetchall())
        return {"lanes":{"local":self.local.capability().as_dict(),"external":self.external.capability().as_dict()},"jobs":counts}
