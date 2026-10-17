"""Deterministic shadow-admission CLI for NICLI Dispatcher v0.1 (MIN-74 / MIN-75).

Evaluates candidate Linear issue snapshots against the deterministic NICLI admission rules:
- Issue safety: valid ID regex, MIN team key
- Status and label guards: status == "Todo", no VETO / Human-Hold, no Canceled/Icebox
- Role requirements: "Role: Builder-Ready" present on issue
- Role conflict prevention: no "Role: Architect-Needed" on issue or parent
- Parent guards: parent exists and carries "Role: PM-Watch"
- IC and handoff provenance: parent IC decision reference and R4 handoff references required
- Dependency resolution: all blocked_by relations must be "Done"
- Concrete execution spec: source_repo, source_commit, and acceptance_commands mandatory
- Pinned model policy: Gemini 3.8 Flash Medium pinned; zero model calls during admission.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Sequence

from .core import (
    ALLOWED_AUTH_LANES,
    DEFAULT_CLI_VERSION,
    DEFAULT_PINNED_MODEL,
    NICLI_SHADOW_ADMISSION_SCHEMA,
    AdmissionDecision,
    DispatcherError,
    LinearIssueSnapshot,
    compute_task_revision_hash,
    evaluate_admission,
)

UTC = dt.timezone.utc


def parse_candidates_json(content: str) -> list[LinearIssueSnapshot]:
    """Parse a JSON string containing either a single issue object or an array of issues."""
    try:
        raw = json.loads(content)
    except json.JSONDecodeError as exc:
        raise DispatcherError("INVALID_JSON", f"Malformed JSON input: {exc}") from exc

    if isinstance(raw, dict):
        # Support either {"candidates": [...]} wrapper or single issue snapshot
        if "candidates" in raw and isinstance(raw["candidates"], list):
            items = raw["candidates"]
        elif "issue_id" in raw:
            items = [raw]
        else:
            raise DispatcherError(
                "UNRECOGNIZED_FIXTURE_SHAPE",
                "Input JSON must be an issue snapshot, an array of snapshots, or an object with 'candidates'",
            )
    elif isinstance(raw, list):
        items = raw
    else:
        raise DispatcherError("UNEXPECTED_JSON_TYPE", f"Expected dict or list, got {type(raw).__name__}")

    snapshots: list[LinearIssueSnapshot] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise DispatcherError("INVALID_CANDIDATE_ENTRY", f"Item #{idx} is not an object")
        try:
            snapshots.append(LinearIssueSnapshot.from_dict(item))
        except KeyError as exc:
            raise DispatcherError("MISSING_REQUIRED_FIELD", f"Item #{idx} missing required key: {exc}") from exc
    return snapshots


def run_shadow_admission(
    candidates: Iterable[LinearIssueSnapshot | dict[str, Any]],
    *,
    now: str | None = None,
    pinned_model: str = DEFAULT_PINNED_MODEL,
    cli_version: str = DEFAULT_CLI_VERSION,
    auth_mode: str = "api_key",
    quota_bucket: str = "ai-studio-free-tier",
    max_wip: int = 1,
) -> dict[str, Any]:
    """Deterministically evaluate candidates for shadow admission without making inference calls."""
    if auth_mode not in ALLOWED_AUTH_LANES:
        raise DispatcherError("UNSUPPORTED_AUTH_MODE", f"Unsupported auth_mode: {auth_mode}")
    if quota_bucket != ALLOWED_AUTH_LANES[auth_mode]:
        raise DispatcherError("QUOTA_BUCKET_MISMATCH", f"auth_mode {auth_mode} must match quota_bucket {ALLOWED_AUTH_LANES[auth_mode]}")
    if max_wip != 1:
        raise DispatcherError("INVALID_WIP_CONFIG", "initial pilot requires max_wip == 1")

    timestamp = now or dt.datetime.now(UTC).isoformat().replace("+00:00", "Z")

    snapshots: list[LinearIssueSnapshot] = []
    for c in candidates:
        if isinstance(c, dict):
            snapshots.append(LinearIssueSnapshot.from_dict(c))
        elif isinstance(c, LinearIssueSnapshot):
            snapshots.append(c)
        else:
            raise DispatcherError("INVALID_CANDIDATE_TYPE", f"Expected dict or LinearIssueSnapshot, got {type(c).__name__}")

    decisions: list[dict[str, Any]] = []
    rejections: dict[str, str] = {}
    rejection_breakdown: dict[str, int] = {}
    admitted_count = 0

    for snap in snapshots:
        decision = evaluate_admission(snap)
        item: dict[str, Any] = {
            "issue_id": snap.issue_id,
            "uuid": snap.uuid,
            "team_key": snap.team_key,
            "title": snap.title,
            "status": snap.status,
            "labels": list(snap.labels),
            "parent_id": snap.parent_id,
            "parent_status": snap.parent_status,
            "parent_labels": list(snap.parent_labels),
            "admitted": decision.admitted,
            "task_revision_hash": decision.task_revision_hash,
            "blocker_code": decision.blocker_code,
            "detail": decision.detail,
        }
        decisions.append(item)
        if decision.admitted:
            admitted_count += 1
        else:
            code = decision.blocker_code or "UNKNOWN_BLOCKER"
            rejections[snap.issue_id] = code
            rejection_breakdown[code] = rejection_breakdown.get(code, 0) + 1

    summary = {
        "total_evaluated": len(snapshots),
        "admitted_count": admitted_count,
        "rejected_count": len(snapshots) - admitted_count,
        "model_calls": 0,
        "rejections": rejections,
        "rejection_breakdown": dict(sorted(rejection_breakdown.items())),
    }

    return {
        "schema": NICLI_SHADOW_ADMISSION_SCHEMA,
        "generated_at": timestamp,
        "pinned_model": pinned_model,
        "cli_version": cli_version,
        "auth_mode": auth_mode,
        "quota_bucket": quota_bucket,
        "max_wip": max_wip,
        "summary": summary,
        "decisions": decisions,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nicli-dispatcher",
        description="NICLI Dispatcher v0.1 — Deterministic Shadow-Admission and Control Plane CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # shadow-admit subcommand
    admit_p = subparsers.add_parser("shadow-admit", help="Run deterministic shadow-admission on candidate fixture(s)")
    admit_p.add_argument("--input", "-i", required=True, help="Path to input JSON fixture (- for stdin)")
    admit_p.add_argument("--output", "-o", help="Path to write JSON report (stdout if omitted)")
    admit_p.add_argument("--pinned-model", default=DEFAULT_PINNED_MODEL, help="Pinned model name")
    admit_p.add_argument("--cli-version", default=DEFAULT_CLI_VERSION, help="Dispatcher CLI version")
    admit_p.add_argument("--auth-mode", default="api_key", choices=list(ALLOWED_AUTH_LANES.keys()))
    admit_p.add_argument("--quota-bucket", default="ai-studio-free-tier")
    admit_p.add_argument("--max-wip", type=int, default=1)
    admit_p.add_argument("--indent", type=int, default=2, help="Indentation for JSON output")
    admit_p.add_argument("--now", help="Explicit ISO UTC timestamp for deterministic reproducibility")

    # version subcommand
    subparsers.add_parser("version", help="Print version, pinned model and schema metadata")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "version":
        info = {
            "version": DEFAULT_CLI_VERSION,
            "pinned_model": DEFAULT_PINNED_MODEL,
            "schemas": {
                "shadow_admission": NICLI_SHADOW_ADMISSION_SCHEMA,
            },
            "allowed_auth_lanes": ALLOWED_AUTH_LANES,
        }
        sys.stdout.write(json.dumps(info, indent=2) + "\n")
        return 0

    if args.command == "shadow-admit" or (args.command is None and len(sys.argv) > 1 and "--input" in sys.argv):
        # Default to shadow-admit if --input is passed without explicit subcommand
        if args.command is None:
            # Re-parse with implicit subcommand
            args = parser.parse_args(["shadow-admit"] + (list(argv) if argv is not None else sys.argv[1:]))

        if args.input == "-":
            content = sys.stdin.read()
        else:
            in_path = Path(args.input)
            if not in_path.is_file():
                sys.stderr.write(f"Error: input file not found: {args.input}\n")
                return 1
            content = in_path.read_text(encoding="utf-8")

        try:
            candidates = parse_candidates_json(content)
            result = run_shadow_admission(
                candidates,
                now=args.now,
                pinned_model=args.pinned_model,
                cli_version=args.cli_version,
                auth_mode=args.auth_mode,
                quota_bucket=args.quota_bucket,
                max_wip=args.max_wip,
            )
        except DispatcherError as exc:
            sys.stderr.write(f"DispatcherError [{exc.code}]: {exc}\n")
            return 2

        output_str = json.dumps(result, indent=args.indent, ensure_ascii=False) + "\n"
        if args.output:
            out_path = Path(args.output)
            try:
                out_path.parent.mkdir(parents=True, exist_ok=True)
            except OSError:
                pass
            out_path.write_text(output_str, encoding="utf-8")
        else:
            sys.stdout.write(output_str)
        return 0

    parser.print_help(sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
