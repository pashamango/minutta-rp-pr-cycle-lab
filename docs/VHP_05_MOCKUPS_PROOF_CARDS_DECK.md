# VHP-05 — Mockups, Interactive Proof Cards, Deck, and Demo Script

**Ticket:** MIN-63  
**Product:** WheelCore  
**Status:** Builder handoff; independent QA required

## Outcome

This package turns the WheelCore proof story into a demo-ready surface: a browser mockup, a machine-readable EA-001 proof card with an interactive state model, a five-slide narrative, and a timed 90-second MVP script.

## Artifact map

| Artifact | Purpose |
|---|---|
| `mockups/vhp-05-proof-console.html` | Self-contained clickable proof-console mockup. The tabs and “Replay proof” control work without a server. |
| `proof-cards/ea-001-wheelcore-card.json` | EA-001 interactive proof-card contract: claim, witness, steps, replay action, and boundary. |
| `deck/vhp-05-5-slide-deck.md` | Slide-by-slide copy, visual direction, and presenter cue. |
| `demo/vhp-05-90s-mvp-script.md` | Timestamped narration and interaction cues totaling 90 seconds. |

## Design contract

- The product promise is “singularities become inspectable values,” not “all arithmetic is classical.”
- Every proof card separates `claim`, `witness`, `steps`, and `boundary` so the demo cannot hide a counterexample.
- The mockup is intentionally static and local: no network calls, credentials, or unverifiable live telemetry.
- Numbers in the UI are scoped to the representative seven-element domain and the eight wheel-property audit described by VHP-01/VHP-02.

## Checks

```bash
python3 -m json.tool proof-cards/ea-001-wheelcore-card.json >/dev/null
python3 - <<'PY'
from pathlib import Path
html = Path('mockups/vhp-05-proof-console.html').read_text()
assert 'Replay proof' in html and 'EA-001' in html
assert html.count('<button') >= 3
assert 'id="reset"' in html
script = Path('demo/vhp-05-90s-mvp-script.md').read_text()
assert '90 seconds' in script
print('VHP-05 artifact smoke checks: PASS')
PY
```

## Limitations

This is a presentation/MVP package, not a production proof runner. The replay button demonstrates the intended interaction and renders the recorded EA-001 steps; it does not execute a theorem prover or claim new mathematical evidence.
