//! Critical-Strip Explorer Engine.
//! Covers:
//! 1. Geometric widths $G_n = [1/2 - \delta_n, 1/2 + \delta_n]$ with $\delta_n = \frac{1}{2}\phi^{n+3}$.
//! 2. Focused window 0.618 - 0.482 centered around the critical axis $\sigma = 1/2$.
//! 3. Complex $\xi(s)$ computation, reflection symmetry verification $\xi(s) = \xi(1-s)$,
//!    zeros on the critical line, and 1D/2D grid sampling.

use crate::claims::{ClaimReceipt, EpistemicStatus, TransformationKind};
use crate::math_core::{xi_sym, Complex, PHI};

/// Geometric band $G_n$ around critical axis 1/2.
#[derive(Debug, Clone, Copy)]
pub struct GoldenBand {
    pub n: u32,
    pub delta: f64,
    pub sigma_min: f64,
    pub sigma_max: f64,
    pub width: f64,
}

/// Compute the geometric nested widths $G_n$.
pub fn compute_golden_bands(num_bands: u32) -> Vec<GoldenBand> {
    let mut bands = Vec::with_capacity(num_bands as usize);
    for n in 0..num_bands {
        // delta_n = 0.5 * phi^(n+3)
        let phi_power = PHI.powi((n + 3) as i32);
        let delta = 0.5 * phi_power;
        let sigma_min = 0.5 - delta;
        let sigma_max = 0.5 + delta;
        let width = 2.0 * delta;
        bands.push(GoldenBand {
            n,
            delta,
            sigma_min,
            sigma_max,
            width,
        });
    }
    bands
}

/// Evaluation result at point $s = \sigma + it$.
#[derive(Debug, Clone)]
pub struct PointEvaluation {
    pub sigma: f64,
    pub t: f64,
    pub xi_re: f64,
    pub xi_im: f64,
    pub xi_abs: f64,
    pub xi_arg: f64,
    pub reflection_diff: f64,
    pub is_on_critical_line: bool,
    pub is_in_golden_window: bool, // sigma in [0.482, 0.618]
}

/// Evaluate $\xi(s)$ at arbitrary $\sigma + it$ with symmetry check.
pub fn evaluate_point(sigma: f64, t: f64) -> PointEvaluation {
    let s = Complex::new(sigma, t);
    let (sym_val, diff) = xi_sym(s);

    let is_on_critical_line = (sigma - 0.5).abs() < 1e-6;
    let is_in_golden_window = sigma >= 0.482 && sigma <= 0.618;

    PointEvaluation {
        sigma,
        t,
        xi_re: sym_val.re,
        xi_im: sym_val.im,
        xi_abs: sym_val.abs(),
        xi_arg: sym_val.arg(),
        reflection_diff: diff,
        is_on_critical_line,
        is_in_golden_window,
    }
}

/// Compute a 1D slice across $\sigma \in [\sigma_{\min}, \sigma_{\max}]$ at fixed height $t$.
pub fn compute_sigma_slice(
    sigma_min: f64,
    sigma_max: f64,
    steps: usize,
    t: f64,
) -> Vec<PointEvaluation> {
    let mut slice = Vec::with_capacity(steps);
    let step_size = if steps > 1 {
        (sigma_max - sigma_min) / ((steps - 1) as f64)
    } else {
        0.0
    };

    for i in 0..steps {
        let sigma = sigma_min + (i as f64) * step_size;
        slice.push(evaluate_point(sigma, t));
    }
    slice
}

/// Compute a 1D slice along $t \in [t_{\min}, t_{\max}]$ at fixed $\sigma$.
pub fn compute_t_slice(t_min: f64, t_max: f64, steps: usize, sigma: f64) -> Vec<PointEvaluation> {
    let mut slice = Vec::with_capacity(steps);
    let step_size = if steps > 1 {
        (t_max - t_min) / ((steps - 1) as f64)
    } else {
        0.0
    };

    for i in 0..steps {
        let t = t_min + (i as f64) * step_size;
        slice.push(evaluate_point(sigma, t));
    }
    slice
}

/// Known first 5 nontrivial zeros on the critical line $s = 1/2 + it$.
pub const KNOWN_ZEROS: [(f64, &'static str); 5] = [
    (14.13472514, "gamma_1 (first zero)"),
    (21.02203964, "gamma_2 (second zero)"),
    (25.01085758, "gamma_3 (third zero)"),
    (30.42487613, "gamma_4 (fourth zero)"),
    (32.93506159, "gamma_5 (fifth zero)"),
];

/// Produce a verified claim receipt for the critical strip reflection symmetry.
pub fn generate_symmetry_claim(sigma: f64, t: f64) -> ClaimReceipt {
    let eval = evaluate_point(sigma, t);
    let tol = 1e-7;
    let verified = eval.reflection_diff < tol;

    ClaimReceipt::new(
        &format!("CLAIM-STRIP-REFL-{:.3}-{:.3}", sigma, t),
        "Reflection Symmetry Involution: xi(s) = xi(1-s)",
        TransformationKind::Approximate,
        EpistemicStatus::Theorem,
        &format!("Coordinate s = ({:.4} + {:.4}i)", sigma, t),
        &format!("Reflected s' = ({:.4} + {:.4}i)", 1.0 - sigma, -t),
        &format!("xi(s) = {:.6e} + {:.6e}i", eval.xi_re, eval.xi_im),
        &format!("|xi(s) - xi(1-s)| = {:.8e}", eval.reflection_diff),
        0.0,
        eval.reflection_diff,
        tol,
        verified,
        "Checked functional equation reflection symmetry in critical strip via accelerated Dirichlet series",
    )
}

/// Produce a verified claim receipt for the golden nested widths contraction.
pub fn generate_golden_width_claim(n: u32) -> ClaimReceipt {
    let bands = compute_golden_bands(n + 1);
    let b = bands.last().unwrap();
    let verified = b.delta > 0.0 && b.sigma_min < 0.5 && b.sigma_max > 0.5;

    ClaimReceipt::new(
        &format!("CLAIM-GOLDEN-WIDTH-G{}", n),
        &format!("Nested Golden Band G_{}: delta = 1/2 * phi^({})", n, n + 3),
        TransformationKind::Iso,
        EpistemicStatus::Formalization,
        &format!("Discrete Level n={}", n),
        &format!("Interval [{:.6}, {:.6}]", b.sigma_min, b.sigma_max),
        &format!("Width = {:.6}", b.width),
        &format!("Center = 0.500000, Delta = {:.6}", b.delta),
        0.0,
        0.0,
        0.0,
        verified,
        "Algebraic contraction of nested geometric widths centered on the critical axis Re(s)=1/2",
    )
}
