# ReproCert — Current Product Status

## Stable v1.0.0 — qualified public product

**Current stable release:** `v1.0.0` (2026-10-09 closeout), released from immutable commit `1b471deafc747909fb419a05048546bc74bd4c29`.

- GitHub Release: https://github.com/AETHERXGLOBAL/reprocert/releases/tag/v1.0.0
- PyPI: `aetherx-reprocert==1.0.0` — https://pypi.org/project/aetherx-reprocert/1.0.0/
- Protected moving GitHub Action / install channel: `AETHERXGLOBAL/reprocert@v1`, initially at exact immutable release source
- Tested Python versions: 3.11, 3.12, 3.13, 3.14
- Tested platforms: GitHub-hosted Ubuntu 24.04, Windows and macOS
- Stable claim/certificate/policy/suite identity and forward-reader compatibility documented in `docs/V1_STABLE_CONTRACT.md` and `docs/COMPATIBILITY.md`

### Exact-source and public-consumer evidence

- Final Source Gate [#37834370993](https://github.com/AETHERXGLOBAL/reprocert/actions/runs/37834370993) — 15/15 jobs SUCCESS, includes full source matrix, adversarial/destruction replay, published Alpha → v1 compatibility and built-wheel qualification.
- Exact main CI [#37834370992](https://github.com/AETHERXGLOBAL/reprocert/actions/runs/37834370992) — 12/12 jobs SUCCESS.
- Official Release [#37844876488](https://github.com/AETHERXGLOBAL/reprocert/actions/runs/37844876488) — both distribution build and PyPI Trusted Publisher upload SUCCESS, with publish attestations.
- Public Consumer Qualification [#37846420495](https://github.com/AETHERXGLOBAL/reprocert/actions/runs/37846420495) — 14/14 jobs SUCCESS on exact tested PR head `0f6743790712531989683ed80ff86f84aa0f9fb1`: exact PyPI 1.0.0 installed and exercised on all 12 advertised OS/Python combinations, public `@v1` Action output/verdict/digest proof, exact initial branch/tag SHA binding and tamper rejection.
- Independent CI for public-consumer PR [#37846420447](https://github.com/AETHERXGLOBAL/reprocert/actions/runs/37846420447) — 12/12 jobs SUCCESS.
- [PR #37](https://github.com/AETHERXGLOBAL/reprocert/pull/37) merged; it records an initial isolated harness parsing defect and the single corrective patch, without weakening acceptance checks.
- Immutable release tag governance: active no-bypass `refs/tags/v1.*` ruleset #24747076.
- Movable stable branch governance: active no-bypass `refs/heads/v1` ruleset #24751782, denying deletion and force pushes while allowing forward movement.

### Declared stable limitations

Stable describes a tested and supported **product contract**, not independent adoption or universal truth. The certificate's canonical digest proves self-consistency, **not** producer authentication. Independent signed provenance is needed when producer identity matters. Verification of locally supplied evidence does not prove the source was honest, a scientific claim is correct, a benchmark is fair, or a program is secure.

v1 is a **forward reader** for supported Alpha artifacts. The historical Alpha is not required to read v1 artifacts. Tested CI environments do not establish compatibility with all future hosts.

## Historical supported Alpha product state



**ReproCert v0.2.2a1 is the Final Supported Alpha Release within its documented Python/CLI/GitHub Action product boundary.**

Canonical public identities:

- PyPI package: `aetherx-reprocert==0.2.2a1`
- immutable release tag: `v0.2.2a1`
- immutable release source: `4f802fa23891c848b6a984479f5ecc2bb7fb100e`
- stable GitHub Action / source channel: `AETHERXGLOBAL/reprocert@v0.2`
- qualified Python versions: 3.11, 3.12, 3.13 and 3.14 on the tested GitHub-hosted Ubuntu, Windows and macOS environments

The supported Alpha is finished within this bounded scope. Future feature work, interface changes or stable-v1 commitments are separate work and do not change the qualification of immutable `v0.2.2a1`.

## Qualification evidence

Final qualification was executed against the published package and immutable release source, not only against unreleased development code.

Accepted evidence includes:

- exact public PyPI package across Ubuntu / Windows / macOS and Python 3.11 / 3.12 / 3.13 / 3.14;
- zero-contact `init -> doctor -> run -> verify -> inspect` on all 12 runtime combinations;
- explicit CLI verdict contract: PASS `0`, FAIL `1`, INCONCLUSIVE `3`, ERROR `4`, malformed/load error `2`;
- certificate verdict/check tamper rejection, wrong-claim rejection, corrupted-certificate rejection and evidence-content tamper rejection;
- 250 consecutive deterministic PASS executions with certificate verification;
- 100 consecutive deterministic FAIL executions with exit-code and certificate verification;
- immutable-release full regression and package rebuild;
- public wheel and sdist clean installation;
- pytest-native, JUnit, multi-claim suite, policy, predicate and digest-pinned hardened Docker paths;
- stable `v0.2` Action PASS/output contract and source-relationship check.

Canonical qualification workflow run: `37146641481` — SUCCESS.
Ordinary CI on the same qualification head: `37146641364` — SUCCESS.
Qualification issue: `#23`.

Final scientific classification:

`REPROCERT_0_2_2A1_FINAL_SUPPORTED_ALPHA_WITH_DECLARED_LIMITATIONS`

## Declared limitations

The final supported-alpha designation is deliberately bounded:

1. It does not claim independent third-party adoption or external validation. External-adoption work remains open.
2. `reprocert verify` checks certificate structure, internal consistency, optional claim identity and optional local evidence digests; certificate verification alone does not authenticate the producer. Use a separate signed attestation when producer identity matters.
3. Cross-platform qualification proves the tested GitHub-hosted OS/Python matrix, not every future OS/runtime combination.
4. The hardened Docker profile is qualified on the supported GitHub-hosted Ubuntu path and is not a proof of deterministic computation.
5. `v0.2.2a1` remains an Alpha interface and does not claim stable-v1 compatibility.
6. Repository branch protection is governance hardening, separate from the technical qualification of the immutable published artifact. It is tracked in `#25`.
7. `v0.2` is a mutable stable-channel branch. Movement of that branch must not be interpreted as changing the immutable qualification of `v0.2.2a1`.

## Trust boundary

ReproCert converts an explicit claim into recorded execution evidence and a verifiable certificate. It does not convert certificate integrity into scientific or security truth.

`CERTIFICATE INTEGRITY != PRODUCER AUTHENTICITY != EVIDENCE-SOURCE TRUTH != SCIENTIFIC VALIDITY`

ReproCert is not a security certification, proof of benchmark fairness, or adjudicator of scientific correctness.

## External evidence

Independent adoption, external criticism, counterexamples and integration reports remain welcome and may constrain future claims or releases. They are additive evidence and are not retroactively manufactured from AETHER X-controlled tests.
