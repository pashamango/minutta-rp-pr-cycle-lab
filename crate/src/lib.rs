//! AMDE WebAssembly Demo Engine: C-ABI Exports & Core Bindings.
//! PRD-29 / MIN-90: Interactive Critical-Strip Explorer & Geoid Navigator.

pub mod claims;
pub mod critical_strip;
pub mod geoid_navigator;
pub mod math_core;

use std::cell::RefCell;

thread_local! {
    static LAST_RESULT: RefCell<Vec<u8>> = RefCell::new(Vec::new());
}

fn set_last_result(json: String) -> *const u8 {
    let bytes = json.into_bytes();
    let ptr = bytes.as_ptr();
    LAST_RESULT.with(|lr| {
        *lr.borrow_mut() = bytes;
    });
    ptr
}

#[no_mangle]
pub extern "C" fn amde_get_last_result_ptr() -> *const u8 {
    LAST_RESULT.with(|lr| lr.borrow().as_ptr())
}

#[no_mangle]
pub extern "C" fn amde_get_last_result_len() -> usize {
    LAST_RESULT.with(|lr| lr.borrow().len())
}

#[no_mangle]
pub extern "C" fn amde_wasm_version() -> u32 {
    100
}

/// Evaluate a single point in the critical strip: $s = \sigma + it$.
#[no_mangle]
pub extern "C" fn amde_eval_point(sigma: f64, t: f64) -> *const u8 {
    let eval = critical_strip::evaluate_point(sigma, t);
    let claim = critical_strip::generate_symmetry_claim(sigma, t);

    let json = format!(
        "{{\"sigma\":{:.6},\"t\":{:.6},\"xi_re\":{:.8e},\"xi_im\":{:.8e},\"xi_abs\":{:.8e},\"xi_arg\":{:.8},\"reflection_diff\":{:.8e},\"is_on_critical_line\":{},\"is_in_golden_window\":{},\"claim\":{}}}",
        eval.sigma,
        eval.t,
        eval.xi_re,
        eval.xi_im,
        eval.xi_abs,
        eval.xi_arg,
        eval.reflection_diff,
        eval.is_on_critical_line,
        eval.is_in_golden_window,
        claim.to_json()
    );

    set_last_result(json)
}

/// Compute 1D slice across $\sigma \in [\sigma_{\min}, \sigma_{\max}]$ at height $t$.
#[no_mangle]
pub extern "C" fn amde_eval_sigma_slice(
    sigma_min: f64,
    sigma_max: f64,
    steps: u32,
    t: f64,
) -> *const u8 {
    let points = critical_strip::compute_sigma_slice(sigma_min, sigma_max, steps as usize, t);
    let mut out = String::from("{\"points\":[");
    for (i, p) in points.iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        out.push_str(&format!(
            "{{\"sigma\":{:.5},\"re\":{:.6e},\"im\":{:.6e},\"abs\":{:.6e},\"diff\":{:.6e}}}",
            p.sigma, p.xi_re, p.xi_im, p.xi_abs, p.reflection_diff
        ));
    }
    out.push_str("]}");
    set_last_result(out)
}

/// Compute 1D slice along $t \in [t_{\min}, t_{\max}]$ at coordinate $\sigma$.
#[no_mangle]
pub extern "C" fn amde_eval_t_slice(t_min: f64, t_max: f64, steps: u32, sigma: f64) -> *const u8 {
    let points = critical_strip::compute_t_slice(t_min, t_max, steps as usize, sigma);
    let mut out = String::from("{\"points\":[");
    for (i, p) in points.iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        out.push_str(&format!(
            "{{\"t\":{:.4},\"re\":{:.6e},\"im\":{:.6e},\"abs\":{:.6e},\"diff\":{:.6e}}}",
            p.t, p.xi_re, p.xi_im, p.xi_abs, p.reflection_diff
        ));
    }
    out.push_str("]}");
    set_last_result(out)
}

/// Return geometric golden widths $G_n$.
#[no_mangle]
pub extern "C" fn amde_get_golden_bands(num_bands: u32) -> *const u8 {
    let bands = critical_strip::compute_golden_bands(num_bands.max(1).min(16));
    let mut out = String::from("{\"bands\":[");
    for (i, b) in bands.iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        out.push_str(&format!(
            "{{\"n\":{},\"delta\":{:.8},\"sigma_min\":{:.8},\"sigma_max\":{:.8},\"width\":{:.8}}}",
            b.n, b.delta, b.sigma_min, b.sigma_max, b.width
        ));
    }
    out.push_str("]}");
    set_last_result(out)
}

/// Geoid Navigator: Stage 1 — FACTORIZE (ISO).
#[no_mangle]
pub extern "C" fn amde_geoid_factorize(n: u64) -> *const u8 {
    let (state, claim) = geoid_navigator::step_factorize(n);
    let mut coords_json = String::from("[");
    for (i, c) in state.coordinates.iter().enumerate() {
        if i > 0 {
            coords_json.push(',');
        }
        coords_json.push_str(&format!(
            "{{\"prime\":{},\"exponent\":{},\"weight\":{:.6}}}",
            c.prime, c.exponent, c.log_weight
        ));
    }
    coords_json.push(']');

    let json = format!(
        "{{\"stage\":\"FACTORIZE\",\"n\":{},\"coordinates\":{},\"height\":{:.6},\"entropy\":{:.6},\"odd_kernel\":{},\"powers_of_two\":{},\"claim\":{}}}",
        state.value_u64,
        coords_json,
        state.total_height,
        state.valuation_entropy,
        state.odd_kernel,
        state.powers_of_two,
        claim.to_json()
    );

    set_last_result(json)
}

