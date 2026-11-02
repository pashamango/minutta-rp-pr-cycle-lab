# AMDE demo: WASM pipeline + critical-strip explorer

Open [`demo/index.html`](demo/index.html) directly in a browser (`file://`). It has no server, CDN, module import, or network dependency. The slider exposes the bounded window `0.482 ≤ Re(s) ≤ 0.618`; the navigator runs `factorize → evolve → canonicalize → reconstruct` and checks the exact `ISO` round-trip.

## WASM boundary

The page currently uses a dependency-free JavaScript reference so the acceptance path works offline. The matching Rust/WASM source lives in [`crate/src/lib.rs`](crate/src/lib.rs) and exposes the same typed operations:

```text
factorize(u64) -> ValuationProfile
evolve(ValuationProfile) -> ValuationProfile
canonicalize(ValuationProfile) -> CanonicalProfile
reconstruct(CanonicalProfile) -> u64
```

Build the library when Rust and the WebAssembly target are installed:

```sh
rustup target add wasm32-unknown-unknown
cargo test --manifest-path crate/Cargo.toml
cargo build --manifest-path crate/Cargo.toml --target wasm32-unknown-unknown --release
```

The checked-in demo remains serverless and has no generated binary or runtime dependency. The strip explorer is a bounded predicate, not an unbounded analytic proof.

## Check

```sh
python3 - <<'PY'
from pathlib import Path
assert 'app.js' in Path('demo/index.html').read_text()
assert 'factorize' in Path('demo/app.js').read_text()
print('static asset references: PASS')
PY
```

The JavaScript reference is intentionally kept as the browser fallback: this makes `file://demo/index.html` usable without a server, CDN, module import, or WASM loader.
