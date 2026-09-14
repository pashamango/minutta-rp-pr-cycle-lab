import json
import pytest
from smart_router.credential_enrollment import *

M = EnrollmentManifest("google-gemini", "pavel.cherkashin@vestor.in", "projects/667742918474", "Gemini API Key for NICLI", "smart-router/google/projects/667742918474/gemini-nicli")
META = [{"name": "projects/667742918474/locations/global/keys/nicli", "display_name": M.key_display_name, "location": "global"}]

def test_end_to_end_fake_transfer_and_fresh_consumer():
    sentinel = b"fixture-secret-never-serialized"; sink = FakeSink(M.secret_handle)
    result = enroll(M, M.principal, [M.principal, "other@example.com"], META, FakeSource(sentinel), sink)
    assert sentinel.decode() not in json.dumps(result)
    assert sink.resolve(M.secret_handle).to_dict()["handle"] == M.secret_handle
    assert sink.state[M.secret_handle] == sentinel

@pytest.mark.parametrize("active,available", [("wrong@example.com", ["wrong@example.com"]), (M.principal, []), (None, [M.principal])])
def test_identity_fail_closed(active, available):
    with pytest.raises(EnrollmentError, match="ACCOUNT_MISMATCH"): enroll(M, active, available, META)

@pytest.mark.parametrize("meta", [[], [dict(META[0], name="projects/other/locations/global/keys/nicli")], [META[0], META[0]]])
def test_metadata_fail_closed(meta):
    with pytest.raises(EnrollmentError, match="KEY_METADATA_MATCH_COUNT"): enroll(M, M.principal, [M.principal], meta)

@pytest.mark.parametrize("source,sink,error", [(FakeSource(b"x", True), FakeSink(M.secret_handle), "SOURCE_FAILURE"), (FakeSource(b"x"), FakeSink(M.secret_handle, True), "SINK_FAILURE")])
def test_transfer_failures(source, sink, error):
    with pytest.raises(EnrollmentError, match=error): enroll(M, M.principal, [M.principal], META, source, sink)

def test_secret_bearing_receipt_is_not_serializable():
    class SecretBearing: pass
    with pytest.raises(EnrollmentError, match="RECEIPT_SERIALIZATION_REJECTED"): safe_json({"receipt": SecretBearing()})
