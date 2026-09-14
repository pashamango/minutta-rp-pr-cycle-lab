# CAPABILITYD_MACOS_PRODUCTION_BOUNDARY_DECISION/v1

**Task/source/lease:** `CAPABILITYD-MACOS-PRODUCTION-BOUNDARY-DECISION-0001` / issue 242 / `3b2855930c3f3199e8d9e5d16a4c7ebb45a775cc2d80b3cd54ce4b20b844560a` / `700978021a2a4e59a6f3359b270268a5`  
**Research date:** 2026-09-14. **Base:** `acf6266067825849a0d8e2ce6b27bedd4bf4308d`. **Continuity predecessor:** `e8d9850721bdf182458e86a2c7ae7c04d5a6b16a`.  
**Verdict:** `SUPPORTED_ZERO_TOUCH_PATH_ABSENT / owner-controlled supervised MDM (or repeated user TCC consent) is the missing authority for protected-folder zero-touch; a user-installed profile cannot substitute for MDM.`

## Decision

The smallest production boundary that meets “no routine per-Python prompts” is a single, stable, signed broker application (not each Python interpreter), installed in `/Applications`, with owner-controlled supervised MDM delivering PPPC for only the broker’s required protected-folder classes. Apple documents PPPC as requiring a device-management service and supervised device, and identifies the app by bundle ID plus a code-signing requirement; `SystemPolicyDocumentsFolder` and `SystemPolicyAllFiles` are distinct services. [Apple Deployment, PPPC payload settings (published 2024-07-29)](https://support.apple.com/en-gb/guide/deployment/dep38df53c2a/web), [Apple PPPC services](https://developer.apple.com/documentation/devicemanagement/privacypreferencespolicycontrol/services-data.dictionary)

This is an owner bootstrap, not an agent-granted permission. Without that owner authority, the honest result is the negative verdict above. The narrow alternative is to keep all imported data under ChitAkasha-controlled storage and use a user-selected folder/bookmark for explicit import; it removes the need for broad Documents access but does not make arbitrary protected-folder reads zero-touch.

## Capability-to-control-surface map

| Required class | Actual macOS surface | PPPC/MDM | User-installed profile | Irreducible user action |
|---|---|---|---|---|
| Documents read/import | TCC `SystemPolicyDocumentsFolder`; App Sandbox file entitlement and Open/Save panel semantics | Can preauthorize the signed broker’s Documents-folder access when owner-managed/supervised | Cannot install PPPC; PPPC payload requires device-management service | Open/Save panel, drag/drop, or first unprofiled access; Apple says selection gives implied consent |
| Local storage write | App container/group; user-selected location; security-scoped bookmark; TCC only if writing outside mediated location | PPPC only for the relevant protected class, not arbitrary bookmark issuance | Cannot grant PPPC | User selects location once and broker persists a scoped bookmark; broker must start/stop scope |
| Broker IPC | XPC/Unix socket plus code-signing/launch constraints and peer validation; AppleEvents only if AppleEvents are used | PPPC AppleEvents can authorize specified sender/receiver pairs; it does not authenticate an arbitrary socket peer | Cannot grant this authority | Consent may still be needed for a newly introduced restricted IPC path |
| Remote presence renewal | WebAuthn browser/user-agent and RP server; TLS transport; local broker session | Not a TCC grant and not replaced by PPPC | Not a WebAuthn credential | Fresh user-mediated WebAuthn assertion; server verifies challenge, origin, RP ID, signature and policy |

Apple states that Documents access is implicitly granted by Open/Save selection or drag/drop, while first direct access prompts; security-scoped bookmarks persist a selected resource across relaunches and require resolving plus access-scope handling. [Apple `NSDocumentsFolderUsageDescription`](https://developer.apple.com/documentation/bundleresources/information-property-list/nsdocumentsfolderusagedescription), [Apple App Sandbox file access](https://developer.apple.com/documentation/security/accessing-files-from-the-macos-app-sandbox)

## Identity and change invalidation

PPPC targeting must record the broker’s globally unique bundle identifier (`CFBundleIdentifier`), its exact designated requirement (DR), and the Team ID/certificate lineage used by the distribution signature. Apple describes the DR as the identity macOS records so later versions can retain access; the default DR normally combines an Apple trust anchor, identifier, and Team ID. A Developer ID Application signature is the compatible independent-distribution route. [Apple TN3127, Inside Code Signing: Requirements](https://developer.apple.com/documentation/technotes/tn3127-inside-code-signing-requirements), [Apple distribution signing](https://developer.apple.com/documentation/xcode/creating-distribution-signed-code-for-the-mac/)

Trust must be treated as invalid or requiring owner review if the bundle ID/signing identifier changes, the DR no longer matches, Team ID or certificate chain changes, the code is re-signed by another team, the broker is moved outside the managed installation path, or a nested helper changes identity. A version update that still satisfies the approved DR is the intended stable case; a cdhash-pinned rule intentionally invalidates other versions. PPPC must target the broker executable that actually crosses the TCC boundary, not an untrusted Python child.

## Boundary alternatives

| Option | Prompt reduction | Authority/security boundary | Decision |
|---|---|---|---|
| Owner MDM + PPPC for signed broker | Yes for approved TCC classes | Owner/supervised device, exact signed identity; narrowest zero-touch path | **Recommended** |
| One-time direct TCC consent to stable signed broker | Yes after owner consents; not zero-touch | Per-user consent, no owner fleet control; reset/replacement can re-prompt | Viable fallback, not the requested production zero-touch |
| Sandbox + security-scoped bookmark/user-selected folder | Eliminates repeated prompts for selected resources, not arbitrary Documents reads | User explicitly delegates a folder/file; bookmark is scoped and revocable by removal | Cheapest no-MDM import path |
| Import outside protected folders | Avoids protected-folder TCC entirely | ChitAkasha owns the storage boundary; user exports/selects data | Preferred if product can change the data boundary |

## Production approval and renewal

The web link is a one-time ceremony launcher containing an opaque, short-lived transaction handle only; it is never a bearer grant. The RP creates a fresh challenge and receives a WebAuthn assertion. WebAuthn credentials are scoped to an RP and accessible only to matching origins; the authenticator/user agent requires user consent. [W3C WebAuthn Level 3 Recommendation, 2026-08-25, §§1 and 7](https://www.w3.org/TR/2026/REC-webauthn-3-20260825/)

The verified mandate binds: principal/account; exact HTTPS RP origin and RP ID; credential ID/public key; device and broker identity (bundle ID, DR digest, Team ID, broker instance key); canonical mandate digest; capability scope; epoch; expiry/deadline; fresh nonce/challenge; and parent/descendant reference. The server rejects reused challenges/nonces, wrong origin/RP hash, wrong principal, stale epoch, expired mandate, revoked ancestor, mismatched broker identity, or scope not attenuated from the parent. Renewal creates a new descendant with the same or narrower scope and a new challenge/nonce; scope expansion is a new approval requiring fresh explicit owner/principal consent and must never be disguised as renewal. A link alone proves none of these properties.

## Threat and boundary table

| Threat/event | Required control | Failure result |
|---|---|---|
| Replay | Single-use challenge/nonce, expiry, server-side transaction state | Reject |
| Cross-device proof mixing | Bind assertion, principal, device/broker key and mandate digest | Reject |
| Broker binary replacement | Verify signature, DR, Team ID and approved installation identity | Re-bootstrap/revoke |
| Reboot | Persist only non-secret mandate metadata/bookmark; require fresh renewal policy | Resume only if epoch, expiry and identity pass |
| Wall-clock rollback | Server/monotonic lease time and bounded clock-skew checks | Reject or require online renewal |
| Stolen old session state | No bearer link; encrypted/authenticated state plus epoch/revocation check | Reject |
| Scope widening | Canonical scope comparison; descendants may only attenuate | Reject and alarm |
| Revoked/expired descendant | Check ancestor chain, epoch and expiry at every use | Reject |

## One next vertical slice

Build only: a signed broker proof-of-concept that imports one user-selected folder into ChitAkasha-controlled storage, persists one read-only security-scoped bookmark, and performs one WebAuthn renewal bound to the canonical mandate digest. Do not request Documents-folder PPPC yet.

**One-time human bootstrap:** the owner launches the signed broker, selects exactly one fixture folder in an Open panel, reviews the displayed scope and broker identity, and completes one WebAuthn assertion at the fixed RP origin. No MDM enrollment, profile installation, Keychain/Secure Enclave access, daemon activation, or network exposure is part of this slice.

**Pass:** selected fixture imports after relaunch without a new prompt; unselected sibling folder is denied; bookmark stale/revoked state fails closed; a fresh assertion renews the same-or-narrower scope; replay, wrong-origin, wrong-device-key, expired, widened-scope and revoked-ancestor fixtures all reject; broker signature/DR mismatch rejects. **Fail:** any unselected access succeeds, a link alone authorizes, renewal widens scope, or any invalid fixture is accepted.

**Cheapest falsification:** after the one selection, relaunch the broker and attempt (a) the selected folder, (b) an unselected protected folder, and (c) a replaced/re-signed broker against the same stored state. If (a) fails, bookmark mediation is not viable; if (b) or (c) succeeds, the boundary is unsound. Rollback is deletion of the prototype branch/artifacts and removal of the stored bookmark/mandate; no production state is changed.

## Negative findings and non-action

No MDM/profile installation, TCC inspection/reset, protected-resource access, signing/certificate enrollment, passkey registration, UI automation, daemon activation, credentials, network service, or dispatcher/reporter change was performed. Repository inspection found the synthetic mandate/attenuation material but no installed production broker identity or macOS authority that could convert it into a supported zero-touch guarantee. This report therefore does not claim runtime settlement.
