"""Unit tests for Wolfram capacity-aware profiles harness (MIN-56 / WOLFRAM_PROFILES/v1)."""

import importlib.machinery
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROFILES_TOOL = ROOT / "tools" / "wolfram-profiles"
loader = importlib.machinery.SourceFileLoader("wolfram_profiles", str(PROFILES_TOOL))
spec = importlib.util.spec_from_loader(loader.name, loader)
wolfram_profiles = importlib.util.module_from_spec(spec)
import sys
sys.modules[loader.name] = wolfram_profiles
loader.exec_module(wolfram_profiles)


class TestWolframProfilesParsing(unittest.TestCase):
    def test_parse_sysctl_memsize(self):
        output = "hw.memsize: 17179869184\n"
        self.assertEqual(wolfram_profiles.parse_sysctl_memsize(output), 17179869184)

    def test_parse_sysctl_memsize_invalid(self):
        with self.assertRaises(ValueError):
            wolfram_profiles.parse_sysctl_memsize("no numbers here")

    def test_parse_swapusage(self):
        output = "vm.swapusage: total = 14336.00M  used = 12820.06M  free = 1515.94M  (encrypted)\n"
        total, used, free = wolfram_profiles.parse_swapusage(output)
        self.assertEqual(total, 14336.00)
        self.assertEqual(used, 12820.06)
        self.assertEqual(free, 1515.94)

    def test_parse_swapusage_invalid(self):
        with self.assertRaises(ValueError):
            wolfram_profiles.parse_swapusage("invalid swap line")

    def test_parse_memory_pressure(self):
        output = "System-wide memory free percentage: 72%\n"
        self.assertEqual(wolfram_profiles.parse_memory_pressure(output), 72.0)

    def test_parse_memory_pressure_fallback(self):
        output = "Free memory: 48%"
        self.assertEqual(wolfram_profiles.parse_memory_pressure(output), 48.0)

    def test_parse_vm_stat(self):
        output = """Mach Virtual Memory Statistics: (page size of 16384 bytes)
Pages free:                                     3551.
Pages active:                                 359563.
Pages inactive:                               347547.
Pages wired down:                             136169.
Pages stored in compressor:                  1756179.
Pageins:                                   749493758.
Pageouts:                                    8470778.
Swapins:                                     4724229.
Swapouts:                                    7240895.
"""
        stats = wolfram_profiles.parse_vm_stat(output)
        self.assertEqual(stats["Pages free"], 3551)
        self.assertEqual(stats["Pages active"], 359563)
        self.assertEqual(stats["Pages wired down"], 136169)
        self.assertEqual(stats["Pages stored in compressor"], 1756179)
        self.assertEqual(stats["Pageins"], 749493758)
        self.assertEqual(stats["Pageouts"], 8470778)


