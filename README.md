# AMDE-NUM: Arb Ball-Arithmetic Harness for $\xi(s)$

**Linear Ticket**: `MIN-88`  
**PRD Specification**: [`PRD-28`](https://linear.app/mindrock/issue/PRD-28/amde-num-certified-numerics-arb-three-channel-experiment)  
**Builder**: `agy@wolfram`  
**Reviewer**: `Muse`  

Certified numerical verification of the Riemann $\xi$ function using arbitrary-precision ball arithmetic (Arb/FLINT).

---

## Deliverables & Architecture

1. **Certified Ball Arithmetic Engine (`amde_num/`)**:
   - `ball_arithmetic.py`: ArbContext, BallReal, BallComplex wrappers.
   - `xi_functional.py`: Certified Riemann $\xi(s)$ with reflection regularized pole cancellation.
   - `channel_ribbon.py`: Channel 1 Ribbon flow $F(\delta, t)$ and golden difference operator $L_\phi F$.
   - `channel_winding.py`: Channel 2 Argument principle winding number zero counter.
   - `channel_li.py`: Channel 3 Certified Keiper-Li coefficients $\lambda_1 \dots \lambda_N$.
   - `three_channel_experiment.py`: Synthesis across height blocks.
   - `cli.py`: Unified CLI for interactive and automated verification.

2. **Automated Verification Gate (`scripts/verify_harness.py`)**:
   - Fail-closed verification running 25 unit tests, analytic checks, and component gates.

3. **Experimental Execution (`scripts/run_three_channel.py`)**:
   - Runs the three-channel experiment on standard height blocks and exports `evidence/EXPERIMENT_RESULTS.json`.

4. **Canonical Documentation (`docs/`)**:
   - `docs/AMDE_NUM_ARB_SPEC.md`: Formal specification of the Arb ball-arithmetic harness.
   - `docs/THREE_CHANNEL_EXPERIMENT_REPORT.md`: Comprehensive experimental report and honest null-result.

---

## Reproducibility & Replay

### 1. Run Complete Test Suite
```bash
python3 -m unittest discover tests
```

### 2. Run Fail-Closed Audit Gate
```bash
python3 scripts/verify_harness.py
```

### 3. Run Three-Channel Experiment
```bash
python3 scripts/run_three_channel.py
```

### 4. Verify Cryptographic Manifest
```bash
shasum -a 256 -c evidence/manifest.sha256
```
