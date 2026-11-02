#!/usr/bin/env python3
"""Validate the DP-00 capability registry without network access."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "capability-registry.json"
ALLOWED = {"SOURCE_READ", "READ_BLOCKED", "SUMMARY_ONLY"}
REQUIRED = {"canonical_api", "credentials_owner", "scopes", "rate_limits", "pagination", "source_of_truth", "cost", "policy", "freshness", "backup_restore", "blocked_states", "access_state", "privacy_class", "last_verified_at", "verification_method"}
SECRET = re.compile(r"(?i)(bearer\s+|api[_-]?key\s*[:=]|password\s*[:=]|private[_-]?key|cookie\s*[:=]|oauth[_-]?code)")

def fail(message):
    raise AssertionError(message)

def main():
    data = json.loads(REGISTRY.read_text())
    if set(data["access_states"]) != ALLOWED:
        fail("access state vocabulary must be exactly SOURCE_READ/READ_BLOCKED/SUMMARY_ONLY")
    if data["consent"]["gmail_additional_accounts"]["separate_from_primary"] is not True:
        fail("additional Gmail consent must be separate")
    entries = data["capabilities"]
    if len(entries) < 1 or len({e["id"] for e in entries}) != len(entries):
        fail("capability IDs must be non-empty and unique")
    now = datetime.now(timezone.utc)
    for entry in entries:
        missing = REQUIRED - entry.keys()
        if missing:
            fail(f'{entry["id"]}: missing {sorted(missing)}')
        if entry["access_state"] not in ALLOWED:
            fail(f'{entry["id"]}: invalid access state')
        try:
            verified = datetime.fromisoformat(entry["last_verified_at"].replace("Z", "+00:00"))
        except ValueError as exc:
            fail(f'{entry["id"]}: invalid last_verified_at: {exc}')
        if verified > now:
            fail(f'{entry["id"]}: last_verified_at is in the future')
        if not entry["verification_method"]:
            fail(f'{entry["id"]}: verification_method is required')
        if SECRET.search(json.dumps(entry, sort_keys=True)):
            fail(f'{entry["id"]}: possible secret material')
    print(f"PASS: validated {len(entries)} capability entries; no secret material detected")

if __name__ == "__main__":
    main()
