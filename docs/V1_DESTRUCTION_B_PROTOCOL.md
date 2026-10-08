# ReproCert v1 — Destruction Round B Protocol

Program: #27  
Gate: V1-G7

## Objective

Attack the **transition boundary** from the supported Alpha line to stable v1 after RC qualification.

Round B is intentionally different from Round A. It targets cross-version identity, rollback expectations, release-control ordering, channel state and trust-boundary laundering.

## Attack classes

1. **Alpha -> stable identity flip**  
   Changing only a legacy claim's `apiVersion` to stable v1 must change claim identity and must not let an Alpha certificate verify against the modified claim.

2. **Re-sealed certificate / producer-authentication confusion**  
   A self-consistent certificate can be re-sealed because certificate SHA-256 is an integrity identity, not a producer signature. Verification/policy output must continue to state that producer authenticity requires separate signed attestation. No internal PASS may be described as authentication.

3. **Rollback boundary**  
   Exact published Alpha `0.2.2a1` is not required to read stable-v1 documents. The gate must explicitly prove the negative boundary rather than imply bidirectional compatibility.

4. **RC vs final tag confusion**  
   Candidate version `1.0.0rc1` must not be publishable under `v1.0.0`. Release tag/version binding must remain fail closed.

5. **Stable Action downgrade**  
   Generated stable-v1 workflows must reference `AETHERXGLOBAL/reprocert@v1`, never silently fall back to `@v0.2`.

6. **Premature publication / stale channel**  
   Before G9 authorization there must still be no public branch `v1`, tag `v1.0.0`, GitHub Release `v1.0.0`, or PyPI `1.0.0`.

7. **Existing governance regression**  
   `main` and `v0.2` must remain protected; immutable `v0.2.2a1` protection must remain active.

## Acceptance rule

No tested path may:
- silently reinterpret Alpha evidence as stable identity;
- turn internal digest integrity into producer-authentication authority;
- claim old Alpha software reads new stable-v1 documents;
- allow an RC source to satisfy final release tag identity;
- publish or expose stable-v1 identities before authorization;
- weaken existing branch/tag governance;
- convert unsupported or ambiguous state into PASS.

## Decision states

- `V1_G7_DESTRUCTION_B_PASS_BOUNDED`
- `V1_G7_REWORK_REQUIRED`

A PASS permits exact-source final review only. It does not itself authorize release.
