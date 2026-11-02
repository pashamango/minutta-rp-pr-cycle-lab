#!/usr/bin/env python3
"""
Unit tests for VHP-01 Pitch Specification & Verifier
"""

import unittest
import subprocess
import sys
import json
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

class TestVHPPitch(unittest.TestCase):
    def setUp(self):
        self.ref_pitch_path = REPO_ROOT / "pitch" / "vhp-01-reference-pitch.md"
        self.tmpl_pitch_path = REPO_ROOT / "pitch" / "vhp-01-pitch-template.md"
        self.verifier_script = REPO_ROOT / "tools" / "verify-vhp-pitch"
        self.receipt_path = REPO_ROOT / "pitch" / "artifacts" / "pitch_verification_receipt.json"
        self.schema_path = REPO_ROOT / "pitch" / "artifacts" / "pitch_schema.json"
        self.ref_json_path = REPO_ROOT / "pitch" / "artifacts" / "reference_pitch.json"

    def test_reference_pitch_exists_and_within_symbol_budget(self):
        self.assertTrue(self.ref_pitch_path.exists(), "Reference pitch file must exist")
        content = self.ref_pitch_path.read_text(encoding="utf-8")
        self.assertLessEqual(len(content), 1500, f"Reference pitch exceeds 1500 symbols: {len(content)}")
        self.assertGreater(len(content), 500, "Reference pitch is too short")

    def test_template_pitch_exists_and_within_symbol_budget(self):
        self.assertTrue(self.tmpl_pitch_path.exists(), "Template pitch file must exist")
        content = self.tmpl_pitch_path.read_text(encoding="utf-8")
        self.assertLessEqual(len(content), 1500, f"Template pitch exceeds 1500 symbols: {len(content)}")

    def test_mandatory_sections_present_in_reference_pitch(self):
        content = self.ref_pitch_path.read_text(encoding="utf-8")
        self.assertIn("## 1. Executive Hook", content)
        self.assertIn("## 2. Formal Breakthrough", content)
        self.assertIn("## 3. Verification Receipt", content)

    def test_mandatory_receipt_coordinates(self):
        content = self.ref_pitch_path.read_text(encoding="utf-8")
        self.assertIn("Repository:", content)
        self.assertIn("Commit SHA:", content)
        self.assertIn("Verification Command:", content)
        self.assertIn("Axiom Audit:", content)

    def test_cli_verifier_execution(self):
        result = subprocess.run(
            [sys.executable, str(self.verifier_script), "verify", str(self.ref_pitch_path)],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, f"Verifier failed: {result.stdout}\n{result.stderr}")
        self.assertIn("PASSED", result.stdout)

    def test_cli_check_all(self):
        result = subprocess.run(
            [sys.executable, str(self.verifier_script), "check-all"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, f"check-all failed: {result.stdout}\n{result.stderr}")
        self.assertIn("ALL VHP-01 CHECKS PASSED", result.stdout)

    def test_cli_rejects_oversized_pitch(self):
        import tempfile
        oversized_content = (
            "# Giant: Pitch\n\n"
            "## 1. Executive Hook\n" + ("A" * 600) + "\n\n"
            "## 2. Formal Breakthrough\n" + ("B" * 600) + "\n\n"
            "## 3. Verification Receipt\n"
            "- Repository: https://github.com/example/repo\n"
            "- Commit SHA: 1234567890abcdef\n"
            "- Verification Command: true\n" + ("C" * 300)
        )
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as tf:
            tf.write(oversized_content)
            temp_path = tf.name

        try:
            result = subprocess.run(
                [sys.executable, str(self.verifier_script), "verify", temp_path],
                capture_output=True,
                text=True
            )
            self.assertNotEqual(result.returncode, 0, "Verifier should reject >1500 chars pitch")
            self.assertIn("exceeds limit", result.stdout)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_cli_rejects_missing_mandatory_section(self):
        import tempfile
        missing_sec_content = (
            "# Incomplete: Pitch\n\n"
            "## 1. Executive Hook\nOnly hook here.\n\n"
            "## 3. Verification Receipt\n"
            "- Repository: https://github.com/example/repo\n"
            "- Commit SHA: 1234567890abcdef\n"
            "- Verification Command: true\n"
        )
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as tf:
            tf.write(missing_sec_content)
            temp_path = tf.name

        try:
            result = subprocess.run(
                [sys.executable, str(self.verifier_script), "verify", temp_path],
                capture_output=True,
                text=True
            )
            self.assertNotEqual(result.returncode, 0, "Verifier should reject missing Formal Breakthrough")
            self.assertIn("Missing mandatory section header", result.stdout)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_json_artifacts_schema_and_receipt_integrity(self):
        self.assertTrue(self.receipt_path.exists())
        self.assertTrue(self.schema_path.exists())
        self.assertTrue(self.ref_json_path.exists())

        receipt = json.loads(self.receipt_path.read_text(encoding="utf-8"))
        self.assertTrue(receipt["audit_passed"])

        ref_content = self.ref_pitch_path.read_text(encoding="utf-8")
        actual_sha = hashlib.sha256(ref_content.encode("utf-8")).hexdigest()
        self.assertEqual(receipt["target_artifacts"]["reference_pitch"]["sha256"], actual_sha)

if __name__ == "__main__":
    unittest.main()
