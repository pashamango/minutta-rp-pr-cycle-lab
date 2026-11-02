#!/usr/bin/env python3
"""Fail-closed audit verification gate for AMDE-NUM Arb ball-arithmetic harness."""

import sys
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from amde_num.xi_functional import RiemannXi
from amde_num.channel_ribbon import RibbonFlowChannel
from amde_num.channel_winding import WindingNumberChannel
from amde_num.channel_li import LiCoefficientChannel


def main():
    print("=" * 60)
    print("AMDE-NUM AUDIT GATE: RIGOROUS ARB NUMERICS VERIFICATION")
    print("=" * 60)

    # 1. Run unittest test suite
    print("\n[Phase 1] Executing Automated Unit Test Suite...")
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "tests"))
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)

    if not test_result.wasSuccessful():
        print(f"\n[FAIL] Unit tests failed: {len(test_result.failures)} failures, {len(test_result.errors)} errors.")
        sys.exit(1)
    print("[PASS] All unit tests completed successfully.")

    # 2. Riemann Xi Reflection & Singularity Audit
    print("\n[Phase 2] Auditing Riemann Xi Analytic Invariants...")
    xi = RiemannXi(default_dps=50)

    # s = 0 and s = 1
    r0 = xi.evaluate(0, 0)
    r1 = xi.evaluate(1, 0)
    if not (r0.xi.real.contains_point(0.5) and r1.xi.real.contains_point(0.5)):
        print("[FAIL] xi(0) or xi(1) does not enclose 0.5")
        sys.exit(1)
    print(f"  xi(0) = {r0.xi.real} (Radius: {r0.radius_bound:.2e}) -> PASS")
    print(f"  xi(1) = {r1.xi.real} (Radius: {r1.radius_bound:.2e}) -> PASS")

    # Reflection symmetry off critical line
    s_test = (1.5, 23.5)
    r_sym = xi.evaluate(*s_test)
    if not r_sym.is_reflection_symmetric:
        print(f"[FAIL] Reflection symmetry failed at {s_test}")
        sys.exit(1)
    print(f"  xi({s_test[0]} + {s_test[1]}j) - xi(1-s) contains 0: TRUE -> PASS")

    # 3. Channel 1: Ribbon Flow & Golden Attractor Audit
    print("\n[Phase 3] Auditing Channel 1 Ribbon Flow & Golden Difference Operator (L_phi F)...")
    ribbon = RibbonFlowChannel(default_dps=40)
    r_res = ribbon.run_channel(t_val=20.0, n_levels=5)
    if not r_res.is_even:
        print("[FAIL] Even parity F(delta, t) = F(-delta, t) violated")
        sys.exit(1)
    print(f"  F(delta, t) Even Parity: TRUE (Discrepancy: {r_res.even_discrepancy.midpoint:.2e}) -> PASS")

    ratio_5 = r_res.golden_checks[-1].ratio
    if abs(ratio_5 - 1.0) > 1e-4:
        print(f"[FAIL] L_phi F ratio to 2nd derivative {ratio_5} exceeds tolerance 1e-4")
        sys.exit(1)
    print(f"  L_phi F convergence to F''(0) term (level 5 ratio): {ratio_5:.8f} -> PASS")

    # 4. Channel 2: Certified Winding Number / Zero Count
    print("\n[Phase 4] Auditing Channel 2 Certified Winding Numbers...")
    winding = WindingNumberChannel(default_dps=40)
    w_res = winding.count_zeros_in_box(sigma_min=0.1, sigma_max=0.9, t_min=10.0, t_max=18.0)
    if not w_res.is_certified_integer or w_res.proven_zero_count != 1:
        print(f"[FAIL] Expected exactly 1 zero in [10, 18], got {w_res.proven_zero_count}")
        sys.exit(1)
    print(f"  Contour [0.1, 0.9] x [10, 18]: Proven Zero Count = {w_res.proven_zero_count} (Winding: {w_res.winding_value.real.midpoint:.6f} +/- {w_res.radius_bound:.2e}) -> PASS")

    # 5. Channel 3: Certified Li Coefficients
    print("\n[Phase 5] Auditing Channel 3 Li Coefficients & Li Criterion...")
    li = LiCoefficientChannel(default_dps=50)
    li_res = li.compute_coefficients(max_n=8)
    if not li_res.all_positive:
        print("[FAIL] Li criterion positivity violated for lambda_1..lambda_8")
        sys.exit(1)
    print(f"  lambda_1 = {li_res.coefficients[0].val.midpoint:.10f} +/- {li_res.coefficients[0].val.radius:.2e} (Strictly positive: True)")
    print(f"  lambda_8 = {li_res.coefficients[-1].val.midpoint:.10f} +/- {li_res.coefficients[-1].val.radius:.2e} (Strictly positive: True)")
    print(f"  All 8 Li coefficients strictly positive: TRUE -> PASS")

    print("\n" + "=" * 60)
    print("SUCCESS: 100% AMDE-NUM VERIFICATION GATES PASSED (FAIL-CLOSED)")
    print("=" * 60)
    sys.exit(0)


if __name__ == "__main__":
    main()
