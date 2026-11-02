#!/usr/bin/env python3
"""Automated acceptance verification for PRD-29 / MIN-90 interactive HTML/WASM demos."""

import json
import os
import subprocess
import sys

def run_command(cmd):
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode, res.stdout, res.stderr

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, ".."))
    demo_dir = os.path.join(root_dir, "demo")
    pkg_dir = os.path.join(demo_dir, "pkg")
    wasm_path = os.path.join(pkg_dir, "amde_demo_wasm.wasm")
    js_path = os.path.join(pkg_dir, "amde_demo_wasm.js")

    print("=== AMDE Interactive Demos Verification (PRD-29 / MIN-90) ===")
    checklist = {}

    # Check 1: Artifact existence
    print("[1/5] Checking file artifacts...")
    artifacts = [
        wasm_path,
        js_path,
        os.path.join(demo_dir, "index.html"),
        os.path.join(demo_dir, "critical_strip.html"),
        os.path.join(demo_dir, "geoid_navigator.html"),
        os.path.join(demo_dir, "style.css"),
    ]
    all_exist = True
    for a in artifacts:
        if not os.path.exists(a):
            print(f"  FAILED: Missing {a}")
            all_exist = False
        else:
            print(f"  OK: {os.path.relpath(a, root_dir)} ({os.path.getsize(a)} bytes)")
    checklist["artifacts_exist"] = "PASS" if all_exist else "FAIL"

    # Check 2: WASM compilation & size
    print("\n[2/5] Checking WASM binary properties...")
    wasm_size = os.path.getsize(wasm_path)
    if wasm_size > 0 and wasm_size < 1_000_000:
        print(f"  OK: WASM binary size is {wasm_size} bytes (efficient, < 1MB)")
        checklist["wasm_binary_size"] = "PASS"
    else:
        print(f"  FAIL: WASM binary size {wasm_size} unexpected")
        checklist["wasm_binary_size"] = "FAIL"

    # Check 3: Headless execution via Node.js
    print("\n[3/5] Testing WASM execution via Node.js...")
    node_test_code = f"""
    const engine = require('{js_path}');
    globalThis.amdeEngine.init().then(e => {{
        const tests = e.verifyClaims();
        const bands = e.getGoldenBands(4);
        const evalPt = e.evalPoint(0.5, 14.13472514);
        const fact = e.geoidFactorize(840);
        const cycle = e.geoidFullCycle(27, 0, 4);
        console.log(JSON.stringify({{ tests, bands, evalPt, fact, cycle }}));
    }}).catch(err => {{
        console.error(err);
        process.exit(1);
    }});
    """

    code, out, err = run_command(f"node -e \"{node_test_code}\"")
    if code != 0:
        print(f"  FAIL: Node.js execution failed: {err}")
        checklist["node_wasm_execution"] = "FAIL"
    else:
        res = json.loads(out.strip().split("\n")[-1])
        print(f"  OK: Self-test passed = {res['tests']['all_passed']}")
        checklist["self_test_all_passed"] = "PASS" if res['tests']['all_passed'] else "FAIL"

        # Verify Golden Bands (0.618 - 0.482 / Gn)
        g0 = res['bands']['bands'][0]
        print(f"  OK: G_0 band = [{g0['sigma_min']:.6f}, {g0['sigma_max']:.6f}] width={g0['width']:.6f}")
        bands_ok = abs(g0['sigma_max'] - 0.61803399) < 1e-4 and abs(g0['sigma_min'] - 0.38196601) < 1e-4
        checklist["golden_bands_g0"] = "PASS" if bands_ok else "FAIL"

        # Verify Critical Point evaluation & reflection symmetry
        pt = res['evalPt']
        print(f"  OK: xi(0.5, 14.135) reflection diff = {pt['reflection_diff']:.4e}, verified = {pt['claim']['verified']}")
        pt_ok = pt['reflection_diff'] < 1e-6 and pt['claim']['verified']
        checklist["reflection_symmetry"] = "PASS" if pt_ok else "FAIL"

        # Verify Geoid Factorization (ISO)
        fact_ok = res['fact']['claim']['verified'] and res['fact']['n'] == 840 and res['fact']['claim']['transformation_kind'] == "ISO"
        print(f"  OK: Factorization of 840 = {res['fact']['claim']['output']}, ISO verified = {fact_ok}")
        checklist["geoid_factorize_iso"] = "PASS" if fact_ok else "FAIL"

        # Verify Geoid Full Cycle (4 phases, 4 receipts)
        claims = res['cycle']['claims']
        cycle_ok = len(claims) == 4 and all(c['sha256'] and len(c['sha256']) == 64 for c in claims)
        print(f"  OK: Full cycle claims generated: {len(claims)}, all with valid SHA-256 receipts")
        checklist["geoid_4_phase_pipeline"] = "PASS" if cycle_ok else "FAIL"

    # Check 4: Standalone / Zero-Server capability (checks base64 payload)
    print("\n[4/5] Checking zero-server base64 loader compatibility...")
    with open(js_path, "r", encoding="utf-8") as f:
        js_src = f.read()
    if "EMBEDDED_WASM_BASE64 =" in js_src and len(js_src) > 100_000:
        print(f"  OK: amde_demo_wasm.js contains complete embedded base64 payload ({len(js_src)} bytes)")
        checklist["zero_server_offline_ready"] = "PASS"
    else:
        print(f"  FAIL: amde_demo_wasm.js missing embedded payload")
        checklist["zero_server_offline_ready"] = "FAIL"

    # Check 5: HTML files contain correct scripts and titles
    print("\n[5/5] Validating HTML structures...")
    html_ok = True
    for html_name in ["index.html", "critical_strip.html", "geoid_navigator.html"]:
        p = os.path.join(demo_dir, html_name)
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        if "pkg/amde_demo_wasm.js" not in content or "style.css" not in content:
            print(f"  FAIL: {html_name} missing script or stylesheet references")
            html_ok = False
        else:
            print(f"  OK: {html_name} properly references pkg/amde_demo_wasm.js and style.css")
    checklist["html_assets_integrity"] = "PASS" if html_ok else "FAIL"

    print("\n=== SUMMARY VERIFICATION RESULTS ===")
    all_passed = True
    for k, v in checklist.items():
        status_symbol = "[x]" if v == "PASS" else "[ ]"
        print(f"  {status_symbol} {k}: {v}")
        if v != "PASS":
            all_passed = False

    if all_passed:
        print("\n>>> ALL ACCEPTANCE CHECKS PASSED SUCCESSFULLY! <<<")
        sys.exit(0)
    else:
        print("\n>>> VERIFICATION FAILED <<<")
        sys.exit(1)

if __name__ == "__main__":
    main()
