"""Direct and landmark-coordinate evaluators for one accelerated Collatz step."""

from typing import NamedTuple


class CoordinateResult(NamedTuple):
    k: int
    successor: int
    landmark: int
    q: int
    correction: int


def v2(value: int) -> int:
    """Return the exponent of two in a positive integer."""
    if value <= 0:
        raise ValueError("v2 requires a positive integer")
    return (value & -value).bit_length() - 1


def direct_successor(n: int) -> tuple[int, int]:
    """Evaluate one accelerated Collatz transition directly."""
    _validate_odd_positive(n)
    w = 3 * n + 1
    k_direct = v2(w)
    return k_direct, w // (1 << k_direct)


def landmark(k: int) -> int:
    """Return L_k = (4^ceil(k/2) - 1) / 3."""
    if k < 1:
        raise ValueError("landmark index must be positive")
    r = (k + 1) // 2
    return (4**r - 1) // 3


def coordinate_successor(n: int) -> CoordinateResult:
    """Evaluate one transition using only the normative coordinate stages."""
    _validate_odd_positive(n)

    k = 1
    while (n - landmark(k)) % (1 << k) == 0:
        k += 1
    k -= 1

    landmark_k = landmark(k)
    q = (n - landmark_k) // (1 << k)
    c_k = 1 if k % 2 == 0 else 2
    m_coordinate = 3 * q + c_k
    return CoordinateResult(k, m_coordinate, landmark_k, q, c_k)


def _validate_odd_positive(n: int) -> None:
    if n <= 0 or n % 2 == 0:
        raise ValueError("input must be a positive odd integer")