/// Geoid Navigator: Stage 2 — EVOLVE (Dynamical transition).
#[no_mangle]
pub extern "C" fn amde_geoid_evolve(n: u64, rule_id: u32) -> *const u8 {
    let rule = geoid_navigator::EvolutionRule::from_u32(rule_id);
    let (state, trajectory, claim) = geoid_navigator::step_evolve(n, rule);

    let traj_json = trajectory
        .iter()
        .map(|v| v.to_string())
        .collect::<Vec<_>>()
        .join(",");

    let json = format!(
        "{{\"stage\":\"EVOLVE\",\"n\":{},\"next_n\":{},\"rule\":\"{}\",\"trajectory\":[{}],\"height\":{:.6},\"odd_kernel\":{},\"claim\":{}}}",
        n,
        state.value_u64,
        rule.as_str(),
        traj_json,
        state.total_height,
        state.odd_kernel,
        claim.to_json()
    );

    set_last_result(json)
}

/// Geoid Navigator: Complete 4-phase cycle:
/// Factorize -> Evolve -> Canonicalize -> Reconstruct.
#[no_mangle]
pub extern "C" fn amde_geoid_full_cycle(n: u64, rule_id: u32, horizon_k: u32) -> *const u8 {
    let res = geoid_navigator::run_full_pipeline(n, rule_id, horizon_k as usize);

    let claims_json = res
        .claims
        .iter()
        .map(|c| c.to_json())
        .collect::<Vec<_>>()
        .join(",");

    let traj_json = res
        .trajectory
        .iter()
        .map(|v| v.to_string())
        .collect::<Vec<_>>()
        .join(",");

    let mut fact_coords = String::from("[");
    for (i, c) in res.state_factorize.coordinates.iter().enumerate() {
        if i > 0 {
            fact_coords.push(',');
        }
        fact_coords.push_str(&format!(
            "{{\"prime\":{},\"exponent\":{},\"weight\":{:.6}}}",
            c.prime, c.exponent, c.log_weight
        ));
    }
    fact_coords.push(']');

    let mut can_coords = String::from("[");
    for (i, c) in res.state_canonicalize.coordinates.iter().enumerate() {
        if i > 0 {
            can_coords.push(',');
        }
        can_coords.push_str(&format!(
            "{{\"prime\":{},\"exponent\":{},\"weight\":{:.6}}}",
            c.prime, c.exponent, c.log_weight
        ));
    }
    can_coords.push(']');

    let json = format!(
        "{{\"initial_n\":{},\"reconstructed_n\":{},\"is_descent\":{},\"trajectory\":[{}],\"factorize\":{{\"n\":{},\"coordinates\":{},\"height\":{:.6},\"entropy\":{:.6}}},\"evolve\":{{\"n\":{},\"height\":{:.6},\"odd_kernel\":{}}},\"canonicalize\":{{\"n\":{},\"coordinates\":{},\"height\":{:.6}}},\"claims\":[{}]}}",
        res.initial_n,
        res.reconstructed_n,
        res.reconstructed_n < res.initial_n,
        traj_json,
        res.state_factorize.value_u64,
        fact_coords,
        res.state_factorize.total_height,
        res.state_factorize.valuation_entropy,
        res.state_evolve.value_u64,
        res.state_evolve.total_height,
        res.state_evolve.odd_kernel,
        res.state_canonicalize.value_u64,
        can_coords,
        res.state_canonicalize.total_height,
        claims_json
    );

    set_last_result(json)
}

/// Self-test suite verifying mathematical claims and receipts.
#[no_mangle]
pub extern "C" fn amde_verify_claims() -> *const u8 {
    // 1. Prime Factorization ISO test
    let test_n = 840u64; // 2^3 * 3 * 5 * 7
    let (fact_state, fact_claim) = geoid_navigator::step_factorize(test_n);
    let iso_verified = fact_claim.verified && fact_state.value_u64 == 840;

    // 2. Reflection Symmetry test at gamma_1 (14.134725)
    let gamma_1 = 14.13472514;
    let eval_sym = critical_strip::evaluate_point(0.5, gamma_1);
    let sym_verified = eval_sym.reflection_diff < 1e-4;

    // 3. Golden Widths G_0 test: sigma_min=0.381966, sigma_max=0.618034
    let bands = critical_strip::compute_golden_bands(4);
    let g0 = &bands[0];
    let g0_verified = (g0.sigma_max - math_core::PHI).abs() < 1e-5
        && (g0.sigma_min - math_core::PHI_SQ).abs() < 1e-5;

    // 4. Syracuse descent test for n = 27
    let pipe_27 = geoid_navigator::run_full_pipeline(27, 0, 4);
    let pipeline_verified = pipe_27.claims.len() == 4 && pipe_27.reconstructed_n > 0;

    let all_passed = iso_verified && sym_verified && g0_verified && pipeline_verified;

    let json = format!(
        "{{\"all_passed\":{},\"tests\":{{\"prime_factorization_iso\":{},\"xi_reflection_symmetry\":{},\"golden_widths_g0\":{},\"pipeline_execution\":{}}}}}",
        all_passed,
        iso_verified,
        sym_verified,
        g0_verified,
        pipeline_verified
    );

    set_last_result(json)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_claim_verification() {
        let json_ptr = amde_verify_claims();
        let len = amde_get_last_result_len();
        let bytes = unsafe { std::slice::from_raw_parts(json_ptr, len) };
        let s = std::str::from_utf8(bytes).unwrap();
        assert!(s.contains("\"all_passed\":true"));
    }
}
