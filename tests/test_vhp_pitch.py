#!/usr/bin/env python3
"""
Unit tests for VHP-01 Pitch Specification & Verifier
"""

import unittest
import subprocess
import sys
import json
import hashlib
import re
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

        audited_commit = receipt.get("audited_commit") or receipt.get("commit_sha")
        res = subprocess.run(
            ["git", "show", f"{audited_commit}:pitch/vhp-01-reference-pitch.md"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True
        )
        if res.returncode == 0:
            target_sha = hashlib.sha256(res.stdout.encode("utf-8")).hexdigest()
            audited_art_sha = receipt.get("audited_tree_artifacts", {}).get("reference_pitch", {}).get("sha256")
            self.assertEqual(audited_art_sha, target_sha)

        ref_content = self.ref_pitch_path.read_text(encoding="utf-8")
        actual_sha = hashlib.sha256(ref_content.encode("utf-8")).hexdigest()
        self.assertEqual(receipt["canonical_artifacts"]["reference_pitch"]["sha256"], actual_sha)
        self.assertEqual(receipt["target_artifacts"]["reference_pitch"]["sha256"], actual_sha)
        self.assertEqual(receipt["canonical_artifacts"]["reference_pitch"]["symbol_count"], len(ref_content))

    def test_schema_validation_passes(self):
        schema_data = json.loads(self.schema_path.read_text(encoding="utf-8"))
        ref_data = json.loads(self.ref_json_path.read_text(encoding="utf-8"))
        # Verify schema conformance
        for req in schema_data.get("required", []):
            self.assertIn(req, ref_data, f"Missing required property {req}")
        self.assertEqual(ref_data["status"], "VALID")
        self.assertLessEqual(ref_data["character_count"], 1500)
        self.assertEqual(ref_data["max_allowed_symbols"], 1500)

    def test_receipt_commit_matches_head(self):
        ref_data = json.loads(self.ref_json_path.read_text(encoding="utf-8"))
        receipt_commit = ref_data.get("verification_receipt", {}).get("commit_sha")
        self.assertNotEqual(receipt_commit, "HEAD")
        self.assertTrue(bool(re.fullmatch(r"[0-9a-fA-F]{40}", receipt_commit)))

        # Compare dynamically with git rev-parse HEAD (or its audited target commit parent HEAD^)
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0, f"git rev-parse HEAD failed: {res.stderr}")
        head_sha = res.stdout.strip()

        valid_shas = {head_sha}
        res_parent = subprocess.run(
            ["git", "rev-parse", "HEAD^"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True
        )
        if res_parent.returncode == 0:
            valid_shas.add(res_parent.stdout.strip())

        self.assertIn(
            receipt_commit,
            valid_shas,
            f"Receipt commit '{receipt_commit}' must strictly match repository HEAD ({head_sha}) or audited target parent commit HEAD^"
        )

        # Check pitch_verification_receipt.json audited_commit
        receipt_data = json.loads(self.receipt_path.read_text(encoding="utf-8"))
        audited_commit = receipt_data.get("audited_commit") or receipt_data.get("commit_sha")
        self.assertEqual(
            receipt_commit,
            audited_commit,
            f"Receipt commit in reference_pitch.json '{receipt_commit}' must equal audited_commit '{audited_commit}'"
        )
        self.assertIn(
            audited_commit,
            valid_shas,
            f"Verification receipt audited commit '{audited_commit}' must match repository HEAD or target commit"
        )

        # Also check markdown receipt commit
        content = self.ref_pitch_path.read_text(encoding="utf-8")
        self.assertIn("Commit SHA:", content)
        self.assertIn(receipt_commit, content)
        self.assertNotIn("Commit SHA: HEAD", content)

    def test_receipt_commit_rejects_outdated_baseline(self):
        ref_data = json.loads(self.ref_json_path.read_text(encoding="utf-8"))
        receipt_commit = ref_data.get("verification_receipt", {}).get("commit_sha")

        import types
        from importlib.machinery import SourceFileLoader
        loader = SourceFileLoader("verify_vhp_pitch", str(self.verifier_script))
        mod = types.ModuleType(loader.name)
        loader.exec_module(mod)

        # Verify neither 511565c nor 71d6696 are accepted
        for rejected_sha in ["511565cc3c68e51ad616726579b9f613399038cd", "71d669674f9b47b7be6395913b6e5fc88edb4739"]:
            self.assertNotEqual(
                receipt_commit,
                rejected_sha,
                f"Receipt commit must not point to outdated/rejected ancestor {rejected_sha}"
            )
            ok, msg = mod.verify_receipt_commit(rejected_sha, REPO_ROOT)
            self.assertFalse(ok, f"Verifier must strictly reject outdated ancestor {rejected_sha}")
            self.assertTrue("outdated" in msg or "rejected" in msg or "does not match" in msg)

    def test_wheel_axioms_cli_check_axioms(self):
        result = subprocess.run(
            [sys.executable, str(self.verifier_script), "check-axioms"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, f"check-axioms failed: {result.stdout}\n{result.stderr}")
        self.assertIn("8/8 Carlström wheel properties verified on 7-element representative domain", result.stdout)

    def test_ast_auditor_cli_check_ast(self):
        result = subprocess.run(
            [sys.executable, str(self.verifier_script), "check-ast"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, f"check-ast failed: {result.stdout}\n{result.stderr}")
        self.assertIn("AST Audit passed", result.stdout)

    def test_wheel_axioms_covers_infinity_and_bottom(self):
        import types
        from importlib.machinery import SourceFileLoader
        loader = SourceFileLoader("verify_vhp_pitch", str(self.verifier_script))
        mod = types.ModuleType(loader.name)
        loader.exec_module(mod)

        ok, msg, count = mod.verify_wheel_axioms()
        self.assertTrue(ok)
        self.assertEqual(count, 1190, f"Expected 1,190 evaluations across 7 samples, got {count}")

    def test_audited_commit_tree_verification_passes_for_target(self):
        import types
        from importlib.machinery import SourceFileLoader
        loader = SourceFileLoader("verify_vhp_pitch", str(self.verifier_script))
        mod = types.ModuleType(loader.name)
        loader.exec_module(mod)

        receipt_data = json.loads(self.receipt_path.read_text(encoding="utf-8"))
        audited_commit = receipt_data.get("audited_commit") or receipt_data.get("commit_sha")
        ok, msg, log = mod.verify_audited_commit_tree(audited_commit, receipt_data, REPO_ROOT)
        self.assertTrue(ok, f"Audited commit tree verification failed: {msg}\nLog: {log}")
        self.assertIn("strictly verified", msg)

    def test_audited_commit_tree_rejects_71d6696_due_to_hash_mismatch_and_bypass(self):
        import types
        from importlib.machinery import SourceFileLoader
        loader = SourceFileLoader("verify_vhp_pitch", str(self.verifier_script))
        mod = types.ModuleType(loader.name)
        loader.exec_module(mod)

        receipt_data = json.loads(self.receipt_path.read_text(encoding="utf-8"))
        # Verify 71d6696 is rejected because its pitch is b556... and it is in OUTDATED_REJECTED_SHAS
        ok, msg, issues = mod.verify_audited_commit_tree("71d669674f9b47b7be6395913b6e5fc88edb4739", receipt_data, REPO_ROOT)
        self.assertFalse(ok, "Commit 71d6696 must be strictly rejected as audited target for a463... receipt")
        self.assertTrue(any("not found" in iss or "SHA-256 mismatch" in iss or "CANONICAL_TARGET_SHAS" in iss or "OUTDATED_REJECTED_SHAS" in iss or "outdated" in iss for iss in issues))

    def test_check_all_fails_when_parent_artifact_hash_mismatches_receipt(self):
        """
        Negative test required by QA:
        When immediate parent exists, but receipt specifies an artifact hash that differs
        from the actual artifact hash in the audited commit tree, check-all MUST fail.
        """
        import tempfile
        receipt_data = json.loads(self.receipt_path.read_text(encoding="utf-8"))
        mutated = json.loads(json.dumps(receipt_data))
        if "audited_tree_artifacts" in mutated:
            mutated["audited_tree_artifacts"]["reference_pitch"]["sha256"] = "0000000000000000000000000000000000000000000000000000000000000000"
        if "target_artifacts" in mutated:
            mutated["target_artifacts"]["reference_pitch"]["sha256"] = "0000000000000000000000000000000000000000000000000000000000000000"

        with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tf:
            json.dump(mutated, tf, indent=2)
            temp_receipt_path = tf.name

        try:
            res = subprocess.run(
                [sys.executable, str(self.verifier_script), "check-all", temp_receipt_path],
                capture_output=True,
                text=True
            )
            self.assertNotEqual(res.returncode, 0, "check-all must return non-zero exit code when audited artifact hash mismatches")
            self.assertIn("Tree Audit Failure", res.stdout)
            self.assertIn("SHA-256 mismatch", res.stdout)
            self.assertIn("SOME CHECKS FAILED", res.stdout)
        finally:
            Path(temp_receipt_path).unlink(missing_ok=True)

    def test_check_all_fails_when_json_commit_differs_from_audited_commit(self):
        """
        Negative test required by QA (Requirement 4):
        check-all MUST fail when commit in reference_pitch.json differs from audited_commit,
        even if it is an existing ancestor commit in git history (such as 71d6696).
        """
        import tempfile
        original_json = self.ref_json_path.read_text(encoding="utf-8")
        mutated_data = json.loads(original_json)
        # Mutate to ancestor commit 71d6696
        mutated_data["verification_receipt"]["commit_sha"] = "71d669674f9b47b7be6395913b6e5fc88edb4739"
        
        with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tf:
            json.dump(mutated_data, tf, indent=2)
            temp_json_path = tf.name

        try:
            res = subprocess.run(
                [sys.executable, str(self.verifier_script), "check-all", "--ref-json", temp_json_path],
                capture_output=True,
                text=True
            )
            self.assertNotEqual(res.returncode, 0, "check-all must fail when reference_pitch.json commit differs from audited_commit")
            self.assertIn("Receipt Commit Mismatch in reference_pitch.json", res.stdout)
            self.assertIn("SOME CHECKS FAILED", res.stdout)
        finally:
            Path(temp_json_path).unlink(missing_ok=True)

    def test_check_all_fails_when_markdown_commit_differs_from_audited_commit(self):
        """
        Negative test required by QA (Requirement 4):
        check-all MUST fail when commit in Markdown pitch differs from audited_commit,
        even if it is an existing ancestor commit in git history (such as 71d6696).
        """
        import tempfile
        original_md = self.ref_pitch_path.read_text(encoding="utf-8")
        # Replace audited commit with ancestor commit 71d6696
        mutated_md = original_md.replace("935f0251dd372d4e21cb77d26ac2ee3ff4f77d68", "71d669674f9b47b7be6395913b6e5fc88edb4739")

        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as tf:
            tf.write(mutated_md)
            temp_md_path = tf.name

        try:
            res = subprocess.run(
                [sys.executable, str(self.verifier_script), "check-all", "--ref-pitch", temp_md_path],
                capture_output=True,
                text=True
            )
            self.assertNotEqual(res.returncode, 0, "check-all must fail when markdown pitch commit differs from audited_commit")
            self.assertIn("Reference Pitch Markdown Commit Mismatch", res.stdout)
            self.assertIn("SOME CHECKS FAILED", res.stdout)
        finally:
            Path(temp_md_path).unlink(missing_ok=True)

    def test_check_all_fails_on_same_length_canonical_pitch_mutation(self):
        """
        Negative test required by QA:
        Mutates canonical pitch without changing length (1446 chars), sections,
        commit SHA or verification command (e.g. 'billions' -> 'millions').
        check-all MUST fail with non-zero exit code due to SHA-256 and content mismatch.
        """
        import tempfile
        original_md = self.ref_pitch_path.read_text(encoding="utf-8")
        mutated_md = original_md.replace("billions", "millions")
        self.assertEqual(len(mutated_md), len(original_md), "Length must remain identical for same-length test")

        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as tf:
            tf.write(mutated_md)
            temp_md_path = tf.name

        try:
            res = subprocess.run(
                [sys.executable, str(self.verifier_script), "check-all", "--ref-pitch", temp_md_path],
                capture_output=True,
                text=True
            )
            self.assertNotEqual(res.returncode, 0, "check-all must fail when canonical pitch is mutated with same length")
            self.assertIn("Canonical Pitch SHA-256 mismatch", res.stdout)
            self.assertIn("SOME CHECKS FAILED", res.stdout)
        finally:
            Path(temp_md_path).unlink(missing_ok=True)

    def test_check_all_fails_when_reference_json_sha_differs_from_pitch(self):
        """
        Negative test required by QA:
        check-all MUST fail when canonical_pitch_sha256 in reference_pitch.json
        differs from the actual canonical pitch SHA-256.
        """
        import tempfile
        original_json = self.ref_json_path.read_text(encoding="utf-8")
        mutated_data = json.loads(original_json)
        mutated_data["canonical_pitch_sha256"] = "0" * 64

        with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tf:
            json.dump(mutated_data, tf, indent=2)
            temp_json_path = tf.name

        try:
            res = subprocess.run(
                [sys.executable, str(self.verifier_script), "check-all", "--ref-json", temp_json_path],
                capture_output=True,
                text=True
            )
            self.assertNotEqual(res.returncode, 0, "check-all must fail when reference_pitch.json canonical_pitch_sha256 is tampered")
            self.assertIn("canonical_pitch_sha256 mismatch", res.stdout)
            self.assertIn("SOME CHECKS FAILED", res.stdout)
        finally:
            Path(temp_json_path).unlink(missing_ok=True)

    def test_check_all_fails_when_reference_json_hook_differs_from_pitch(self):
        """
        Negative test required by QA:
        check-all MUST fail when structured content (executive_hook) in reference_pitch.json
        differs from the canonical Markdown pitch.
        """
        import tempfile
        original_json = self.ref_json_path.read_text(encoding="utf-8")
        mutated_data = json.loads(original_json)
        mutated_data["executive_hook"] = mutated_data["executive_hook"].replace("billions", "millions")

        with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tf:
            json.dump(mutated_data, tf, indent=2)
            temp_json_path = tf.name

        try:
            res = subprocess.run(
                [sys.executable, str(self.verifier_script), "check-all", "--ref-json", temp_json_path],
                capture_output=True,
                text=True
            )
            self.assertNotEqual(res.returncode, 0, "check-all must fail when reference_pitch.json hook differs from markdown")
            self.assertIn("Executive Hook content mismatch", res.stdout)
            self.assertIn("SOME CHECKS FAILED", res.stdout)
        finally:
            Path(temp_json_path).unlink(missing_ok=True)

if __name__ == "__main__":
    unittest.main()
