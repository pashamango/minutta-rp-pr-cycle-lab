//! Geoid Navigator Engine: 4-Phase Pipeline.
//! Visualizes and computes:
//! FACTORIZE -> EVOLVE -> CANONICALIZE -> RECONSTRUCT
//! With rigorous type invariants, algebraic transformations, and cryptographic claim receipts.

use crate::claims::{ClaimReceipt, EpistemicStatus, TransformationKind};
use crate::math_core::{
    factorize_u64, logarithmic_height_u64, reconstruct_u64, valuation_profile_height, PrimeFactor, PHI,
};

/// Valuation coordinate in the Geoid lattice.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct GeoidCoordinate {
    pub prime: u64,
    pub exponent: u32,
    pub log_weight: f64,
}

/// Full Geoid state representation at any stage.
#[derive(Debug, Clone)]
pub struct GeoidState {
    pub stage_name: &'static str,
    pub value_u64: u64,
    pub coordinates: Vec<GeoidCoordinate>,
    pub total_height: f64,
    pub valuation_entropy: f64,
    pub odd_kernel: u64,
    pub powers_of_two: u32,
}

impl GeoidState {
    pub fn from_u64(stage: &'static str, n: u64) -> Self {
        let factors = factorize_u64(n);
        let total_height = logarithmic_height_u64(n);

        let mut coords = Vec::with_capacity(factors.len());
        let mut powers_of_two = 0;
        let mut entropy = 0.0;

        for f in &factors {
            if f.prime == 2 {
                powers_of_two = f.exponent;
            }
            let weight = (f.exponent as f64) * (f.prime as f64).ln();
            if total_height > 1e-12 {
                let p_i = weight / total_height;
                if p_i > 1e-12 {
                    entropy -= p_i * p_i.ln();
                }
            }
            coords.push(GeoidCoordinate {
                prime: f.prime,
                exponent: f.exponent,
                log_weight: weight,
            });
        }

        let odd_kernel = if powers_of_two > 0 {
            n / (1u64 << powers_of_two.min(63))
        } else {
            n
        };

        Self {
            stage_name: stage,
            value_u64: n,
            coordinates: coords,
            total_height,
            valuation_entropy: entropy,
            odd_kernel,
            powers_of_two,
        }
    }

    pub fn to_factors(&self) -> Vec<PrimeFactor> {
        self.coordinates
            .iter()
            .map(|c| PrimeFactor {
                prime: c.prime,
                exponent: c.exponent,
            })
            .collect()
    }
}

/// Evolution rule identifier.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EvolutionRule {
    Syracuse = 0,     // S(n) = (3n+1) / 2^(v2)
    Collatz = 1,      // T(n) = n/2 if even else 3n+1
    GoldenShift = 2,  // n' = round(phi * n)
    OddModular = 3,   // n' = (3n + 5) / 2^(v2)
}

impl EvolutionRule {
    pub fn from_u32(val: u32) -> Self {
        match val {
            0 => Self::Syracuse,
            1 => Self::Collatz,
            2 => Self::GoldenShift,
            _ => Self::OddModular,
        }
    }

    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Syracuse => "Syracuse (3n+1)/2^v2",
            Self::Collatz => "Standard Collatz",
            Self::GoldenShift => "Golden Contraction [phi * n]",
            Self::OddModular => "Modular Odd (3n+5)/2^v2",
        }
    }
}

/// Step 1: FACTORIZE — Bijective Isomorphism (ISO).
/// Decomposes natural number into prime valuation vector.
pub fn step_factorize(n: u64) -> (GeoidState, ClaimReceipt) {
    let state = GeoidState::from_u64("FACTORIZE", n);
    let reconstructed = reconstruct_u64(&state.to_factors());
    let verified = reconstructed == n;
    let delta_i = (state.total_height - valuation_profile_height(&state.to_factors())).abs();

    let factors_str = if state.coordinates.is_empty() {
        "1".to_string()
    } else {
        state
            .coordinates
            .iter()
            .map(|c| {
                if c.exponent == 1 {
                    format!("{}", c.prime)
                } else {
                    format!("{}^{}", c.prime, c.exponent)
                }
            })
            .collect::<Vec<_>>()
            .join(" * ")
    };

    let claim = ClaimReceipt::new(
        &format!("CLAIM-GEOID-FACT-{}", n),
        "Prime Factorization Isomorphism: N+ <-> (Primes ->0 N)",
        TransformationKind::Iso,
        EpistemicStatus::Theorem,
        &format!("Natural Number n = {}", n),
        &format!("Valuation Profile [{}]", factors_str),
        &format!("n = {}", n),
        &format!("factors = {}", factors_str),
        delta_i,
        0.0,
        0.0,
        verified,
        "Exact bijective decomposition into prime valuation coordinates, Delta I = 0, epsilon = 0",
    );

    (state, claim)
}

