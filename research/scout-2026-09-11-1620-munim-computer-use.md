# Research Scout — Munim Computer Use MCP

Date: 2026-09-11
Verdict: `WATCH / DO NOT INSTALL ON PRIMARY HOST YET`
Candidate Issue: not created — today's opportunity backlog already has sufficient candidates; preserve as evidence for later Market Maker ranking.

## Evidence

Primary repository: https://github.com/munimtechnologies/munim-computer-use

Latest release observed: `v0.2.0`, published 2026-09-10 22:54:40Z. Release provides Developer-ID-signed macOS universal binary, Windows x64 binary, and SHA256 checksums. v0.2.0 is mainly a naming/artifact alignment release; behavior is stated unchanged from v0.1.0.

The project exposes a cross-platform MCP server for GUI/computer use. On macOS it uses Accessibility APIs and ScreenCaptureKit; the README documents accessibility-tree element IDs, background input, screenshots/zoom, application interaction, and optional control of a dedicated tab group in the user's signed-in Chrome. It advertises direct Codex registration through an MCP command. It is Apache-2.0 and can be built from source.

## Decision-relevant finding

This is unusually relevant to the current browser/Face-ID/UI-automation thread because it could replace brittle pixel-driving with semantic Accessibility element IDs while remaining model-agnostic and locally hosted.

However the capability boundary is much broader than the current sovereign-worker design: on macOS it requires Accessibility + Screen Recording, can click/type across applications, and its optional Chrome path operates inside a signed-in browser profile. Its fastest Codex configuration uses `npx -y`, which introduces first-run supply-chain fetching. The README also documents an opt-in environment flag that can permit secure-field input; it is refused by default.

Therefore this is **not** presently a safe drop-in capability for Wolfram or another primary personal host. A successful MCP handshake would not demonstrate a safe authority boundary.

## Opportunity shape

Potential capability: semantic GUI adapter for a future disposable/local worker or browser-auth experiment, exposing narrow Accessibility actions instead of unrestricted shell/browser automation.

Expected value: medium-to-high infrastructure leverage if it can be capability-narrowed; could reduce token use versus screenshot-heavy computer use and make deterministic GUI tests possible across macOS/Windows/Linux.

Time to first useful result: day once separately admitted.

Complexity/risk: medium-to-high. Main uncertainty is whether the server can be safely wrapped so the agent receives only an allowlisted app/window/action surface rather than host-wide Accessibility authority.

Smallest falsification test: in a disposable macOS user/profile or VM, build from pinned source/release checksum (not `npx -y`), disable browser tools, keep secure-field input disabled, expose one synthetic app only, and test whether OS-level/adapter-level policy can actually deny interactions outside that app. If host-wide actions remain available to the MCP client, reject it for sovereign-worker use unless a small auditable allowlist shim exists.

Expected Codex/local-compute cost: low; source review + deterministic local test, Luna/Light only if Research Market later allocates Codex.

Why now: first tagged releases landed 2026-09-05 and 2026-09-10, and the project directly targets Codex/MCP computer use at the same moment current work needs a clean browser/UI experimental substrate.

## Option-value assessment

`MEDIUM-HIGH OPTION / HOLD` — cheap to falsify and potentially useful, but the current default trust surface conflicts with `delegate capability, not the whole computer`. Preserve for later comparison against Codex Computer Use / Playwright / browser-only adapters. Do not install on primary Wolfram/Darwin merely because the tool is local or open source.

## Quota discipline

No Codex execution allocated. No model step-up. No quota counters estimated. Research-only path follows `research/quota-governor-v0.md`.