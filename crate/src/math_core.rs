//! AMDE Core Math Engine: Complex Arithmetic, Special Functions (Zeta, Xi, Gamma),
//! Prime Factorization, and Pure-Rust SHA-256 for Cryptographic Receipts.

use std::f64::consts::PI;

pub const PHI: f64 = 0.61803398874989484820; // (sqrt(5) - 1) / 2
pub const PHI_SQ: f64 = 0.38196601125010515180; // 1 - PHI = PHI^2

/// Complex number representation.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Complex {
    pub re: f64,
    pub im: f64,
}

impl Complex {
    pub const fn new(re: f64, im: f64) -> Self {
        Self { re, im }
    }

    pub const fn zero() -> Self {
        Self { re: 0.0, im: 0.0 }
    }

    pub const fn one() -> Self {
        Self { re: 1.0, im: 0.0 }
    }

    pub const fn i() -> Self {
        Self { re: 0.0, im: 1.0 }
    }

    pub fn abs_sq(self) -> f64 {
        self.re * self.re + self.im * self.im
    }

    pub fn abs(self) -> f64 {
        self.abs_sq().sqrt()
    }

    pub fn arg(self) -> f64 {
        self.im.atan2(self.re)
    }

    pub fn conj(self) -> Self {
        Self {
            re: self.re,
            im: -self.im,
        }
    }

    pub fn add(self, other: Self) -> Self {
        Self {
            re: self.re + other.re,
            im: self.im + other.im,
        }
    }

    pub fn sub(self, other: Self) -> Self {
        Self {
            re: self.re - other.re,
            im: self.im - other.im,
        }
    }

    pub fn mul(self, other: Self) -> Self {
        Self {
            re: self.re * other.re - self.im * other.im,
            im: self.re * other.im + self.im * other.re,
        }
    }

    pub fn scale(self, k: f64) -> Self {
        Self {
            re: self.re * k,
            im: self.im * k,
        }
    }

    pub fn div(self, other: Self) -> Self {
        let d = other.abs_sq();
        if d == 0.0 {
            Self {
                re: f64::NAN,
                im: f64::NAN,
            }
        } else {
            Self {
                re: (self.re * other.re + self.im * other.im) / d,
                im: (self.im * other.re - self.re * other.im) / d,
            }
        }
    }

    pub fn exp(self) -> Self {
        let r = self.re.exp();
        Self {
            re: r * self.im.cos(),
            im: r * self.im.sin(),
        }
    }

    pub fn ln(self) -> Self {
        Self {
            re: self.abs().ln(),
            im: self.arg(),
        }
    }

    pub fn pow(self, p: Self) -> Self {
        if self.abs_sq() == 0.0 {
            if p.re > 0.0 {
                Self::zero()
            } else {
                Self {
                    re: f64::NAN,
                    im: f64::NAN,
                }
            }
        } else {
            (self.ln().mul(p)).exp()
        }
    }

    pub fn pow_f64(self, p: f64) -> Self {
        self.pow(Self::new(p, 0.0))
    }
}

/// Complex Gamma function using the Lanczos approximation (g=7, N=9).
pub fn gamma(z: Complex) -> Complex {
    if z.re < 0.5 {
        // Reflection formula: Gamma(z) * Gamma(1-z) = pi / sin(pi * z)
        let pi_z = z.scale(PI);
        let sin_pi_z = sin_complex(pi_z);
        let numerator = Complex::new(PI, 0.0);
        let denom = sin_pi_z.mul(gamma(Complex::one().sub(z)));
        return numerator.div(denom);
    }

    // Lanczos coefficients for g=7
    const P: [f64; 9] = [
        0.99999999999980993,
        676.5203681218851,
        -1259.1392167224028,
        771.32342877765313,
        -176.61502916214059,
        12.507343278686905,
        -0.138571095836524,
        9.9843695780195716e-6,
        1.5056327351493116e-7,
    ];

    let z_minus_1 = z.sub(Complex::one());
    let mut x = Complex::new(P[0], 0.0);
    for i in 1..9 {
        let term = Complex::new(P[i], 0.0).div(z_minus_1.add(Complex::new(i as f64, 0.0)));
        x = x.add(term);
    }

    let t = z_minus_1.add(Complex::new(7.5, 0.0));
    let sqrt_two_pi = (2.0 * PI).sqrt();

    let part1 = Complex::new(sqrt_two_pi, 0.0);
    let part2 = t.pow(z_minus_1.add(Complex::new(0.5, 0.0)));
    let part3 = t.scale(-1.0).exp();

    part1.mul(part2).mul(part3).mul(x)
}

