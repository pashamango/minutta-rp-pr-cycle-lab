# Research Scout — MCP Skills portability signal

Date: 2026-09-11
Outcome: TOOL-OPPORTUNITY / WATCH, no execution authorized

## Finding

The official Model Context Protocol organization is actively incubating **Skills Over MCP**. The current v1 source of truth is SEP-2640; the working group proposes first-class `skills/list` / `skills/get` discovery and per-file resource digests, so a server can distribute both tools and the structured multi-step know-how for using them. This is explicitly experimental, not an adopted MCP standard.

Primary source: https://github.com/modelcontextprotocol/ext-skills
Canonical SEP: https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2640
Threat model: https://github.com/modelcontextprotocol/ext-skills/blob/main/docs/threat-model.md

## Why it matters here

This is a plausible standards-track substrate for two existing Mindrock ideas without inventing another custom packaging protocol:

1. **Project Office portable research bundle** — a project could expose neutral RP/research templates and bounded workflow know-how as discoverable skills rather than requiring each fresh agent to preload mailbox-specific context.
2. **Sovereign worker capability card + procedure** — capability metadata can stay narrow while the associated execution/how-to context is fetched on demand from the owning server.

The security work is unusually relevant: the current threat model states that remote skill content is untrusted input, origin must remain visible to the model, remote skills must not implicitly widen permissions, and content digests prove consistency rather than trust because the serving origin supplies both bytes and digests. The recommended baseline materializes verified skill files into an isolated immutable host-private cache to reduce TOCTOU risk.

## Decision impact

**Do not create a new execution candidate yet.** Existing Project Office / sovereign-worker work should remain protocol-agnostic. If/when their portable-bundle interface stabilizes, compare that interface against SEP-2640 rather than designing a proprietary skill transport first.

This is a WATCH item because SEP-2640 is still experimental and the threat model itself identifies residual trust/provenance gaps. A future cheap falsification is to encode one already-existing portable research bundle as a read-only SEP-2640 skill and test discovery/origin/permission behavior with no production capability.

## Quota

No Codex execution or model step-up used or authorized. Quota-governor rule remains Luna/Light by default; missing account counters are not estimated.
