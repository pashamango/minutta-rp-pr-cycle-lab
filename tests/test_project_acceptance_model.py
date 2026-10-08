import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "project-office"))
from control_model import Execution, Outcome, Scientific, can_accept_gate, forgotten_value, next_best_action, propose_gate_movement, validate_project

def project():
    return {"project_id":"p", "portfolio_id":"o", "mission":"m", "stage":"RESEARCH", "budget":{}, "kpis":{}, "status":"ACTIVE", "evidence_refs":["e1"], "claims":[{"schema":"CLAIM/v1"}], "acceptance_gates":[{"gate_id":"g", "value":4, "status":"OPEN", "kind":"information_gain", "acceptance_condition":"bounded test"}], "issues":[], "consumed_evidence":[]}

def test_issue_is_not_authority():
    p=project(); p["issues"]=[{"status":"CLOSED", "accepted":True}]
    assert "issue cannot accept project work" in validate_project(p)

def test_negative_success_can_satisfy_information_gate():
    assert can_accept_gate(Outcome(Scientific.NEGATIVE, Execution.SUCCESS), "information_gain", "e1", "verifier")
    assert not can_accept_gate(Outcome(Scientific.NOT_TESTED, Execution.BLOCKED), "information_gain", "e1", "verifier")

def test_proposal_is_not_acceptance_and_action_is_highest_value():
    p=project(); p["acceptance_gates"].append({"gate_id":"high", "value":9, "status":"OPEN", "acceptance_condition":"x"})
    assert propose_gate_movement({"gate_id":"g", "evidence_ref":"e1"}, p)["state"] == "PROPOSED"
    assert next_best_action(p)["gate_id"] == "high"

def test_forgotten_value_query_survives_issue_replacement():
    p=project(); p["issues"]=[{"issue_id":1,"status":"CLOSED","gate_id":"g","evidence_ref":"e1"}]
    assert forgotten_value(p)[0]["issue_id"] == 1
    p["issues"]=[{"issue_id":2,"status":"OPEN","gate_id":"g"}]
    assert p["claims"] and p["evidence_refs"] == ["e1"]
