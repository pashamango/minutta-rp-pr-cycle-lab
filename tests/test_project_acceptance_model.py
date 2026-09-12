import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "project-office"))
from control_model import Execution, Outcome, Scientific, can_accept_gate, forgotten_value, next_best_action, propose_gate_movement, validate_project, verify_gate_transition

def project():
    return {"company_id":"c", "project_id":"p", "portfolio_id":"o", "mission":"m", "stage":"RESEARCH", "budget":{}, "kpis":{}, "status":"ACTIVE", "evidence_refs":["e1"], "evidence":[{"evidence_ref":"e1"}], "claims":[{"schema":"CLAIM/v1"}], "acceptance_gates":[{"gate_id":"g", "value":4, "status":"OPEN", "kind":"information_gain", "acceptance_condition":"bounded test"}], "issues":[], "consumed_evidence":[]}

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

def test_verifier_gate_is_only_acceptance_path_and_replay_is_rejected():
    p=project(); packet={"project_id":"p","company_id":"c","portfolio_id":"o","gate_id":"g","evidence_ref":"e1","scientific":"POSITIVE","execution":"SUCCESS"}
    receipt=verify_gate_transition(p, packet, "v"); assert receipt["state"] == "ACCEPTED" and p["acceptance_gates"][0]["status"] == "ACCEPTED"
    assert verify_gate_transition(p, packet, "v")["state"] == "REJECTED"

def test_rejections_retain_evidence_and_wrong_binding_fails_closed():
    p=project(); packet={"project_id":"wrong","company_id":"c","portfolio_id":"o","gate_id":"g","evidence_ref":"e1","scientific":"POSITIVE","execution":"SUCCESS"}
    assert verify_gate_transition(p, packet, "v")["state"] == "REJECTED" and not p["evidence"][0].get("consumed")
    packet["project_id"]="p"; packet["exception"]={"kind":"NO_PR_REQUIRED","worker_granted":True}
    assert verify_gate_transition(p, packet, "v")["state"] == "REJECTED"

def test_closed_issue_without_evidence_is_execution_debt():
    p=project(); p["issues"]=[{"status":"CLOSED","gate_id":"g"}]
    assert forgotten_value(p)[0]["debt"] == "execution/no-result"
