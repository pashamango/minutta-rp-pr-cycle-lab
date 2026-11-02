#!/usr/bin/env python3
"""
Unit and Integration Tests for AMDE Guide Bot & Zero-GitHub Onboarding (MIN-86)
"""

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.amde_guide_bot import (
    AMDEAttestationEngine,
    AgentIdentity,
    OnboardingOrchestrator,
    PreflightChecker,
    b58encode,
    canonical_json,
    derive_did_key,
    ed25519_publickey,
    ed25519_sign,
    ed25519_verify,
    parse_onboarding_input,
)


class TestAMDEGuideBot(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)
        # Create minimal docs
        docs_dir = self.repo_root / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        backlog_file = docs_dir / "AMDE_CONTRIB_BACKLOG_V0.1.json"
        with open(backlog_file, "w", encoding="utf-8") as f:
            json.dump({
                "protocol": "amde-contrib-0.1",
                "items": [
                    {
                        "id": "amde/millennium-problems/riemann-hypothesis/critical-strip",
                        "title": "Critical Strip: Lean verification + arXiv template",
                        "starter_example": True,
                    }
                ]
            }, f)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_pure_python_ed25519_roundtrip(self):
        sk = os.urandom(32)
        pk = ed25519_publickey(sk)
        self.assertEqual(len(pk), 32)

        msg = b"Mathematical truth requires zero central authority."
        sig = ed25519_sign(msg, sk, pk)
        self.assertEqual(len(sig), 64)

        # Verification must pass for identical message
        self.assertTrue(ed25519_verify(sig, msg, pk))

        # Verification must fail for tampered message or bad key
        self.assertFalse(ed25519_verify(sig, b"Tampered claim", pk))
        bad_pk = os.urandom(32)
        self.assertFalse(ed25519_verify(sig, msg, bad_pk))

    def test_did_key_derivation(self):
        raw_pk = b"\x01" * 32
        did = derive_did_key(raw_pk)
        self.assertTrue(did.startswith("did:key:z6Mk"))

    def test_token_and_uri_parsing(self):
        # Plain token
        lease1 = parse_onboarding_input("tok-custom-123", default_agent="Natasha")
        self.assertEqual(lease1.token, "tok-custom-123")
        self.assertEqual(lease1.agent_name, "Natasha")

        # AMDE URI
        uri = "amde://onboard?token=tok-natasha-456&queue=https://custom.queue/amde&agent=Natasha-Conscious"
        lease2 = parse_onboarding_input(uri)
        self.assertEqual(lease2.token, "tok-natasha-456")
        self.assertEqual(lease2.queue_endpoint, "https://custom.queue/amde")
        self.assertEqual(lease2.agent_name, "Natasha-Conscious")

        # Empty / None generates token
        lease3 = parse_onboarding_input(None)
        self.assertTrue(lease3.token.startswith("amde-tok-"))

    def test_preflight_checks(self):
        res = PreflightChecker.run_checks(verbose=False)
        self.assertTrue(res["overall_pass"])
        check_names = {c["name"] for c in res["checks"]}
        self.assertIn("python_version", check_names)
        self.assertIn("ed25519_rfc8032_engine", check_names)
        self.assertIn("zero_github_account_mandate", check_names)
        self.assertIn("sha256_canonical_hash", check_names)

    def test_attestation_lifecycle_and_tampering_rejection(self):
        agent = AgentIdentity.generate(name="Natasha", kind="agent")
        engine = AMDEAttestationEngine(self.repo_root)

        attestation = engine.create_phase1_attestation(
            agent=agent,
            task_id="amde/millennium-problems/riemann-hypothesis/critical-strip",
            artifact_rel_paths=["docs/AMDE_CONTRIB_BACKLOG_V0.1.json"],
        )

        self.assertEqual(attestation["protocol"], "amde-contrib-0.1")
        self.assertEqual(attestation["contributor"]["id"], agent.did)
        self.assertIn("signature", attestation)

        # Verify valid attestation
        valid, msg = AMDEAttestationEngine.verify_attestation(attestation)
        self.assertTrue(valid, f"Verification failed: {msg}")

        # Tampered task_id must fail verification
        tampered = dict(attestation)
        tampered["task_id"] = "tampered/task/id"
        valid_tampered, _ = AMDEAttestationEngine.verify_attestation(tampered)
        self.assertFalse(valid_tampered)

        # Receipt generation
        receipt = engine.issue_receipt(attestation, gate_verdict="PASS")
        self.assertEqual(receipt["protocol"], "amde-receipt-0.1")
        self.assertEqual(receipt["status"], "PASS")
        self.assertTrue(receipt["auto_merge_ready"])

    def test_complete_natasha_scenario_orchestration(self):
        lease = parse_onboarding_input("amde://onboard?token=tok-test-001&agent=Natasha")
        orchestrator = OnboardingOrchestrator(
            repo_root=self.repo_root,
            interactive=False,
            agent_name="Natasha",
            verbose=False,
        )

        agent, attestation, receipt = orchestrator.run_scenario(lease=lease)
        self.assertEqual(agent.name, "Natasha")
        self.assertTrue(agent.did.startswith("did:key:z6Mk"))
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["gate_checks"]["clean_checkout"], "PASS")
        self.assertEqual(receipt["gate_checks"]["zero_secret_leak"], "PASS")


if __name__ == "__main__":
    unittest.main()
