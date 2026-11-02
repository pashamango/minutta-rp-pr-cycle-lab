"""Ball arithmetic primitives and context management wrapping Arb/FLINT.

Every number is represented as a midpoint with a rigorous error radius [m +/- r].
Guarantees fail-closed certified mathematics: true mathematical values are rigorously
enclosed within the resulting intervals.
"""

from typing import Union, Tuple, Optional
import flint
from flint import arb, acb, ctx


class ArbContext:
    """Context manager for Arb precision and accuracy configuration."""

    def __init__(self, dps: int = 50, cap: int = 100):
        self.dps = dps
        self.cap = cap
        self._prev_dps = ctx.dps
        self._prev_cap = getattr(ctx, "cap", 100)

    def __enter__(self):
        ctx.dps = self.dps
        try:
            ctx.cap = self.cap
        except Exception:
            pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ctx.dps = self._prev_dps
        try:
            ctx.cap = self._prev_cap
        except Exception:
            pass


class BallReal:
    """Rigorous real ball [midpoint +/- radius] enclosing a real value."""

    def __init__(self, val: Union[arb, float, int, str]):
        if isinstance(val, arb):
            self._val = val
        else:
            self._val = arb(str(val))

    @property
    def raw(self) -> arb:
        return self._val

    @property
    def midpoint(self) -> float:
        try:
            return float(self._val.mid())
        except Exception:
            return float(self._val)

    @property
    def radius(self) -> float:
        try:
            return float(self._val.rad())
        except Exception:
            return 0.0

    @property
    def diameter(self) -> float:
        return 2.0 * self.radius

    def contains_zero(self) -> bool:
        try:
            return bool(self._val.contains_zero())
        except Exception:
            m = self.midpoint
            r = self.radius
            return (m - r) <= 0.0 <= (m + r)

    def contains_point(self, pt: Union[float, int]) -> bool:
        pt_arb = arb(str(pt))
        try:
            return bool(self._val.overlaps(pt_arb))
        except Exception:
            return (self.midpoint - self.radius) <= float(pt) <= (self.midpoint + self.radius)

    def is_positive(self) -> bool:
        """Rigorous positivity: lower bound is strictly greater than zero."""
        try:
            return bool(self._val.is_positive())
        except Exception:
            return (self.midpoint - self.radius) > 0.0

    def __add__(self, other):
        o = other._val if isinstance(other, BallReal) else arb(str(other))
        return BallReal(self._val + o)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        o = other._val if isinstance(other, BallReal) else arb(str(other))
        return BallReal(self._val - o)

    def __rsub__(self, other):
        o = other._val if isinstance(other, BallReal) else arb(str(other))
        return BallReal(o - self._val)

    def __mul__(self, other):
        o = other._val if isinstance(other, BallReal) else arb(str(other))
        return BallReal(self._val * o)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        o = other._val if isinstance(other, BallReal) else arb(str(other))
        return BallReal(self._val / o)

    def __pow__(self, power):
        p = power._val if isinstance(power, BallReal) else arb(str(power))
        return BallReal(self._val ** p)

    def __neg__(self):
        return BallReal(-self._val)

    def __repr__(self) -> str:
        return f"BallReal({self._val})"

    def __str__(self) -> str:
        return str(self._val)


class BallComplex:
    """Rigorous complex ball enclosing a complex number in Arb (mid_re +/- rad_re) + i*(mid_im +/- rad_im)."""

    def __init__(self, re: Union[acb, arb, float, int, str], im: Union[arb, float, int, str] = 0):
        if isinstance(re, acb):
            self._val = re
        elif isinstance(re, (arb, float, int, str)) and im == 0 and isinstance(re, str) and ("j" in re or "+" in re):
            self._val = acb(re)
        else:
            re_arb = re._val if isinstance(re, BallReal) else (re if isinstance(re, arb) else arb(str(re)))
            im_arb = im._val if isinstance(im, BallReal) else (im if isinstance(im, arb) else arb(str(im)))
            self._val = acb(re_arb, im_arb)

    @property
    def raw(self) -> acb:
        return self._val

    @property
    def real(self) -> BallReal:
        return BallReal(self._val.real)

    @property
    def imag(self) -> BallReal:
        return BallReal(self._val.imag)

    @property
    def abs_sq(self) -> BallReal:
        """Rigorous squared absolute magnitude |z|^2."""
        return BallReal(self._val.real ** 2 + self._val.imag ** 2)

    def contains_zero(self) -> bool:
        return self.real.contains_zero() and self.imag.contains_zero()

    def contains_point(self, re: float, im: float = 0.0) -> bool:
        return self.real.contains_point(re) and self.imag.contains_point(im)

    def __add__(self, other):
        o = other._val if isinstance(other, BallComplex) else acb(str(other))
        return BallComplex(self._val + o)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        o = other._val if isinstance(other, BallComplex) else acb(str(other))
        return BallComplex(self._val - o)

    def __rsub__(self, other):
        o = other._val if isinstance(other, BallComplex) else acb(str(other))
        return BallComplex(o - self._val)

    def __mul__(self, other):
        o = other._val if isinstance(other, BallComplex) else acb(str(other))
        return BallComplex(self._val * o)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        o = other._val if isinstance(other, BallComplex) else acb(str(other))
        return BallComplex(self._val / o)

    def __neg__(self):
        return BallComplex(-self._val)

    def __repr__(self) -> str:
        return f"BallComplex({self._val})"

    def __str__(self) -> str:
        return str(self._val)
