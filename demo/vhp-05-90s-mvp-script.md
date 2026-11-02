# VHP-05 — 90-Second MVP Demo Script

**Runtime:** 90 seconds  
**Demo surface:** `mockups/vhp-05-proof-console.html`  
**Card:** EA-001

| Time | Action | Spoken copy |
|---|---|---|
| 00–10s | Open the console | “This is WheelCore: a small arithmetic safety surface for systems that cannot afford to lose the boundary case.” |
| 10–22s | Point to the status rail | “Instead of turning division by zero into a crash or an opaque NaN, we keep the result visible as a named singular value.” |
| 22–35s | Open EA-001 | “Here is an interactive proof card. Every card has a claim, a concrete witness, replayable steps, and an explicit boundary.” |
| 35–50s | Click `Replay proof` | “The witness is one, one, and infinity. The classical form splits: two times infinity is infinity, but infinity plus infinity is bottom.” |
| 50–64s | Advance through steps | “The regularizer adds zero times infinity. That term is not noise; it exposes the singularity and brings both sides to the same recorded value.” |
| 64–76s | Show PASS and boundary | “The green result means the scoped regularized claim passes. The amber boundary says what we are not claiming: classical distributivity everywhere.” |
| 76–84s | Show next-step rail | “The MVP path is deliberately bounded: local replay, one instrumented adapter, then one measured pilot.” |
| 84–90s | Return to hero | “WheelCore does not make singularities disappear. It makes them legible, testable, and safe to discuss.” |

## Operator notes

- If the browser is not available, read the EA-001 JSON and narrate the same eight beats.
- Do not claim this mockup is a production theorem prover or a live safety deployment.
- Pause on the boundary panel; it is the trust-building moment of the demo.
