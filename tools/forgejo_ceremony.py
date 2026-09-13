"""Synthetic-only capability handle and secret-free authorization boundary."""
from dataclasses import dataclass
import hashlib

ALLOWED = frozenset(("read", "push_non_protected", "create_pr"))

@dataclass(frozen=True)
class Capability:
    provider: str
    principal_id: str
    login: str
    repo: str
    verbs: frozenset
    handle: str
    active: bool = True

def handle(provider, principal_id, login, repo, capability):
    raw = "|".join((provider, principal_id, login, repo, capability))
    return "opaque:" + hashlib.sha256(raw.encode()).hexdigest()[:24]

def authorize(cap, principal_id, repo, verb):
    if not cap.active or cap.principal_id != principal_id or cap.repo != repo:
        raise PermissionError("capability mismatch")
    if verb not in cap.verbs or verb not in ALLOWED:
        raise PermissionError("verb denied")
    return cap.handle

