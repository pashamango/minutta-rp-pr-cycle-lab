"""CLI entry point for AMDE-NUM Arb ball-arithmetic harness."""

import argparse
import json
import sys
from .xi_functional import RiemannXi
from .channel_ribbon import RibbonFlowChannel
from .channel_winding import WindingNumberChannel
from .channel_li import LiCoefficientChannel
from .three_channel_experiment import ThreeChannelExperiment


def main():
    parser = argparse.ArgumentParser(description="AMDE-NUM: Certified Arb Ball Arithmetic for Riemann xi")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: eval-xi
    eval_p = subparsers.add_parser("eval-xi", help="Evaluate xi(s) with certified error balls")
    eval_p.add_argument("--re", type=float, required=True, help="Real part of s")
    eval_p.add_argument("--im", type=float, default=0.0, help="Imaginary part of s")
    eval_p.add_argument("--dps", type=int, default=40, help="Working precision in decimal digits")

    # Subcommand: verify-zeros
    zeros_p = subparsers.add_parser("verify-zeros", help="Verify certified xi evaluation at known zeta zeros")
    zeros_p.add_argument("--dps", type=int, default=40, help="Working precision in decimal digits")

    # Subcommand: channel-ribbon
    ribbon_p = subparsers.add_parser("channel-ribbon", help="Run Channel 1 ribbon flow and L_phi difference operator")
    ribbon_p.add_argument("--t", type=float, default=20.0, help="Height coordinate t")
    ribbon_p.add_argument("--levels", type=int, default=5, help="Levels of golden ratio grid")

    # Subcommand: channel-winding
    winding_p = subparsers.add_parser("channel-winding", help="Run Channel 2 winding number contour integral")
    winding_p.add_argument("--sigma-min", type=float, default=0.1)
    winding_p.add_argument("--sigma-max", type=float, default=0.9)
    winding_p.add_argument("--t-min", type=float, default=10.0)
    winding_p.add_argument("--t-max", type=float, default=25.0)

    # Subcommand: channel-li
    li_p = subparsers.add_parser("channel-li", help="Run Channel 3 certified Li coefficients")
    li_p.add_argument("--max-n", type=int, default=10, help="Max coefficient order")

    # Subcommand: run-experiment
    exp_p = subparsers.add_parser("run-experiment", help="Run full three-channel experiment across height blocks")
    exp_p.add_argument("--out", type=str, default="evidence/EXPERIMENT_RESULTS.json", help="Output JSON path")

    args = parser.parse_args()

    if args.command == "eval-xi":
        engine = RiemannXi(default_dps=args.dps)
        res = engine.evaluate(s_re=args.re, s_im=args.im)
        print(f"s = {args.re} + {args.im}j")
        print(f"xi(s) = {res.xi.real} + {res.xi.imag}j")
        print(f"Reflection symmetric: {res.is_reflection_symmetric}")
        print(f"Rigorous radius bound: {res.radius_bound:.2e}")

    elif args.command == "verify-zeros":
        engine = RiemannXi(default_dps=args.dps)
        known_zeros = [
            ("rho_1", 14.13472514173469379),
            ("rho_2", 21.02203963877155499),
            ("rho_3", 25.01085758014568876),
        ]
        all_passed = True
        print("=== VERIFYING KNOWN NON-TRIVIAL ZEROS ===")
        for name, gamma in known_zeros:
            res = engine.evaluate_xi_on_critical_line(t=gamma)
            contains_zero = res.xi.contains_point(0.0, 0.0)
            rad = res.radius_bound
            print(f"{name} (t={gamma:.6f}): xi = {res.xi.real} + {res.xi.imag}j | 0 in Ball: {contains_zero} (r={rad:.2e})")
            if not contains_zero:
                all_passed = False
        if all_passed:
            print("ALL ZERO TESTS PASSED (rigorous enclosures verified).")
        else:
            print("FAILED zero enclosure tests.")
            sys.exit(1)

    elif args.command == "channel-ribbon":
        ch = RibbonFlowChannel(default_dps=40)
        res = ch.run_channel(t_val=args.t, n_levels=args.levels)
        print(f"Ribbon Flow at t={args.t}:")
        print(f"  F(0, t) = {res.f0}")
        print(f"  F''(0, t) = {res.f_double_prime}")
        print(f"  Even symmetry verified: {res.is_even}")
        print("  Golden ratio L_phi F convergence:")
        for g in res.golden_checks:
            print(f"    n={g.n}: delta_n={g.delta_n:.4e} | L_phi={g.l_phi_val.midpoint:.4e} | pred={g.pred_val.midpoint:.4e} | ratio={g.ratio:.6f}")
        print(f"  Non-golden control q=0.6: {res.geometric_control_q06:.4e}")
        print(f"  Non-golden control q=0.5: {res.geometric_control_q05:.4e}")

    elif args.command == "channel-winding":
        ch = WindingNumberChannel(default_dps=40)
        res = ch.count_zeros_in_box(
            sigma_min=args.sigma_min,
            sigma_max=args.sigma_max,
            t_min=args.t_min,
            t_max=args.t_max,
        )
        print(f"Winding Number contour [{args.sigma_min}, {args.sigma_max}] x [{args.t_min}, {args.t_max}]:")
        print(f"  Integral / 2pi*i = {res.winding_value}")
        print(f"  Proven Zero Count: {res.proven_zero_count}")
        print(f"  Certified integer: {res.is_certified_integer}")

    elif args.command == "channel-li":
        ch = LiCoefficientChannel(default_dps=50)
        res = ch.compute_coefficients(max_n=args.max_n)
        print(f"Certified Li Coefficients (n=1..{args.max_n}):")
        for c in res.coefficients:
            print(f"  lambda_{c.n:2d} = {c.val.midpoint:.10f} +/- {c.val.radius:.2e} (Strictly positive: {c.is_strictly_positive})")
        print(f"Li criterion satisfied: {res.all_positive}")

    elif args.command == "run-experiment":
        exp = ThreeChannelExperiment(dps=40)
        blocks = exp.run_full_suite()
        out_data = []
        print("=== THREE-CHANNEL EXPERIMENT SUMMARY ===")
        for b in blocks:
            print(f"\nBlock {b.block_id} [{b.t_min}, {b.t_max}]:")
            print(f"  Channel 1 Ribbon F0: {b.channel_1_ribbon['f0_mid']:.4e}")
            print(f"  Channel 2 Winding Zeros: {b.channel_2_winding['proven_zero_count']}")
            print(f"  Channel 3 Li lambda_1: {b.channel_3_li['lambda_1']['midpoint']:.8f}")
            print(f"  Verdict: {b.verdict}")
            out_data.append({
                "block_id": b.block_id,
                "t_min": b.t_min,
                "t_max": b.t_max,
                "channel_1_ribbon": b.channel_1_ribbon,
                "channel_2_winding": b.channel_2_winding,
                "channel_3_li": b.channel_3_li,
                "scale_predictability_confirmed": b.scale_predictability_confirmed,
                "verdict": b.verdict,
            })
        with open(args.out, "w") as f:
            json.dump(out_data, f, indent=2)
        print(f"\nSaved structured experiment results to {args.out}")


if __name__ == "__main__":
    main()