fn sin_complex(z: Complex) -> Complex {
    // sin(x + iy) = sin(x)cosh(y) + i cos(x)sinh(y)
    Complex::new(
        z.re.sin() * z.im.cosh(),
        z.re.cos() * z.im.sinh(),
    )
}

/// Riemann zeta function $\zeta(s)$ via the Borwein / Cohen-Villegas-Zagier accelerated alternating series.
/// Converges rapidly in the critical strip $0 < \operatorname{Re}(s) < 1$.
pub fn zeta(s: Complex) -> Complex {
    // Check trivial pole at s = 1
    if (s.re - 1.0).abs() < 1e-12 && s.im.abs() < 1e-12 {
        return Complex::new(1e12, 0.0);
    }

    // Number of terms for 14-digit precision
    const N: usize = 18;
    let mut d = [0.0; N + 1];
    d[0] = 1.0;
    for k in 1..=N {
        let mut sum = 0.0;
        for j in 0..k {
            let mut coeff = 1.0;
            for m in 1..=j {
                coeff *= (k - m + 1) as f64 / m as f64;
            }
            sum += coeff;
        }
        d[k] = sum;
    }

    let factor = 1.0 / (2.0f64.powi(N as i32));

    // Dirichlet eta function: eta(s) = sum_{k=0}^{2N-1} (-1)^k e_k / (k+1)^s
    let mut eta = Complex::zero();
    let two_n = 2 * N;

    for k in 0..two_n {
        let sign = if k % 2 == 0 { 1.0 } else { -1.0 };
        let coeff = if k < N {
            1.0
        } else {
            let j = two_n - 1 - k;
            let mut c = 0.0;
            for m in 0..=j {
                let mut bin = 1.0;
                for p in 1..=m {
                    bin *= (N - p + 1) as f64 / p as f64;
                }
                c += bin;
            }
            c * factor
        };

        let k_plus_1 = Complex::new((k + 1) as f64, 0.0);
        let term = k_plus_1.pow(s.scale(-1.0)).scale(sign * coeff);
        eta = eta.add(term);
    }

    // Relation: zeta(s) = eta(s) / (1 - 2^{1-s})
    let one_minus_s = Complex::one().sub(s);
    let two_pow = Complex::new(2.0, 0.0).pow(one_minus_s);
    let denom = Complex::one().sub(two_pow);

    eta.div(denom)
}

/// Completed Riemann xi function:
/// $\xi(s) = \frac{1}{2} s(s-1) \pi^{-s/2} \Gamma(s/2) \zeta(s)$
/// Satisfies exact reflection symmetry: $\xi(s) = \xi(1-s)$.
pub fn xi(s: Complex) -> Complex {
    let half = Complex::new(0.5, 0.0);
    let s_minus_one = s.sub(Complex::one());
    let prefactor = half.mul(s).mul(s_minus_one); // 0.5 * s * (s - 1)

    let s_over_two = s.scale(0.5);
    let pi_c = Complex::new(PI, 0.0);
    let pi_factor = pi_c.pow(s_over_two.scale(-1.0)); // pi^(-s/2)

    let gamma_factor = gamma(s_over_two); // Gamma(s/2)
    let zeta_factor = zeta(s); // zeta(s)

    prefactor.mul(pi_factor).mul(gamma_factor).mul(zeta_factor)
}

/// Symmetrized Xi function evaluation ensuring numerical stability via:
/// $\xi_{\text{sym}}(s) = \frac{1}{2}[\xi(s) + \xi(1-s)]$.
pub fn xi_sym(s: Complex) -> (Complex, f64) {
    let val_fwd = xi(s);
    let one_minus_s = Complex::one().sub(s);
    let val_rev = xi(one_minus_s);

    let diff = val_fwd.sub(val_rev).abs();
    let avg = val_fwd.add(val_rev).scale(0.5);

    (avg, diff)
}

/// Sparse prime valuation item: $(p, v_p)$.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PrimeFactor {
    pub prime: u64,
    pub exponent: u32,
}

