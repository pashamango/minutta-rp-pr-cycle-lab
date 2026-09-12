import json
import pytest

from smart_router.credential_enrollment import (EnrollmentError, EnrollmentManifest,
                                                  capability, enroll)


M = EnrollmentManifest("google-gemini", "pavel.cherkashin@vestor.in",
                       "projects/667742918474", "Gemini API Key for NICLI",
                       "smart-router/google/projects/667742918474/gemini-nicli")
META = [{"name": "projects/667742918474/locations/global/keys/nicli", "display_name": M.key_display_name, "location": "global"}]


def test_expected_identity_and_unique_metadata_is_ready_for_auth():
    result = enroll(M, [M.principal], META)
    assert result["verdict"] == "AUTH_REQUIRED_WITH_READY_CEREMONY"
    assert result["capability"]["secret_handle"] == M.secret_handle


@pytest.mark.parametrize("principal", ["minutta@gmail.com", "unknown@example.com"])
def test_wrong_identity_fails_before_metadata_or_secret(principal):
    with pytest.raises(EnrollmentError, match="ACCOUNT_MISMATCH"):
        enroll(M, [principal], META)


@pytest.mark.parametrize("metadata", [[], [META[0], dict(META[0])]])
def test_zero_or_multiple_matches_fail_closed(metadata):
    with pytest.raises(EnrollmentError, match="KEY_METADATA_MATCH_COUNT"):
        enroll(M, [M.principal], metadata)


def test_capability_and_all_serialized_outputs_exclude_secret_sentinel():
    sentinel = "fixture-secret-never-serialized"
    result = enroll(M, [M.principal], META)
    blob = json.dumps({"result": result, "capability": capability(M)})
    assert sentinel not in blob
    assert "api_key" not in blob

