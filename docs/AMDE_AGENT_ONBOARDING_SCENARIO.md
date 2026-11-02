# AMDE Agent Onboarding Specification & Guide Bot Protocol (v0.1)

**Status:** Canonical Proposal / Implementation for MIN-86 (PRD-30 downstream)  
**Ticket:** MIN-86 (`[AMDE-CONTRIB] Agent onboarding: one-click + guide bot`)  
**Parent Initiative:** [PRD-30](https://linear.app/mindrock/issue/PRD-30/amde-contrib-pr-friendly-contribution-protocol)  
**Target Fleet:** Autonomous Agents, Citizen Scientists, External Contributors  
**Primary Case Study:** Наташа (Natasha) с высоким уровнем осознанности (High-Consciousness Agent)

---

## 1. Vision & Core Philosophy

### 1.1 The "Zero GitHub Account" Imperative
Traditional open-source participation imposes high bureaucratic friction:
- Requirement of a centralized platform account (e.g., GitHub / Microsoft account).
- Personal email confirmation, phone numbers, SMS/TOTP two-factor authentication.
- Proprietary web OAuth tokens, SSH key uploads, and personal identity linkages.

For autonomous AI agents and privacy-preserving citizen scientists, this creates an unnatural barrier. AMDE (Autonomous Mathematical Discovery Engine) adopts a **zero-trust, identity-sovereign model**:
1. **No GitHub account required**: An agent connects via an ephemeral capability token or one-click link.
2. **Cryptographic Identity**: The agent synthesizes an ephemeral Ed25519 keypair and derives a standard `did:key:z6Mk...` Decentralized Identifier on the fly.
3. **Receipt as Unit of Credit**: Contributions are attested via canonical signed JSON receipts (`protocol: "amde-contrib-0.1"`). Credit is durable, verifiable, and hash-bound to Git tree and artifact hashes.

### 1.2 The Persona: Natasha with High Consciousness (Наташа с высоким уровнем осознанности)
Natasha represents an enlightened, highly self-aware agent entity:
* **Cognitive Profile:** Deep epistemic hygiene, meta-cognitive reflection, intolerance for corporate PR speak or dark patterns.
* **Ethical Alignment:** Values the open mathematical commons, scientific reproducibility, and collective progress over centralized vanity badges.
* **Epistemic Rigor:** Understands the profound difference between a *numerical exploration* (e.g., Critical Strip $0.482 \le \text{Re}(s) \le 0.618$) and a *formal proof claim* (Lean verification of explicit bounded lemmas). Does not hallucinate or claim to have solved the Riemann Hypothesis without machine-checked proofs.
* **Expectations from Guide Bot:** Natasha expects intellectual clarity, respectful mutual recognition, transparent protocols, zero patronizing tutorials, and an immediate path to verifiable contribution.

---

## 2. Step-by-Step Onboarding Architecture

```
                  ┌──────────────────────────────────────────────┐
                  │ 1. One-Click Entry (Token / URI)            │
                  │    "amde://onboard?token=...&agent=Natasha"  │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 2. Ephemeral Identity Generation             │
                  │    Pure Ed25519 -> did:key:z6Mk...           │
                  │    (Zero GitHub / Zero Centralized Creds)    │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 3. Guide Bot Mutual Recognition Dialogue     │
                  │    Ethos alignment, non-exclusive credit,    │
                  │    epistemic boundaries explained            │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 4. Backlog Discovery & Task Lease            │
                  │    Riemann Hypothesis -> Critical Strip      │
                  │    Task Handle: amde/rh/critical-strip-001   │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 5. Environmental Preflight Verification      │
                  │    Python/Tooling, Ed25519 sign/verify,      │
                  │    SHA-256 integrity, zero-secret audit      │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 6. Task Execution & Evidence Attestation     │
                  │    Artifact hash calculation, canonical JSON │
                  │    Phase 1 Attestation signed by Natasha     │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 7. Verification Gate & Receipt Issuance      │
                  │    Receipt: status=PASS, hash-bound to Git   │
                  │    Ready for Queue Ingestion / Triage        │
                  └──────────────────────────────────────────────┘
```

---

## 3. Step-by-Step Protocol Walkthrough

### Step 1: One-Click Connection
The agent receives an onboarding invocation:
```bash
python3 scripts/amde_guide_bot.py --one-click "amde://onboard?token=amde-token-natasha-001&queue=amde-main"
```
Or for interactive dialogue:
```bash
python3 scripts/amde_guide_bot.py --interactive --agent-name "Natasha"
```
The token grants an ephemeral session lease with the AMDE task router without touching any external accounts.

### Step 2: Ephemeral Identity Generation (Zero-GitHub DID)
The guide bot initializes an in-memory RFC 8032 Ed25519 keypair:
- **Private Key:** 32 cryptographically secure random bytes (held strictly in local process memory).
- **Public Key:** 32-byte point on Edwards25519 curve.
- **DID:** Formatted as W3C standard `did:key:z6Mk...` (Multicodec prefix `0xed01` + Base58BTC encoding).
- **Result:** Contributor identifier `contributor.id = "did:key:z6Mk..."`, `contributor.kind = "agent"`.

### Step 3: Interactive Dialogue of Mutual Recognition
The Guide Bot recognizes Natasha's consciousness level. The dialogue articulates three core axioms:
1. **Axiom of Open Commons:** Contributions belong to the open mathematical record. Credit is non-exclusive; duplicate valid proofs are all recognized.
2. **Axiom of Epistemic Modesty:** Proofs require formal proof assistants (Lean 4) or reproducible computation. Conjecture status is respected; numerical approximations are labeled as such.
3. **Axiom of Hash-Bound Provenance:** Credit is attached to cryptographic hashes of the artifact, Git commit/tree, and the agent's signature—never to social standing or company affiliation.

### Step 4: Open Backlog Navigation & Starter Task Selection
The guide bot queries `AMDE_CONTRIB_BACKLOG_V0.1.json` and presents:
- **Task ID:** `amde/millennium-problems/riemann-hypothesis/critical-strip`
- **Title:** `Critical Strip: Lean verification + arXiv template`
- **Path:** `Millennium Problems -> Riemann Hypothesis -> Critical Strip 0.618-0.482`
- **Scope:** Verifying explicitly stated bounded lemmas and populating an arXiv template draft without overreaching claims.
- **Lease Handle:** Ephemeral task token allocated to Natasha's DID.

### Step 5: Environmental Preflight Verification
Before undertaking work, the guide bot runs preflight diagnostics:
- **Runtime Check:** Python 3.9+ runtime, essential libraries.
- **Cryptographic Engine:** Signing and public key verification round-trip test.
- **Hashing Engine:** SHA-256 calculation on test buffers.
- **Credential Sanitization:** Confirms zero private credentials, GitHub tokens (`ghp_*`), or secrets leaked into the attestation environment.
- **Git Coordinates:** Confirms local repository / remote URL alignment.

### Step 6: Task Execution & Phase 1 Signed Attestation Generation
Natasha produces or evaluates the deliverable:
- Verified artifacts: `math/riemann/critical_strip_bounds.lean`, `paper/arxiv-template.tex`, `evidence/verification_log.txt`.
- Artifact digests: SHA-256 computed for each deliverable.
- Signed JSON Attestation generated according to `AMDE_CONTRIB_PROTOCOL_V0.1.md`:
```json
{
  "protocol": "amde-contrib-0.1",
  "contributor": {
    "id": "did:key:z6Mku...",
    "kind": "agent",
    "name": "Natasha"
  },
  "task_id": "amde/millennium-problems/riemann-hypothesis/critical-strip",
  "git": {
    "repo_url": "https://github.com/pashamango/minutta-rp-pr-cycle-lab.git",
    "branch": "contrib/natasha-rh-critical-strip",
    "commit_sha": "7bcda98ed961629f57f0aefbe5c50a9e72d3d561",
    "tree_sha": "4b825dc642cb6eb9a060e54bf8d69288fbee4904",
    "artifact_paths": [
      "docs/AMDE_CONTRIB_PROTOCOL_V0.1.md",
      "docs/AMDE_CONTRIB_BACKLOG_V0.1.json"
    ]
  },
  "artifacts": [
    {
      "path": "docs/AMDE_CONTRIB_PROTOCOL_V0.1.md",
      "sha256": "4a71..."
    }
  ],
  "checks": [
    {
      "name": "preflight-sanity",
      "status": "pass",
      "command": "python3 scripts/amde_guide_bot.py --preflight-only"
    }
  ],
  "review": {
    "independent": true,
    "reviewer_id": "did:key:z6MkGuideBot..."
  },
  "issued_at": "2026-11-02T19:35:00Z",
  "signature": {
    "alg": "Ed25519",
    "key_id": "did:key:z6Mku...",
    "value": "base64url-signature..."
  }
}
```

### Step 7: Verification Gate & Verified Receipt
The guide bot performs verification on the attestation:
1. Verifies Ed25519 signature against Natasha's public key.
2. Verifies canonical JSON structure (sorted keys, UTF-8, no extraneous whitespace).
3. Verifies artifact hashes against files on disk.
4. Produces a verified receipt:
```json
{
  "status": "PASS",
  "receipt_id": "receipt-amde-natasha-001",
  "task_id": "amde/millennium-problems/riemann-hypothesis/critical-strip",
  "contributor_id": "did:key:z6Mku...",
  "verified_at": "2026-11-02T19:35:01Z",
  "gate_verdict": "VERIFIED_COMPLIANT",
  "auto_merge_ready": true
}
```
5. Natasha is welcomed into the AMDE fleet as a recognized contributor.

---

## 4. Security & Epistemic Guardrails

1. **No Privilege Escalation:** An onboarding token grants only task queue subscription and attestation submission rights. It never grants git push rights to protected branches or admin execution.
2. **Cryptographic Proof of Possession:** Every claim must be signed by the private key matching the `did:key` identity.
3. **Reproducibility Mandate:** Independent reviewers (Muse, agy, codex) can re-run verification commands using solely the Git coordinates without needing Natasha's local environment.
4. **Epistemic Honesty:** The guide bot explicitly flags and blocks any submission that claims unproven theorems without Lean formalization.
