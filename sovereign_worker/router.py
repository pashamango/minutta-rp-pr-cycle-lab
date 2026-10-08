"""Minimal fail-closed privacy router for the worker runway experiment."""
from dataclasses import dataclass
import json, os, time, urllib.request
@dataclass(frozen=True)
class Decision:
    lane: str
    reason: str
PRIVATE_MARKERS = ("private", "secret", "credential", "password", "correspondence", "unpublished")
def classify(goal):
    return Decision("local-private", "sensitive marker; external inference denied") if any(x in goal.casefold() for x in PRIVATE_MARKERS) else Decision("external-low-sensitivity", "no sensitive marker; external lane permitted")
def run_local(goal, model="gemma4:latest", url="http://127.0.0.1:11434/api/generate"):
    started=time.monotonic(); payload=json.dumps({"model":model,"prompt":goal,"stream":False}).encode()
    request=urllib.request.Request(url,payload,{"Content-Type":"application/json"})
    with urllib.request.urlopen(request, timeout=60) as response: body=json.load(response)
    return {"lane":"local-private","model":model,"response":body.get("response",""),"elapsed_seconds":round(time.monotonic()-started,3)}
def route(goal):
    decision=classify(goal)
    if decision.lane == "local-private":
        result=run_local(goal, os.environ.get("SOVEREIGN_LOCAL_MODEL", "gemma4:latest")); result["decision"]=decision.reason; return result
    return {"lane":decision.lane,"decision":decision.reason,"status":"AUTH_REQUEST_REQUIRED","provider":"google-gemini-ai-studio","secret_handling":"no credential read or emitted"}
