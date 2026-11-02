import unittest

from rp_pnp import DifficultyObservation, EpistemicState, TerminationState
from rp_pnp import diagonal_contradiction, estimate_difficulty

class RPPNPModelTests(unittest.TestCase):
    def test_difficulty_includes_context_cost_and_validation(self):
        observations = [DifficultyObservation(1, 5, 2, False, 1.0), DifficultyObservation(2, 5, 4, True, 0.95), DifficultyObservation(3, 1, 2, True, 0.80)]
        self.assertEqual(estimate_difficulty(observations, epsilon=0.10), 9)
    def test_unestablished_is_not_uncomputable(self):
        self.assertIsNone(estimate_difficulty([], epsilon=0.05))
    def test_timeout_is_distinct_from_nontermination(self):
        self.assertNotEqual(TerminationState.TIMEOUT_INTERRUPTED, TerminationState.UNKNOWN)
        self.assertNotEqual(EpistemicState.UNKNOWN_UNDECIDED, EpistemicState.VERIFIED_FALSE)
    def test_diagonal_boundary_rejects_both_oracle_answers(self):
        self.assertFalse(diagonal_contradiction(True))
        self.assertTrue(diagonal_contradiction(False))
    def test_epsilon_is_bounded(self):
        with self.assertRaises(ValueError):
            estimate_difficulty([], epsilon=1.1)

if __name__ == "__main__":
    unittest.main()
