"""Portable project acceptance semantics; boards are projections, not truth."""
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

def next_best_action(project):
    unmet = [g for g in project.get("acceptance_gates", []) if g.get("status") != "ACCEPTED"]
    if not unmet: return None
    gate = max(unmet, key=lambda g: (g.get("value", 0), g["gate_id"]))
    return {"project_id": project["project_id"], "gate_id": gate["gate_id"], "work_package": {"kind": "bounded", "parent_project": project["project_id"], "acceptance_condition": gate["acceptance_condition"]}}

def forgotten_value(project):
    unmet = {g["gate_id"] for g in project.get("acceptance_gates", []) if g.get("status") != "ACCEPTED"}
    return [i for i in project.get("issues", []) if i.get("status") == "CLOSED" and i.get("evidence_ref") and i.get("gate_id") in unmet and i["evidence_ref"] not in project.get("consumed_evidence", [])]

def validate_project(project):
    required = ("project_id", "portfolio_id", "mission", "stage", "budget", "kpis", "acceptance_gates", "claims", "evidence_refs", "status")
    errors = [f"missing {k}" for k in required if k not in project]
    if project.get("status") not in {"ACTIVE", "PARKED", "COMPLETED"}: errors.append("invalid status")
    if any(i.get("accepted") for i in project.get("issues", [])): errors.append("issue cannot accept project work")
    if any(c.get("schema") != "CLAIM/v1" for c in project.get("claims", [])): errors.append("claim schema required")
    return errors
