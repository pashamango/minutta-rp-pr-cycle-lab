import unittest

from maintainer_agent import (
    ArtifactState,
    AuditReceipt,
    AuditVerdict,
    CaseState,
    MergeObservation,
    OperationState,
    PullRequestSnapshot,
    evaluate_merge_authority,
    merge_is_verified,
    transition,
)


POLICY = {
    "version": "MAINTAINER_POLICY/v1",
    "enabled": True,
    "repository": "acme/widget",
    "base_branches": ["main"],
    "autonomous_ceiling": "R1",
    "protected_paths": [".maintainer/**", ".github/workflows/**", "maintainer_agent/**"],
    "risk_rules": [
        {"pattern": "docs/**", "risk_class": "R0"},
        {"pattern": "src/**", "risk_class": "R1"},
    ],
}


def snapshot(paths=("docs/readme.md",)):
    return PullRequestSnapshot(
        repository="acme/widget",
        pr_number=7,
        base_branch="main",
        head_sha="a" * 40,
        base_sha="b" * 40,
        policy_root="policy-root-0001",
        author_identity="author-app",
        changed_paths=tuple(paths),
    )


def receipt(**overrides):
    values = dict(
        auditor_identity="auditor-app",
        verdict=AuditVerdict.PASS,
        repository="acme/widget",
        pr_number=7,
        head_sha="a" * 40,
        base_sha="b" * 40,
        policy_root="policy-root-0001",
        deterministic_checks_complete=True,
        semantic_checks_complete=True,
        unresolved_objections=(),
    )
    values.update(overrides)
    return AuditReceipt(**values)


def decide(snap=None, audit=None, **overrides):
    args = dict(
        current_head_sha="a" * 40,
        current_base_sha="b" * 40,
        current_policy_root="policy-root-0001",
        required_checks_pass=True,
        unresolved_threads=0,
        merge_identity="broker-app",
    )
    args.update(overrides)
    return evaluate_merge_authority(POLICY, snap or snapshot(), audit or receipt(), **args)


class AuthorityTests(unittest.TestCase):
    def test_low_risk_independent_pass_is_eligible(self):
        self.assertTrue(decide().eligible)

    def test_head_drift_invalidates_pass(self):
        result = decide(current_head_sha="c" * 40)
        self.assertFalse(result.eligible)
        self.assertIn("HEAD_SHA_DRIFT", result.reasons)

    def test_self_review_is_rejected(self):
        result = decide(audit=receipt(auditor_identity="author-app"))
        self.assertFalse(result.eligible)
        self.assertIn("SELF_REVIEW", result.reasons)

    def test_merge_identity_must_be_independent(self):
        result = decide(merge_identity="auditor-app")
        self.assertFalse(result.eligible)
        self.assertIn("IDENTITY_SEPARATION_VIOLATION", result.reasons)

    def test_constitutional_path_never_auto_merges(self):
        result = decide(snap=snapshot(("maintainer_agent/policy.py",)))
        self.assertFalse(result.eligible)
        self.assertIn("CONSTITUTIONAL_FIREWALL", result.reasons)

    def test_missing_semantic_evidence_is_not_pass(self):
        result = decide(audit=receipt(semantic_checks_complete=False))
        self.assertFalse(result.eligible)
        self.assertIn("SEMANTIC_EVIDENCE_INCOMPLETE", result.reasons)


class FinalityTests(unittest.TestCase):
    def test_enqueued_is_not_done(self):
        observation = MergeObservation(
            operation_state=OperationState.ENQUEUED,
            artifact_state=ArtifactState.UNMERGED,
            merge_oid=None,
            observed_pr_head_sha="a" * 40,
            observed_base_head_sha="b" * 40,
        )
        self.assertFalse(merge_is_verified(snapshot(), observation))

    def test_exact_merged_readback_is_done(self):
        observation = MergeObservation(
            operation_state=OperationState.MERGED,
            artifact_state=ArtifactState.MERGED,
            merge_oid="c" * 40,
            observed_pr_head_sha="a" * 40,
            observed_base_head_sha="c" * 40,
        )
        self.assertTrue(merge_is_verified(snapshot(), observation))

    def test_state_machine_rejects_shortcut(self):
        with self.assertRaises(ValueError):
            transition(CaseState.OBSERVED, CaseState.MERGED)


if __name__ == "__main__":
    unittest.main()
