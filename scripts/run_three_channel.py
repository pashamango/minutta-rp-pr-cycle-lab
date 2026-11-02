#!/usr/bin/env python3
"""Run the complete three-channel experiment across height blocks and export results."""

import json
import os
import sys
from amde_num.three_channel_experiment import ThreeChannelExperiment


def main():
    print("=" * 60)
    print("RUNNING THREE-CHANNEL EXPERIMENT ON HEIGHT BLOCKS (PRD-28)")
    print("=" * 60)

    # evidence directory exists
    exp = ThreeChannelExperiment(dps=40)
    blocks = exp.run_full_suite()

    results_data = []
    for b in blocks:
        print(f"\n[Block {b.block_id}] Height Window t in [{b.t_min}, {b.t_max}]:")
        print(f"  Channel 1 (Ribbon Flow):")
        print(f"    F(0, t_mid={b.channel_1_ribbon['t_mid']}) = {b.channel_1_ribbon['f0_mid']:.4e} +/- {b.channel_1_ribbon['f0_rad']:.2e}")
        print(f"    F''(0) = {b.channel_1_ribbon['f_double_prime_mid']:.4e}")
        print(f"    Golden L_phi level 1 ratio: {b.channel_1_ribbon['golden_ratio_level1']:.6f}")
        print(f"    Golden L_phi level 5 ratio: {b.channel_1_ribbon['golden_ratio_level5']:.8f}")
        print(f"  Channel 2 (Winding Number / Zero Count):")
        print(f"    Winding Integral Re: {b.channel_2_winding['winding_real']:.6f} +/- {b.channel_2_winding['winding_radius']:.2e}")
        print(f"    Certified Zero Count: {b.channel_2_winding['proven_zero_count']}")
        print(f"  Channel 3 (Li Coefficients):")
        print(f"    lambda_1: {b.channel_3_li['lambda_1']['midpoint']:.10f}")
        print(f"    All positive: {b.channel_3_li['all_positive']}")
        print(f"  Controls: height f0=[{b.controls['height_control']['t_min_f0']:.4e}, {b.controls['height_control']['t_max_f0']:.4e}], "
              f"width counts agree={b.controls['width_control']['counts_agree']}")
        print(f"  Predictive Scale Hypothesis:")
        print(f"    Verdict: {b.verdict}")

        results_data.append({
            "block_id": b.block_id,
            "t_min": b.t_min,
            "t_max": b.t_max,
            "channel_1_ribbon": b.channel_1_ribbon,
            "channel_2_winding": b.channel_2_winding,
            "channel_3_li": b.channel_3_li,
            "controls": b.controls,
            "scale_predictability_confirmed": b.scale_predictability_confirmed,
            "verdict": b.verdict,
        })

    out_path = "evidence/EXPERIMENT_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\n[SUCCESS] Wrote structured experiment results to {out_path}")


if __name__ == "__main__":
    main()
