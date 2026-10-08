"""Portable PROJECT/v1 acceptance semantics; projections are never authority."""
from hashlib import sha256
import json
from dataclasses import dataclass
from enum import Enum

class Scientific(str, Enum):
    POSITIVE = "POSITIVE"; NEGATIVE = "NEGATIVE"; NOT_TESTED = "NOT_TESTED"
class Execution(str, Enum):
    SUCCESS = "SUCCESS"; BLOCKED = "BLOCKED"; FAILURE = "FAILURE"; NO_RESULT = "NO_RESULT"

@dataclass(frozen=True)
class Outcome:
    scientific: Scientific
    execution: Execution

def can_accept_gate(outcome, gate_kind, evidence, verifier):
    if not verifier or not evidence or outcome.execution is not Execution.SUCCESS: return False
    return outcome.scientific is Scientific.POSITIVE or (outcome.scientific is Scientific.NEGATIVE and gate_kind in {"falsification", "information_gain"})

def propose_gate_movement(packet, project):
    return {"project_id": project["project_id"], "gate_id": packet["gate_id"], "evidence_ref": packet["evidence_ref"], "state": "PROPOSED"}

def verify_gate_transition(project, packet, verifier):
    """The sole acceptance transition; issue state is never consulted."""
    gate = next((g for g in project.get("acceptance_gates", []) if g.get("gate_id") == packet.get("gate_id")), None)
    evidence = next((e for e in project.get("evidence", []) if e.get("evidence_ref") == packet.get("evidence_ref")), None)
    reason = None
    if not verifier: reason = "verifier required"
    elif packet.get("project_id") != project.get("project_id") or not gate: reason = "wrong project or gate binding"
    elif packet.get("company_id") != project.get("company_id") or packet.get("portfolio_id") != project.get("portfolio_id"): reason = "identity binding failed"
    elif not evidence or evidence.get("consumed"): reason = "evidence missing or already consumed"
    elif packet.get("exception", {}).get("kind") == "NO_PR_REQUIRED" and (packet["exception"].get("worker_granted") or not packet["exception"].get("granting_authority") or not packet["exception"].get("immutable_receipt")): reason = "unauthorized exception"
    elif not can_accept_gate(Outcome(Scientific(packet["scientific"]), Execution(packet["execution"])), gate.get("kind"), evidence, verifier): reason = "evidence does not satisfy gate"
    if reason:
        return {"state": "REJECTED", "project_id": project.get("project_id"), "gate_id": packet.get("gate_id"), "evidence_ref": packet.get("evidence_ref"), "reason": reason, "evidence_retained": True}
    evidence["consumed"] = True
    gate["status"] = "ACCEPTED"
    digest = sha256(json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"state": "ACCEPTED", "project_id": project["project_id"], "gate_id": gate["gate_id"], "evidence_ref": evidence["evidence_ref"], "verifier": verifier, "evidence_digest": digest}

def next_best_action(project):
    unmet = [g for g in project.get("acceptance_gates", []) if g.get("status") != "ACCEPTED"]
    if not unmet: return None
    gate = max(unmet, key=lambda g: (g.get("value", 0), g["gate_id"]))
    return {"project_id": project["project_id"], "gate_id": gate["gate_id"], "work_package": {"kind": "bounded", "parent_project": project["project_id"], "acceptance_condition": gate["acceptance_condition"]}}

def forgotten_value(project):
    unmet = {g["gate_id"] for g in project.get("acceptance_gates", []) if g.get("status") != "ACCEPTED"}
    return [i for i in project.get("issues", []) if i.get("status") == "CLOSED" and i.get("evidence_ref") and i.get("gate_id") in unmet and i["evidence_ref"] not in project.get("consumed_evidence", [])]

def validate_project(project):
    required = ("company_id", "project_id", "portfolio_id", "mission", "stage", "budget", "kpis", "acceptance_gates", "claims", "evidence_refs", "status")
    errors = [f"missing {k}" for k in required if not project.get(k)]
    if project.get("status") not in {"ACTIVE", "PARKED", "COMPLETED"}: errors.append("invalid status")
    if any(i.get("accepted") for i in project.get("issues", [])): errors.append("issue cannot accept project work")
    if any(c.get("schema") != "CLAIM/v1" for c in project.get("claims", [])): errors.append("claim schema required")
    return errors