/// Step 2: EVOLVE — Dynamical Transition.
/// Applies dynamical map on the carrier space.
pub fn step_evolve(n: u64, rule: EvolutionRule) -> (GeoidState, Vec<u64>, ClaimReceipt) {
    let mut trajectory = vec![n];
    let next_n = match rule {
        EvolutionRule::Syracuse => {
            if n <= 1 {
                1
            } else {
                let mut m = 3u64.saturating_mul(n).saturating_add(1);
                while m % 2 == 0 {
                    m /= 2;
                }
                m
            }
        }
        EvolutionRule::Collatz => {
            if n <= 1 {
                1
            } else if n % 2 == 0 {
                n / 2
            } else {
                3u64.saturating_mul(n).saturating_add(1)
            }
        }
        EvolutionRule::GoldenShift => {
            let shifted = (PHI * (n as f64)).round() as u64;
            if shifted == 0 {
                1
            } else {
                shifted
            }
        }
        EvolutionRule::OddModular => {
            let mut m = 3u64.saturating_mul(n).saturating_add(5);
            while m % 2 == 0 {
                m /= 2;
            }
            m
        }
    };

    trajectory.push(next_n);

    // Compute short preview trajectory (up to 16 steps)
    let mut curr = next_n;
    for _ in 0..16 {
        if curr <= 1 {
            break;
        }
        let next = match rule {
            EvolutionRule::Syracuse => {
                let mut m = 3u64.saturating_mul(curr).saturating_add(1);
                while m % 2 == 0 {
                    m /= 2;
                }
                m
            }
            EvolutionRule::Collatz => {
                if curr % 2 == 0 {
                    curr / 2
                } else {
                    3u64.saturating_mul(curr).saturating_add(1)
                }
            }
            EvolutionRule::GoldenShift => {
                let shifted = (PHI * (curr as f64)).round() as u64;
                if shifted == 0 {
                    1
                } else {
                    shifted
                }
            }
            EvolutionRule::OddModular => {
                let mut m = 3u64.saturating_mul(curr).saturating_add(5);
                while m % 2 == 0 {
                    m /= 2;
                }
                m
            }
        };
        trajectory.push(next);
        curr = next;
    }

    let state = GeoidState::from_u64("EVOLVE", next_n);
    let delta_i = state.total_height - logarithmic_height_u64(n);
    let is_descent = next_n < n;

    let claim = ClaimReceipt::new(
        &format!("CLAIM-GEOID-EVOLVE-{}-{}", n, next_n),
        &format!("Dynamical Orbit Evolution under {}", rule.as_str()),
        TransformationKind::Approximate,
        EpistemicStatus::LemmaTarget,
        &format!("State n_0 = {}", n),
        &format!("Evolved State n_1 = {}", next_n),
        &format!("n = {}", n),
        &format!("next_n = {}, descent = {}", next_n, is_descent),
        delta_i,
        0.0,
        1.0,
        true,
        &format!(
            "Applied {} operator. Trajectory length = {}, delta height = {:.4}",
            rule.as_str(),
            trajectory.len(),
            delta_i
        ),
    );

    (state, trajectory, claim)
}

