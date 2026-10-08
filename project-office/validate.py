#!/usr/bin/env python3
"""Dependency-free validator for the Project Office shadow state."""
import json, sys

STAGES = ["IDEA", "RP", "RESEARCH", "SYNTHESIS", "IC_DECISION", "FOUNDER_CHARTER", "PROJECT_STATUS"]
def validate(s):
    errors=[]
    if s.get("status") not in STAGES: errors.append("unknown status")
    if not s.get("rp"): errors.append("RP required")
    if not isinstance(s.get("research"), list): errors.append("research must be an array")
    if s.get("status") in STAGES[3:] and not s.get("synthesis"): errors.append("synthesis required")
    if s.get("status") in STAGES[4:] and (not s.get("ic_decision") or s["ic_decision"].get("recommendation") not in {"INVEST","RESEARCH_MORE","PARK","KILL"}): errors.append("IC decision required")
    if s.get("status") in STAGES[5:] and not s.get("founder_charter"): errors.append("founder charter required")
    if s.get("status") == "PROJECT_STATUS" and s.get("project_status") not in {"ACTIVE","PARKED","KILLED"}: errors.append("project status required")
    if s.get("execution_requested") and (not s.get("synthesis") or not s.get("ic_decision") or not s.get("founder_charter")): errors.append("RP -> EXECUTION invalid without synthesis + IC decision + founder charter")
    if s.get("founder_charter") and s["founder_charter"].get("how_plan_copied_from_research"): errors.append("founder receives constraints, not research HOW")
    return errors
if __name__ == "__main__":
    with open(sys.argv[1]) as f: state=json.load(f)
    e=validate(state)
    print(json.dumps({"valid":not e,"errors":e}, indent=2)); sys.exit(bool(e))
