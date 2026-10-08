"""Deterministic tests for the POW-0001 counterexamples."""

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "research" / "pow_0001_attacks.py"
SPEC = importlib.util.spec_from_file_location("pow_0001_attacks", MODULE_PATH)
assert SPEC and SPEC.loader
ATTACKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ATTACKS)


class PredicateTests(unittest.TestCase):
    def test_inverse_at_consensus_widths(self):
        for k in (32, 64, 128, 256, 512):
            inverse = ATTACKS.inverse3_newton(k)
            self.assertEqual((3 * inverse) % (1 << k), 1)

    def test_exhaustive_existence_and_uniqueness_small_widths(self):
        for k in range(1, 9):
            modulus = 1 << k
            inverse = ATTACKS.inverse3_newton(k)
            for a in range(modulus):
                expected = ATTACKS.solve(a, k, inverse)
                solutions = [x for x in range(modulus) if ATTACKS.valid(a, x, k)]
                self.assertEqual(solutions, [expected])

    def test_many_templates_are_solved_without_search(self):
        k = 256
        inverse = ATTACKS.inverse3_newton(k)
        for i in range(10_000):
            a = ATTACKS.derive(b"test-template", i, k)
            self.assertTrue(ATTACKS.valid(a, ATTACKS.solve(a, k, inverse), k))


if __name__ == "__main__":
    unittest.main()