class TestWolframProfilesArbitration(unittest.TestCase):
    def _create_mock_probe(
        self,
        ram_bytes: int = 17179869184,
        swap_total: float = 14336.0,
        swap_used: float = 8000.0,
        swap_free: float = 6336.0,
        mem_free_pct: float = 50.0,
    ):
        return wolfram_profiles.HostCapacityProbe(
            total_ram_bytes=ram_bytes,
            total_ram_gib=round(ram_bytes / (1024**3), 2),
            swap_total_mib=swap_total,
            swap_used_mib=swap_used,
            swap_free_mib=swap_free,
            memory_free_percent=mem_free_pct,
            page_size_bytes=16384,
            pages_free=5000,
            pages_active=300000,
            pages_inactive=300000,
            pages_wired=100000,
            pages_compressed=500000,
            pageins=100000,
            pageouts=10000,
            swapins=5000,
            swapouts=10000,
            timestamp_utc="2026-11-02T20:00:00Z",
        )

    def test_plan_guard_to_forge(self):
        probe = self._create_mock_probe(mem_free_pct=60.0, swap_used=7000.0)
        plan = wolfram_profiles.plan_profile_transition(
            target_profile="FORGE",
            current_profile="GUARD",
            probe=probe,
        )
        self.assertTrue(plan["admissible"])
        self.assertEqual(len(plan["violations"]), 0)
        self.assertIn("Local Ollama single model harness (3B-8B quantized, max_parallel=1)", plan["actions_to_start"])
        self.assertEqual(len(plan["actions_to_stop"]), 0)
        self.assertIn("token_governor", plan["protected_services_preserved"])
        self.assertIn("fleetd", plan["protected_services_preserved"])

    def test_plan_forge_to_math_mutual_exclusion(self):
        probe = self._create_mock_probe(mem_free_pct=60.0, swap_used=7000.0)
        plan = wolfram_profiles.plan_profile_transition(
            target_profile="MATH",
            current_profile="FORGE",
            probe=probe,
        )
        self.assertTrue(plan["admissible"])
        # Must stop Ollama loaded models to prevent memory collision
        self.assertIn("Local Ollama loaded generator models", plan["actions_to_stop"])
        self.assertIn("Lean4 / Rust proof check session", plan["actions_to_start"])

    def test_plan_math_to_forge_mutual_exclusion(self):
        probe = self._create_mock_probe(mem_free_pct=60.0, swap_used=7000.0)
        plan = wolfram_profiles.plan_profile_transition(
            target_profile="FORGE",
            current_profile="MATH",
            probe=probe,
        )
        self.assertTrue(plan["admissible"])
        self.assertIn("MATH formal solver / Lean4 compiler sessions", plan["actions_to_stop"])
        self.assertIn("Local Ollama single model harness (3B-8B quantized, max_parallel=1)", plan["actions_to_start"])

    def test_plan_violates_memory_pressure_threshold(self):
        # Memory free is 15%, below 25% threshold
        probe = self._create_mock_probe(mem_free_pct=15.0, swap_used=7000.0)
        plan = wolfram_profiles.plan_profile_transition(
            target_profile="FORGE",
            current_profile="GUARD",
            probe=probe,
        )
        self.assertFalse(plan["admissible"])
        self.assertTrue(any("below safe threshold" in v for v in plan["violations"]))

    def test_plan_violates_swap_ceiling_threshold(self):
        # Swap used is 14200 MiB, exceeding 14000 MiB limit
        probe = self._create_mock_probe(mem_free_pct=50.0, swap_used=14200.0)
        plan = wolfram_profiles.plan_profile_transition(
            target_profile="FORGE",
            current_profile="GUARD",
            probe=probe,
        )
        self.assertFalse(plan["admissible"])
        self.assertTrue(any("exceeds safety ceiling" in v for v in plan["violations"]))

    def test_invalid_profile(self):
        with self.assertRaises(ValueError):
            wolfram_profiles.plan_profile_transition(target_profile="INVALID")


class TestWolframProfilesEvaluation(unittest.TestCase):
    def test_falsifiable_benefit_admissible(self):
        res = wolfram_profiles.evaluate_falsifiable_benefit(
            task_id="MIN-51-FIXTURE",
            baseline_external_tokens=3500,
            local_forge_tokens_generated=1200,
            tests_passed=True,
            proof_certified=False,
            human_review_minutes=3.5,
            false_done_claims=0,
            wall_clock_seconds=42.0,
            estimated_external_savings_cents=10.5,
        )
        self.assertTrue(res["valid"])
        self.assertTrue(res["admissible_for_token_substitution"])
        self.assertEqual(res["metrics"]["net_tokens_saved_per_review_minute"], 1000.0)
        self.assertEqual(len(res["rejection_reasons"]), 0)

    def test_falsifiable_benefit_rejects_false_done(self):
        res = wolfram_profiles.evaluate_falsifiable_benefit(
            task_id="MIN-51-FIXTURE-BAD",
            baseline_external_tokens=3500,
            local_forge_tokens_generated=1200,
            tests_passed=True,
            proof_certified=False,
            human_review_minutes=3.5,
            false_done_claims=1,  # False DONE claimed!
            wall_clock_seconds=42.0,
            estimated_external_savings_cents=10.5,
        )
        self.assertFalse(res["valid"])
        self.assertFalse(res["admissible_for_token_substitution"])
        self.assertTrue(any("FALSE_DONE_DETECTED" in r for r in res["rejection_reasons"]))

    def test_falsifiable_benefit_rejects_failed_tests(self):
        res = wolfram_profiles.evaluate_falsifiable_benefit(
            task_id="MIN-51-FIXTURE-FAIL",
            baseline_external_tokens=3500,
            local_forge_tokens_generated=1200,
            tests_passed=False,  # Tests failed!
            proof_certified=False,
            human_review_minutes=3.5,
            false_done_claims=0,
            wall_clock_seconds=42.0,
            estimated_external_savings_cents=0.0,
        )
        self.assertFalse(res["valid"])
        self.assertFalse(res["admissible_for_token_substitution"])
        self.assertTrue(any("TESTS_FAILED" in r for r in res["rejection_reasons"]))


if __name__ == "__main__":
    unittest.main()
