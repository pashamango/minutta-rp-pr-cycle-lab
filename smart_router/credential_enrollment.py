from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from typing import Any, Iterable, Protocol

class EnrollmentError(RuntimeError): pass

@dataclass(frozen=True)
class EnrollmentManifest:
    provider: str; principal: str; project: str; key_display_name: str; secret_handle: str
    policy: str = "free_only;public_only;no_billing;keychain_only"

@dataclass(frozen=True)
class IdentityBinding:
    provider: str; principal: str; project: str; location: str; key_display_name: str; resource_name: str

class SecretSource(Protocol):
    def deliver(self, sink: "SecretSink") -> None: ...
class SecretSink(Protocol):
    def accept(self, secret: bytes) -> "CapabilityReceipt": ...

@dataclass(frozen=True)
class CapabilityReceipt:
    protocol: str; handle: str; provider: str; principal_sha256: str = ""; project_sha256: str = ""
    def to_dict(self) -> dict[str, str]: return self.__dict__.copy()

def preflight_identity(manifest: EnrollmentManifest, active_principal: str | None, available_principals: Iterable[str] = ()) -> None:
    if active_principal != manifest.principal or active_principal not in tuple(available_principals): raise EnrollmentError("ACCOUNT_MISMATCH")

def select_identity(manifest: EnrollmentManifest, metadata: Iterable[dict[str, Any]]) -> IdentityBinding:
    prefix = f"{manifest.project}/locations/global/keys/"
    matches = [x for x in metadata if x.get("location") == "global" and x.get("display_name") == manifest.key_display_name and isinstance(x.get("name"), str) and x["name"].startswith(prefix)]
    if len(matches) != 1: raise EnrollmentError("KEY_METADATA_MATCH_COUNT")
    x = matches[0]; return IdentityBinding(manifest.provider, manifest.principal, manifest.project, "global", manifest.key_display_name, x["name"])

def capability(manifest: EnrollmentManifest) -> dict[str, Any]:
    return {"protocol": "smart-router-capability/v1", "provider": manifest.provider, "secret_handle": manifest.secret_handle, "policy": manifest.policy, "principal_sha256": hashlib.sha256(manifest.principal.encode()).hexdigest(), "project_sha256": hashlib.sha256(manifest.project.encode()).hexdigest()}

class FakeSource:
    def __init__(self, secret: bytes, fail: bool = False): self.secret, self.fail = secret, fail
    def deliver(self, sink: SecretSink) -> None:
        if self.fail: raise EnrollmentError("SOURCE_FAILURE")
        sink.accept(self.secret)

class FakeSink:
    def __init__(self, handle: str, fail: bool = False): self.handle, self.fail, self.state = handle, fail, {}
    def accept(self, secret: bytes) -> CapabilityReceipt:
        if self.fail: raise EnrollmentError("SINK_FAILURE")
        if not isinstance(secret, bytes): raise EnrollmentError("SECRET_TYPE_REQUIRED")
        self.state[self.handle] = bytes(secret); return CapabilityReceipt("smart-router-sealed-transfer/v1", self.handle, "google-gemini")
    def resolve(self, handle: str) -> CapabilityReceipt:
        if handle not in self.state: raise EnrollmentError("CAPABILITY_NOT_FOUND")
        return CapabilityReceipt("smart-router-sealed-transfer/v1", handle, "google-gemini")

def sealed_transfer(source: SecretSource, sink: SecretSink) -> CapabilityReceipt:
    result: CapabilityReceipt | None = None
    class DirectSink:
        def accept(self, secret: bytes) -> CapabilityReceipt:
            nonlocal result; result = sink.accept(secret); return result
    source.deliver(DirectSink())
    if result is None: raise EnrollmentError("TRANSFER_INCOMPLETE")
    return result

def enroll(manifest: EnrollmentManifest, active_principal: str | None, available_principals: Iterable[str], metadata: Iterable[dict[str, Any]], source: SecretSource | None = None, sink: SecretSink | None = None) -> dict[str, Any]:
    preflight_identity(manifest, active_principal, available_principals); binding = select_identity(manifest, metadata)
    result = {"verdict": "READY_FOR_SEALED_TRANSFER", "identity": binding.__dict__, "capability": capability(manifest)}
    if (source is None) != (sink is None): raise EnrollmentError("SOURCE_SINK_PAIR_REQUIRED")
    if source is not None: result["receipt"] = sealed_transfer(source, sink).to_dict()
    return result

def safe_json(value: Any) -> str:
    try: return json.dumps(value)
    except (TypeError, ValueError, OverflowError) as exc: raise EnrollmentError("RECEIPT_SERIALIZATION_REJECTED") from exc
