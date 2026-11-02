# AMDE demo: WASM pipeline + critical-strip explorer

Open [`demo/index.html`](demo/index.html) directly in a browser (`file://`). It has no server, CDN, module import, or network dependency. The slider exposes the bounded window `0.482 ≤ Re(s) ≤ 0.618`; the navigator runs `factorize → evolve → canonicalize → reconstruct` and checks the exact `ISO` round-trip.

## WASM boundary

The page currently uses a dependency-free JavaScript reference so the acceptance path works offline. A Rust/WASM implementation can replace these functions without changing the UI contract:

```text
factorize(u64) -> ValuationProfile
evolve(ValuationProfile) -> ValuationProfile
canonicalize(ValuationProfile) -> CanonicalProfile
reconstruct(CanonicalProfile) -> u64
```

No generated `.wasm` binary is committed because this repository has no Rust/WASM source crate or toolchain yet. The strip explorer is a bounded predicate, not an unbounded analytic proof.

## Check

```sh
python3 - <<'PY'
from pathlib import Path
assert 'app.js' in Path('demo/index.html').read_text()
assert 'factorize' in Path('demo/app.js').read_text()
print('static asset references: PASS')
PY
```
