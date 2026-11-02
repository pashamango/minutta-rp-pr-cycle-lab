# VHP-05 — 5-Slide MVP Deck

## Slide 1 — Arithmetic should not disappear at the edge

**Headline:** Division by zero is a value boundary, not a process crash.  
**Visual:** Dark field; a red `1 / 0` crash marker transforms into a visible amber `infinity` node.  
**Presenter cue:** “Autonomous systems fail when a singularity becomes an exception, NaN, or silent corruption.”

## Slide 2 — WheelCore makes the boundary inspectable

**Headline:** Totalized arithmetic keeps `infinity` and `bottom` in the trace.  
**Visual:** Two labeled nodes joined to a normal number line; labels say “propagate” and “inspect.”  
**Presenter cue:** “WheelCore gives singular results names and rules, so downstream logic can inspect what happened.”

## Slide 3 — EA-001: the proof card users can replay

**Headline:** A claim is only useful when its witness and boundary are visible.  
**Visual:** Proof card with four columns: Claim → Witness → Steps → Boundary.  
**Presenter cue:** “This card does not hide the counterexample. It shows exactly where classical distributivity breaks and what the regularized claim restores.”

## Slide 4 — From theorem to operational safety signal

**Headline:** One receipt can travel from proof review to runtime policy.  
**Visual:** `expression` → `proof card` → `policy decision`, with a green PASS and amber REVIEW branch.  
**Presenter cue:** “The MVP is a shared vocabulary between the mathematician, the engineer, and the operator.”

## Slide 5 — The 90-second next step

**Headline:** Replay the card, connect one arithmetic boundary, measure one decision.  
**Visual:** Three milestones: local replay, instrumented adapter, bounded pilot.  
**Presenter cue:** “Today we can replay the proof locally. Next we connect one bounded adapter and measure whether the explicit signal improves recovery.”

**Closing line:** WheelCore does not promise that singularities vanish. It promises they remain legible.
