"""Deterministic verification of the landmark-coordinate evaluator."""

import ast
import inspect
import random
import textwrap
import unittest

from collatz.landmark_coordinate import coordinate_successor
from collatz.landmark_coordinate import direct_successor
from collatz.landmark_coordinate import landmark


class LandmarkCoordinateTests(unittest.TestCase):
    def assert_transition_agrees(self, n: int) -> None:
        k_direct, m_direct = direct_successor(n)
        coordinate = coordinate_successor(n)
        agrees = (k_direct, m_direct) == coordinate[:2]
        invariant_holds = 3 * n + 1 == (1 << coordinate.k) * coordinate.successor
        successor_is_odd = coordinate.successor % 2 == 1
        if not (agrees and invariant_holds and successor_is_odd):
            self.fail(
                "first mismatch: "
                f"n={n}, L_k={coordinate.landmark}, q={coordinate.q}, "
                f"c_k={coordinate.correction}, "
                f"DIRECT=({k_direct}, {m_direct}), "
                f"COORDINATE=({coordinate.k}, {coordinate.successor}), "
                f"invariant_holds={invariant_holds}, "
                f"successor_is_odd={successor_is_odd}"
            )

    def test_required_cases_then_64_bit_stretch(self) -> None:
        # A failure raises immediately, preserving the first mismatching case.
        for n in range(1, 2000, 2):
            self.assert_transition_agrees(n)

        generator = random.Random(0xC011A7)
        for _ in range(1000):
            n = generator.getrandbits(64) | 1
            self.assert_transition_agrees(n)

    def test_landmark_identity(self) -> None:
        for k in range(1, 129):
            r = (k + 1) // 2
            self.assertEqual(3 * landmark(k) + 1, 1 << (2 * r))

    def test_coordinate_implementation_is_independent(self) -> None:
        source = textwrap.dedent(inspect.getsource(coordinate_successor))
        tree = ast.parse(source)
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        allowed_calls = {"CoordinateResult", "landmark", "_validate_odd_positive"}
        self.assertTrue(allowed_calls.issuperset(calls))
        self.assertNotIn("direct_successor", calls)
        self.assertNotIn("v2", calls)

        match_loop = next(node for node in ast.walk(tree) if isinstance(node, ast.While))
        self.assertEqual(
            "(n - landmark(k)) % (1 << k) == 0", ast.unparse(match_loop.test)
        )

        assignments = {
            target.id: ast.unparse(node.value)
            for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        self.assertEqual("(n - landmark_k) // (1 << k)", assignments["q"])
        self.assertEqual("1 if k % 2 == 0 else 2", assignments["c_k"])
        self.assertEqual("3 * q + c_k", assignments["m_coordinate"])


if __name__ == "__main__":
    unittest.main()
