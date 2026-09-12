from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Iterable


class EnrollmentError(RuntimeError):
    pass


@dataclass(frozen=True)
class EnrollmentManifest:
    provider: str
    principal: str
    project: str
    key_display_name: str
    secret_handle: str
    policy: str = "free_only;public_only;no_billing;keychain_only"


def preflight_identity(manifest: EnrollmentManifest, authenticated_principals: Iterable[str]) -> None:
    principals = tuple(authenticated_principals)
    if principals != (manifest.principal,):
        raise EnrollmentError("ACCOUNT_MISMATCH")


def select_key_metadata(manifest: EnrollmentManifest, metadata: Iterable[dict[str, Any]]) -> dict[str, Any]:
    matches = [item for item in metadata
               if item.get("location") == "global"
               and item.get("display_name") == manifest.key_display_name]
    if len(matches) != 1:
        raise EnrollmentError("KEY_METADATA_MATCH_COUNT")
    item = matches[0]
    return {"name": item.get("name"), "display_name": item.get("display_name"),
            "location": item.get("location"), "project": manifest.project}


def capability(manifest: EnrollmentManifest) -> dict[str, Any]:
    """Return only provider-neutral, non-secret enrollment facts."""
    return {"protocol": "smart-router-capability/v1", "provider": manifest.provider,
            "secret_handle": manifest.secret_handle, "policy": manifest.policy,
            "principal_sha256": hashlib.sha256(manifest.principal.encode()).hexdigest(),
            "project_sha256": hashlib.sha256(manifest.project.encode()).hexdigest()}


def auth_request(manifest: EnrollmentManifest) -> dict[str, Any]:
    return {"protocol": "AUTH_REQUEST/v1", "reason": "management_permission_missing",
            "account": manifest.principal, "ceremony": "Google Cloud CLI OAuth in the verified account",
            "continuation": "rerun the enrollment command after authorization"}


def enroll(manifest: EnrollmentManifest, authenticated_principals: Iterable[str],
           metadata: Iterable[dict[str, Any]], management_credential: str | None = None) -> dict[str, Any]:
    preflight_identity(manifest, authenticated_principals)
    selected = select_key_metadata(manifest, metadata)
    if not management_credential:
        return {"verdict": "AUTH_REQUIRED_WITH_READY_CEREMONY", "auth_request": auth_request(manifest),
                "key_metadata": selected, "capability": capability(manifest)}
    raise EnrollmentError("SECRET_DEPOSIT_REQUIRES_SECURITYMANAGER")

