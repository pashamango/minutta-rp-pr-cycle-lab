#!/usr/bin/env python3
"""Dependency-free safety validator for VHP-08 manifests."""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SHA256 = re.compile(r"^[a-f0-9]{64}$")
SHA1 = re.compile(r"^[a-f0-9]{40}$")
ISSUE = re.compile(r"^[A-Z][A-Z0-9]+-[0-9]+$")


def fail(message):
    raise ValueError(message)


def url(value, prefix, field):
    if not isinstance(value, str) or not value.startswith(prefix):
        fail(f"{field} must start with {prefix}")


def validate(data):
    if not isinstance(data, dict): fail("manifest must be an object")
    for key in ("manifestVersion", "submissionId", "createdAt", "expiresAt", "project", "sources", "artifacts", "policy"):
        if key not in data: fail(f"missing required field: {key}")
    if data["manifestVersion"] != "1.0": fail("manifestVersion must be 1.0")
    if not re.fullmatch(r"vhp-[A-Za-z0-9][A-Za-z0-9._-]{7,127}", data["submissionId"]): fail("invalid submissionId")
    try:
        created = datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00"))
        expires = datetime.fromisoformat(data["expiresAt"].replace("Z", "+00:00"))
    except (TypeError, ValueError): fail("createdAt and expiresAt must be ISO-8601 timestamps")
    if created.tzinfo is None or expires.tzinfo is None or expires <= created: fail("expiresAt must be after createdAt and timezone-aware")
    project = data["project"]
    if not isinstance(project, dict) or not project.get("id") or not project.get("name"): fail("project.id and project.name are required")
    if "ticketId" in project and not ISSUE.fullmatch(project["ticketId"]): fail("invalid project.ticketId")
    sources = data["sources"]
    for key in ("drive", "linear", "github"):
        if key not in sources: fail(f"missing source: {key}")
    drive, linear, github = sources["drive"], sources["linear"], sources["github"]
    if not drive.get("fileId"): fail("drive.fileId is required")
    url(drive.get("webUrl"), "https://drive.google.com/", "drive.webUrl")
    if not ISSUE.fullmatch(linear.get("issueId", "")): fail("invalid linear.issueId")
    url(linear.get("issueUrl"), "https://linear.app/", "linear.issueUrl")
    if linear.get("state") not in ("In Progress", "In Review"): fail("linear.state must be In Progress or In Review")
    url(github.get("repoUrl"), "https://github.com/", "github.repoUrl")
    if not SHA1.fullmatch(github.get("commitSha", "")): fail("github.commitSha must be a 40-character lowercase SHA-1")
    if not isinstance(github.get("branch"), str) or not github["branch"] or github["branch"].startswith("/"): fail("invalid github.branch")
    artifacts = data["artifacts"]
    if not isinstance(artifacts, list) or not artifacts: fail("artifacts must be a non-empty array")
    for item in artifacts:
        path = item.get("path", "")
        if not path or path.startswith("/") or ".." in Path(path).parts: fail(f"unsafe artifact path: {path}")
        if not SHA256.fullmatch(item.get("sha256", "")): fail(f"invalid artifact sha256: {path}")
    policy = data["policy"]
    if policy.get("humanApprovalRequired") is not True or policy.get("autoMerge") is not False: fail("policy must require human approval and disable autoMerge")
    if set(policy.get("allowedHosts", [])) != {"drive.google.com", "linear.app", "github.com"}: fail("allowedHosts must be the three declared source hosts")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} MANIFEST.json", file=sys.stderr)
        sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as handle:
            validate(json.load(handle))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"VHP-08 INVALID: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"VHP-08 VALID: {sys.argv[1]}")
