//! Dependency-free AMDE geoid pipeline.
//!
//! The four functions are deliberately small and serialisable at the WASM
//! boundary: the browser demo can keep its offline UI while a wasm-bindgen
//! adapter (or a host embedding) calls the same typed operations.

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Factor {
    pub prime: u64,
    pub exponent: u32,
}

pub type ValuationProfile = Vec<Factor>;
pub type CanonicalProfile = Vec<Factor>;

pub fn factorize(mut n: u64) -> ValuationProfile {
    assert!(n > 0, "the geoid domain is positive integers");
    let mut factors = Vec::new();
    let mut p = 2;
    while p <= n / p {
        if n % p == 0 {
            let mut exponent = 0;
            while n % p == 0 {
                n /= p;
                exponent += 1;
            }
            factors.push(Factor { prime: p, exponent });
        }
        p = if p == 2 { 3 } else { p + 2 };
    }
    if n > 1 {
        factors.push(Factor { prime: n, exponent: 1 });
    }
    factors
}

pub fn evolve(profile: ValuationProfile) -> ValuationProfile {
    profile
}

pub fn canonicalize(mut profile: ValuationProfile) -> CanonicalProfile {
    profile.sort_by_key(|factor| factor.prime);
    profile
}

pub fn reconstruct(profile: &CanonicalProfile) -> u64 {
    profile.iter().fold(1, |value, factor| {
        value.saturating_mul(factor.prime.saturating_pow(factor.exponent))
    })
}

pub fn pipeline(n: u64) -> (ValuationProfile, ValuationProfile, CanonicalProfile, u64) {
    let factored = factorize(n);
    let evolved = evolve(factored.clone());
    let canonical = canonicalize(evolved.clone());
    let rebuilt = reconstruct(&canonical);
    (factored, evolved, canonical, rebuilt)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pipeline_round_trips_examples() {
        for n in [1, 2, 12, 840, 999_999] {
            assert_eq!(pipeline(n).3, n);
        }
    }

    #[test]
    fn canonical_profile_is_sorted() {
        let profile = vec![
            Factor { prime: 7, exponent: 1 },
            Factor { prime: 2, exponent: 3 },
        ];
        assert_eq!(canonicalize(profile)[0].prime, 2);
    }
}
