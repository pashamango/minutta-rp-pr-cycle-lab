# PRD-28 certified numerics insight

Arb balls around sampled values do not by themselves certify a contour
integral when the implementation uses midpoint quadrature or a finite
difference derivative.  A sound winding-number claim must also bound
quadrature and truncation error (or use an interval/validated integration
method); otherwise the result is a high-precision numerical estimate with a
certified rounding enclosure, not a fully certified zero count.