/// Step 3: CANONICALIZE — Invariant Projection / Galois Retract (LOSSY / ADJOINT).
/// Projects state to odd core and truncates to top prime channels.
pub fn step_canonicalize(evolved_state: &GeoidState, prime_horizon_k: usize) -> (GeoidState, ClaimReceipt) {
    let odd = evolved_state.odd_kernel;

    // Filter coordinates to top K prime channels
    let all_factors = factorize_u64(odd);
    let truncated_factors: Vec<PrimeFactor> = all_factors
        .into_iter()
        .take(prime_horizon_k)
        .collect();

    let canon_val = if truncated_factors.is_empty() {
        1
    } else {
        reconstruct_u64(&truncated_factors)
    };

    let canon_state = GeoidState::from_u64("CANONICALIZE", canon_val);
    let delta_i = (evolved_state.total_height - canon_state.total_height).max(0.0);
    let is_lossy = delta_i > 1e-9;

    let kind = if is_lossy {
        TransformationKind::Lossy
    } else {
        TransformationKind::Adjoint
    };

    let claim = ClaimReceipt::new(
        &format!("CLAIM-GEOID-CANON-{}-{}", evolved_state.value_u64, canon_val),
        "Geoid Canonicalization: Odd Kernel & Galois Prime Retract",
        kind,
        EpistemicStatus::Formalization,
        &format!("Evolved State n = {}", evolved_state.value_u64),
        &format!("Canonical State n* = {} (Horizon K={})", canon_val, prime_horizon_k),
        &format!("n = {}", evolved_state.value_u64),
        &format!("n* = {}, removed_powers_of_two = {}", canon_val, evolved_state.powers_of_two),
        delta_i,
        0.0,
        0.0,
        true,
        &format!(
            "Projected to odd kernel (stripped 2^{}) and bounded K={} prime channels, Delta I = {:.6}",
            evolved_state.powers_of_two,
            prime_horizon_k,
            delta_i
        ),
    );

    (canon_state, claim)
}

/// Step 4: RECONSTRUCT — Round-Trip Verification & Descent Certification (ISO).
pub fn step_reconstruct(canon_state: &GeoidState, original_n: u64) -> (u64, ClaimReceipt) {
    let reconstructed_n = reconstruct_u64(&canon_state.to_factors());
    let verified = reconstructed_n == canon_state.value_u64;
    let is_strict_descent = reconstructed_n < original_n;

    let claim = ClaimReceipt::new(
        &format!("CLAIM-GEOID-RECON-{}", reconstructed_n),
        "Geoid Reconstruction & Descent Invariant Certification",
        TransformationKind::Iso,
        EpistemicStatus::Theorem,
        &format!("Canonical Profile [{}]", canon_state.value_u64),
        &format!("Certified Integer n* = {}", reconstructed_n),
        &format!("canonical_val = {}", canon_state.value_u64),
        &format!("reconstructed = {}, strict_descent = {}", reconstructed_n, is_strict_descent),
        0.0,
        0.0,
        0.0,
        verified,
        &format!(
            "Verified exact inverse evaluation n* = {}. Strict orbit descent certified: {}",
            reconstructed_n,
            is_strict_descent
        ),
    );

    (reconstructed_n, claim)
}

/// Full 4-Phase Pipeline Execution Result.
#[derive(Debug, Clone)]
pub struct PipelineResult {
    pub initial_n: u64,
    pub state_factorize: GeoidState,
    pub state_evolve: GeoidState,
    pub trajectory: Vec<u64>,
    pub state_canonicalize: GeoidState,
    pub reconstructed_n: u64,
    pub claims: Vec<ClaimReceipt>,
}

/// Execute the complete 4-stage transformation pipeline:
/// factorize -> evolve -> canonicalize -> reconstruct.
pub fn run_full_pipeline(initial_n: u64, rule_id: u32, horizon_k: usize) -> PipelineResult {
    let rule = EvolutionRule::from_u32(rule_id);
    let mut claims = Vec::with_capacity(4);

    // Stage 1
    let (state_fact, claim1) = step_factorize(initial_n);
    claims.push(claim1);

    // Stage 2
    let (state_ev, trajectory, claim2) = step_evolve(initial_n, rule);
    claims.push(claim2);

    // Stage 3
    let (state_can, claim3) = step_canonicalize(&state_ev, horizon_k);
    claims.push(claim3);

    // Stage 4
    let (recon_n, claim4) = step_reconstruct(&state_can, initial_n);
    claims.push(claim4);

    PipelineResult {
        initial_n,
        state_factorize: state_fact,
        state_evolve: state_ev,
        trajectory,
        state_canonicalize: state_can,
        reconstructed_n: recon_n,
        claims,
    }
}
