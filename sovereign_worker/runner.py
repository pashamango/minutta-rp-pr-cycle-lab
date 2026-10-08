from __future__ import annotations
import hashlib, json, os, sqlite3, subprocess, time, urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path

PRIVATE_MARKERS = ("private", "secret", "password", "token", "credential", "api_key")

def classify_privacy(prompt: str, requested: str | None = None) -> str:
    inferred = "private" if any(x in prompt.lower() for x in PRIVATE_MARKERS) else "public"
    value = requested or inferred
    if value not in {"public", "private"} or (value == "public" and inferred == "private"):
        raise ValueError("ambiguous_privacy_class")
    return value

@dataclass
class Capability:
    provider: str; privacy_class: str; free_only: bool; model: str; availability: str
    def as_dict(self): return asdict(self)

class Ollama:
    def __init__(self, url="http://127.0.0.1:11434", model="gemma4:latest", timeout=90):
        self.url, self.model, self.timeout = url.rstrip("/"), model, timeout
    def capability(self): return Capability("ollama", "private", True, self.model, "configured")
    def infer(self, prompt):
        body = json.dumps({"model": self.model, "prompt": prompt, "stream": False, "think": False}).encode()
        req = urllib.request.Request(self.url + "/api/generate", body, {"Content-Type": "application/json"})
        started = time.monotonic()
        with urllib.request.urlopen(req, timeout=self.timeout) as response: data = json.load(response)
        return data.get("response", ""), {"provider":"ollama", "model":self.model,
            "latency_ms":round((time.monotonic()-started)*1000),
            "usage":{k:data[k] for k in ("prompt_eval_count", "eval_count") if k in data}, "retries":0}

class StubExternal:
    def capability(self): return Capability("synthetic-external", "public", True, "stub-v1", "available")
    def infer(self, prompt): return "synthetic external result: " + prompt, {"provider":"synthetic-external", "model":"stub-v1", "latency_ms":0, "usage":{}, "retries":0}

class NoAuthExternal:
    def capability(self): return Capability("external", "public", True, "unselected", "auth_required")
    def infer(self, prompt): raise PermissionError("AUTH_REQUIRED")

class GeminiExternal:
    """Minimal public-only Gemini adapter; the key is process-bound and never persisted."""
    ENV_KEY = "GEMINI_API_KEY"
    KEYCHAIN_SERVICE = "chitakasha.gemini.api-key"
    DEFAULT_MODEL = "gemini-flash-latest"
    def __init__(self, model=DEFAULT_MODEL, timeout=30, api_key=None):
        self.model, self.timeout = model, timeout
        self._api_key = api_key if api_key is not None else self._load_key()
    @classmethod
    def _load_key(cls):
        value = os.environ.get(cls.ENV_KEY)
        if value:
            return value
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-s", cls.KEYCHAIN_SERVICE, "-w"],
                check=True, capture_output=True, text=True, timeout=3,
            )
            return result.stdout.strip() or None
        except (FileNotFoundError, subprocess.SubprocessError):
            return None
    def capability(self):
        return Capability("google-gemini", "public", True, self.model,
                          "configured" if self._api_key else "auth_required")
    def infer(self, prompt):
        if not self._api_key: raise PermissionError("AUTH_REQUIRED")
        body = json.dumps({"contents":[{"parts":[{"text":prompt}]}],
                           "generationConfig":{"maxOutputTokens":512}}).encode()
        url = ("https://generativelanguage.googleapis.com/v1beta/models/" +
               self.model + ":generateContent?key=" + self._api_key)
        req = urllib.request.Request(url, body, {"Content-Type":"application/json"})
        started = time.monotonic()
        with urllib.request.urlopen(req, timeout=self.timeout) as response: data = json.load(response)
        candidates = data.get("candidates", [])
        result = "".join(p.get("text", "") for p in candidates[0].get("content", {}).get("parts", [])) if candidates else ""
        usage = data.get("usageMetadata", {})
        return result, {"provider":"google-gemini", "model":self.model,
            "latency_ms":round((time.monotonic()-started)*1000),
            "usage":{k:usage[k] for k in ("promptTokenCount","candidatesTokenCount","totalTokenCount") if k in usage}, "retries":0}

class Runner:
    def __init__(self, db_path, local=None, external=None, paid=False):
        if paid: raise PermissionError("billing_enabled_requires_separate_authorization")
        self.db_path = str(db_path); Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.local, self.external = local or Ollama(), external or GeminiExternal()
        with sqlite3.connect(self.db_path) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, prompt TEXT NOT NULL, privacy TEXT NOT NULL, state TEXT NOT NULL, result TEXT, receipt TEXT)")

    def submit(self, job_id, prompt, privacy=None, budget=None):
        cls = classify_privacy(prompt, privacy)
        policy = budget or {"free_only": True, "max_retries": 0, "max_output_tokens": 512}
        with sqlite3.connect(self.db_path) as db:
            db.execute("INSERT OR IGNORE INTO jobs VALUES (?, ?, ?, 'queued', NULL, ?)", (job_id, prompt, cls, json.dumps({"budget":policy})))

    def process(self, job_id):
        with sqlite3.connect(self.db_path) as db:
            row = db.execute("SELECT prompt,privacy,state,result,receipt FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not row: raise KeyError(job_id)
            if row[2] == "completed": return {"job_id":job_id,"state":row[2],"result":json.loads(row[3]),"receipt":json.loads(row[4])}
            provider = self.local if row[1] == "private" else self.external
            try:
                result, meta = provider.infer(row[0]); state = "completed"
            except PermissionError as exc:
                result, meta, state = None, {"reason":str(exc), "retries":0}, "queued"
            except Exception as exc:
                result, meta, state = None, {"reason":type(exc).__name__, "retries":0}, "queued"
            receipt = {"job_id":job_id, "route":row[1], "state":state, **meta}
            if result is not None: receipt["artifact_sha256"] = hashlib.sha256(result.encode()).hexdigest()
            db.execute("UPDATE jobs SET state=?,result=?,receipt=? WHERE id=? AND state='queued'", (state, json.dumps(result) if result is not None else None, json.dumps(receipt), job_id)); db.commit()
            return {"job_id":job_id,"state":state,"result":result,"receipt":receipt}

    def capability_card(self):
        return {"protocol":"worker-capability-card/v1", "task_classes":["bounded-inference"], "privacy_classes":["private","public"], "capacity":{"local":"configured","external":self.external.capability().availability}, "credentials":"not_exposed"}
