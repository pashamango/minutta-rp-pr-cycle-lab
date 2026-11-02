#!/usr/bin/env python3
"""Fail-closed local RP factory; no network or credentials are used."""
from __future__ import annotations
import argparse, hashlib, json, shlex, subprocess, sys
from pathlib import Path

TERMINAL = {"PASSED", "FAILED", "BLOCKED"}

def digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def build(anomaly: dict, out: Path) -> dict:
    required = {"anomaly_id", "observation", "source_receipt", "owner", "cost", "risk", "confidence"}
    missing = sorted(required - anomaly.keys())
    if missing: raise ValueError("missing anomaly fields: " + ", ".join(missing))
    rp = {"rp_id": "rp-" + anomaly["anomaly_id"], "type": "research_proposal",
          "anomaly": anomaly, "acceptance": ["fixture replays deterministically",
          "authorized test has a terminal outcome", "outcome digest verifies"],
          "execution": {"mode": "fixture_only", "forgejo_authorized": False}, "status": "PROPOSED"}
    fixture = {"fixture_id": rp["rp_id"] + "-fixture", "input": anomaly,
               "expected": {"anomaly_id": anomaly["anomaly_id"]}}
    issue = {"title": "[RP] " + rp["rp_id"], "rp_id": rp["rp_id"], "status": "DRAFT",
             "source_receipt": anomaly["source_receipt"], "private_evidence": True}
    for name, value in (("proposal.json", rp), ("fixture.json", fixture), ("issue.json", issue)):
        write_json(out / name, value)
    return rp

def run_cycle(out: Path, authorize_forgejo: bool, command: str | None) -> dict:
    rp = json.loads((out / "proposal.json").read_text())
    fixture = json.loads((out / "fixture.json").read_text())
    if fixture["expected"] != {"anomaly_id": rp["anomaly"]["anomaly_id"]}:
        status, detail = "FAILED", "fixture mismatch"
    elif not authorize_forgejo:
        status, detail = "BLOCKED", "explicit Forgejo authorization is required"
    else:
        # The command is deliberately opt-in and bounded to a caller-supplied fixture command.
        result = subprocess.run(shlex.split(command or "true"), cwd=out, text=True,
                                capture_output=True, timeout=30, check=False)
        status, detail = ("PASSED", "authorized fixture test exited 0") if result.returncode == 0 else ("FAILED", "fixture test exit " + str(result.returncode))
    outcome = {"rp_id": rp["rp_id"], "status": status, "detail": detail,
               "forgejo": {"authorized": authorize_forgejo, "command": command or "true"},
               "fixture_digest": digest(fixture)}
    outcome["outcome_digest"] = digest(outcome)
    write_json(out / "outcome.json", outcome)
    return outcome

def publish_bundle(out: Path) -> dict:
    outcome = json.loads((out / "outcome.json").read_text())
    if outcome["status"] != "PASSED":
        raise ValueError("publication requires PASSED outcome; private evidence retained")
    bundle = {"kind": "github_pr_proposal", "rp_id": outcome["rp_id"],
              "public_artifacts": ["outcome.json"], "private_evidence": ["proposal.json", "fixture.json", "issue.json"],
              "merge": "human review required; never bypass protected main", "outcome_digest": outcome["outcome_digest"]}
    write_json(out / "github-pr-proposal.json", bundle)
    return bundle

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="op", required=True)
    b = sub.add_parser("build"); b.add_argument("anomaly"); b.add_argument("out", type=Path)
    r = sub.add_parser("run"); r.add_argument("out", type=Path); r.add_argument("--authorize-forgejo", action="store_true"); r.add_argument("--command")
    g = sub.add_parser("publish"); g.add_argument("out", type=Path)
    a = p.parse_args(argv)
    try:
        if a.op == "build": result = build(json.loads(Path(a.anomaly).read_text()), a.out)
        elif a.op == "run": result = run_cycle(a.out, a.authorize_forgejo, a.command)
        else: result = publish_bundle(a.out)
        print(json.dumps(result, sort_keys=True)); return 0
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr); return 2

if __name__ == "__main__": sys.exit(main())
