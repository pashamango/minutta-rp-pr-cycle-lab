"""
tests/test_vhp_paper.py — Unit Tests for VHP-02 Scientific Paper Suite
Part of VHP-001 / MIN-60 (Scientific Paper: Conditional Theorems, Countermodels & Axiom Ledger)
Mindrock Autonomous Network / Handoff Gate Protocol (MIN-236)
"""

import unittest
import os
import json
import importlib.util

def load_verify_module():
    cur = os.path.dirname(os.path.abspath(__file__))
    tool_path = os.path.join(os.path.dirname(cur), "tools", "verify-vhp-paper")
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("verify_vhp_paper", tool_path)
    spec = importlib.util.spec_from_loader("verify_vhp_paper", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod

class TestVHPPaperSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verify_mod = load_verify_module()
        cls.root = cls.verify_mod.find_workspace_root()
        cls.artifacts_dir = os.path.join(cls.root, "paper", "artifacts")

    def test_arxiv_template_exists_and_valid(self):
        template_path = os.path.join(self.root, "paper", "vhp-02-arxiv-template.tex")
        self.assertTrue(os.path.exists(template_path), f"Missing {template_path}")
        ok, msg = self.verify_mod.verify_latex_structure(template_path)
        self.assertTrue(ok, msg)

    def test_reference_paper_exists_and_valid(self):
        ref_path = os.path.join(self.root, "paper", "vhp-02-reference-paper.tex")
        self.assertTrue(os.path.exists(ref_path), f"Missing {ref_path}")
        ok, msg = self.verify_mod.verify_latex_structure(ref_path)
        self.assertTrue(ok, msg)

    def test_axiom_ledger_content_and_schema(self):
        ok, msg = self.verify_mod.verify_axiom_ledger(self.artifacts_dir)
        self.assertTrue(ok, msg)

        ledger_file = os.path.join(self.artifacts_dir, "axiom_ledger.json")
        with open(ledger_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data["axioms"]), 8)
        self.assertEqual(data["audit_summary"]["unreviewed_axioms"], 0)
        self.assertTrue(data["audit_summary"]["sorry_free_guarantee"])

    def test_countermodels_symbolic_engine(self):
        ok, results = self.verify_mod.verify_countermodels(self.artifacts_dir)
        self.assertTrue(ok, "Countermodel verification failed")
        self.assertEqual(len(results), 4)
        for cid, passed, detail in results:
            self.assertTrue(passed, f"Countermodel {cid} failed: {detail}")

    def test_claims_traceability_matrix(self):
        ok, msg = self.verify_mod.verify_claims_traceability(self.root)
        self.assertTrue(ok, msg)

        matrix_file = os.path.join(self.artifacts_dir, "claims_traceability_matrix.json")
        with open(matrix_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        claims = data.get("claims", [])
        self.assertGreaterEqual(len(claims), 6)
        claim_types = {c["claim_type"] for c in claims}
        self.assertIn("CONDITIONAL_THEOREM", claim_types)
        self.assertIn("COUNTERMODEL", claim_types)

    def test_full_verification_runner(self):
        code = self.verify_mod.run_full_verification()
        self.assertEqual(code, 0, "run_full_verification() should exit with code 0")

    def test_wheel_fraction_arithmetic_corner_cases(self):
        WF = self.verify_mod.WheelFraction
        zero = WF(0, 1)
        one = WF(1, 1)
        two = WF(2, 1)
        inf = WF(1, 0)
        bot = WF(0, 0)

        # Involutive reciprocal
        self.assertEqual(zero.recip(), inf)
        self.assertEqual(inf.recip(), zero)
        self.assertEqual(bot.recip(), bot)
        self.assertEqual(one.recip(), one)
        self.assertEqual(two.recip().recip(), two)

        # Singularity multiplication
        self.assertEqual(zero * inf, bot)
        self.assertEqual(bot * two, bot)
        self.assertEqual(inf * inf, inf)

        # Wheel negation: x - x = 0 * x
        self.assertEqual(two - two, zero * two)
        self.assertEqual(inf - inf, zero * inf)
        self.assertEqual(bot - bot, zero * bot)

if __name__ == "__main__":
    unittest.main()