/// Factorize an integer $n \ge 1$ into prime components.
pub fn factorize_u64(mut n: u64) -> Vec<PrimeFactor> {
    let mut factors = Vec::new();
    if n <= 1 {
        return factors;
    }

    // Check factor 2
    let mut count2 = 0;
    while n % 2 == 0 {
        count2 += 1;
        n /= 2;
    }
    if count2 > 0 {
        factors.push(PrimeFactor {
            prime: 2,
            exponent: count2,
        });
    }

    // Check odd factors
    let mut d = 3u64;
    while d * d <= n {
        if n % d == 0 {
            let mut count = 0;
            while n % d == 0 {
                count += 1;
                n /= d;
            }
            factors.push(PrimeFactor {
                prime: d,
                exponent: count,
            });
        }
        d += 2;
    }

    if n > 1 {
        factors.push(PrimeFactor {
            prime: n,
            exponent: 1,
        });
    }

    factors
}

/// Reconstruct natural number from prime factors: $n = \prod p^{v_p}$.
pub fn reconstruct_u64(factors: &[PrimeFactor]) -> u64 {
    let mut n = 1u64;
    for f in factors {
        for _ in 0..f.exponent {
            n = n.saturating_mul(f.prime);
        }
    }
    n
}

/// Logarithmic height / information invariant $I(n) = \ln(n)$.
pub fn logarithmic_height_u64(n: u64) -> f64 {
    if n <= 1 {
        0.0
    } else {
        (n as f64).ln()
    }
}

/// Information content from valuation profile: $I(\mathbf{v}) = \sum v_p \ln(p)$.
pub fn valuation_profile_height(factors: &[PrimeFactor]) -> f64 {
    let mut sum = 0.0;
    for f in factors {
        sum += (f.exponent as f64) * (f.prime as f64).ln();
    }
    sum
}

/// Pure-Rust SHA-256 implementation (FIPS 180-4 standard).
pub struct Sha256 {
    state: [u32; 8],
    count: u64,
    buffer: [u8; 64],
}

impl Sha256 {
    pub fn new() -> Self {
        Self {
            state: [
                0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
            ],
            count: 0,
            buffer: [0u8; 64],
        }
    }

    pub fn update(&mut self, data: &[u8]) {
        for &byte in data {
            let idx = (self.count % 64) as usize;
            self.buffer[idx] = byte;
            self.count += 1;
            if (self.count % 64) == 0 {
                let buf = self.buffer;
                self.transform(&buf);
            }
        }
    }

    pub fn finalize(mut self) -> [u8; 32] {
        let bit_len = self.count * 8;
        self.update(&[0x80]);

        while (self.count % 64) != 56 {
            self.update(&[0x00]);
        }

        let len_bytes = bit_len.to_be_bytes();
        for &b in &len_bytes {
            let idx = (self.count % 64) as usize;
            self.buffer[idx] = b;
            self.count += 1;
        }
        let buf = self.buffer;
        self.transform(&buf);

        let mut digest = [0u8; 32];
        for i in 0..8 {
            let b = self.state[i].to_be_bytes();
            digest[i * 4..(i + 1) * 4].copy_from_slice(&b);
        }
        digest
    }

    pub fn digest_hex(data: &[u8]) -> String {
        let mut hasher = Self::new();
        hasher.update(data);
        let out = hasher.finalize();
        let mut s = String::with_capacity(64);
        for byte in out {
            use std::fmt::Write;
            let _ = write!(s, "{:02x}", byte);
        }
        s
    }

    fn transform(&mut self, chunk: &[u8; 64]) {
        const K: [u32; 64] = [
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
        ];

        let mut w = [0u32; 64];
        for i in 0..16 {
            w[i] = u32::from_be_bytes([
                chunk[i * 4],
                chunk[i * 4 + 1],
                chunk[i * 4 + 2],
                chunk[i * 4 + 3],
            ]);
        }

        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
        }

        let mut a = self.state[0];
        let mut b = self.state[1];
        let mut c = self.state[2];
        let mut d = self.state[3];
        let mut e = self.state[4];
        let mut f = self.state[5];
        let mut g = self.state[6];
        let mut h = self.state[7];

        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let temp1 = h.wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let temp2 = s0.wrapping_add(maj);

            h = g;
            g = f;
            f = e;
            e = d.wrapping_add(temp1);
            d = c;
            c = b;
            b = a;
            a = temp1.wrapping_add(temp2);
        }

        self.state[0] = self.state[0].wrapping_add(a);
        self.state[1] = self.state[1].wrapping_add(b);
        self.state[2] = self.state[2].wrapping_add(c);
        self.state[3] = self.state[3].wrapping_add(d);
        self.state[4] = self.state[4].wrapping_add(e);
        self.state[5] = self.state[5].wrapping_add(f);
        self.state[6] = self.state[6].wrapping_add(g);
        self.state[7] = self.state[7].wrapping_add(h);
    }
}
