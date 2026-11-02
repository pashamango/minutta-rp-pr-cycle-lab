"""Typed boundaries for contextual difficulty; not a complexity solver."""
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

class EpistemicState(str, Enum):
    VERIFIED_TRUE = "VERIFIED_TRUE"
    VERIFIED_FALSE = "VERIFIED_FALSE"
    UNVERIFIED = "UNVERIFIED"
    UNKNOWN_UNDECIDED = "UNKNOWN_UNDECIDED"

class TerminationState(str, Enum):
    PROVEN_TERMINATES = "PROVEN_TERMINATES"
    OBSERVED_TERMINATION = "OBSERVED_TERMINATION"
    TIMEOUT_INTERRUPTED = "TIMEOUT_INTERRUPTED"
    UNKNOWN = "UNKNOWN"

@dataclass(frozen=True)
class DifficultyObservation:
    budget: int
    context_cost: int
    solver_cost: int
    validated: bool
    success_probability: float
    @property
    def total_cost(self) -> int:
        return self.context_cost + self.solver_cost

def estimate_difficulty(observations: Iterable[DifficultyObservation], epsilon: float) -> int | None:
    """Least observed validated budget; None means not established."""
    if not 0 <= epsilon <= 1:
        raise ValueError("epsilon must be between 0 and 1")
    threshold = 1.0 - epsilon
    return min((o.total_cost for o in observations if o.validated and 0 <= o.success_probability <= 1 and o.success_probability >= threshold), default=None)

def diagonal_contradiction(halts_oracle: bool) -> bool:
    """Whether one proposed total-oracle answer is contradicted diagonally."""
    return not halts_oracle
