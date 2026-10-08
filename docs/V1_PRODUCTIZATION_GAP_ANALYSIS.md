# ReproCert v1.0 — Productization Gap Analysis

Program: #27  
Baseline audited: `main@1e0194e20872f28fc87ea3e69e97890dc1f76ebd`  
Current public release: `v0.2.2a1` / `aetherx-reprocert==0.2.2a1`  
Current classification: Final Supported Alpha

## Executive decision

ReproCert already satisfies most of the productization work normally required before a stable release:

- public PyPI distribution through Trusted Publishing;
- reusable GitHub Action;
- zero-contact onboarding;
- explicit verdict and exit-code semantics;
- cross-platform qualification on Linux, Windows and macOS;
- Python 3.11–3.14 qualification;
- certificate integrity / tamper rejection;
- claim, pytest, JUnit, suite, policy, predicate and hardened-container paths;
- immutable release identity and protected repository governance.

The v1 blocker is therefore **contract stabilization**, not feature breadth.

## Gaps that block stable v1

### G1 — Stable wire/API identities

Current claim, certificate, policy and suite documents use `v1alpha1` identifiers.

A stable product must not continue generating Alpha-labelled wire identities by default.

Decision:
- v1 generates stable `reprocert.dev/v1` family identifiers;
- v1 continues accepting the existing `v1alpha1` identities;
- existing Alpha artifacts are never rewritten in place;
- backward reading/verification is required;
- old Alpha software reading new v1 artifacts is not guaranteed.

### G2 — Stable compatibility contract

The repository did not previously publish one explicit contract covering:
- CLI commands;
- exit codes;
- claim/certificate/policy/suite compatibility;
- GitHub Action inputs/outputs;
- Python/platform support;
- producer-authentication boundary;
- upgrade and rollback expectations.

This is required before v1.

### G3 — Stable Action channel

Current stable public channel is `@v0.2`.

v1 requires:
- immutable `@v1.0.0` release identity;
- deliberate movable `@v1` stable channel;
- consumer proof against the final release source;
- branch governance preventing delete/force-push while still permitting deliberate forward promotion.

### G4 — Release candidate qualification

The Alpha qualification workflow is pinned to `0.2.2a1`.

A separate v1 qualification path is required that proves:
- source contract on the candidate;
- exact Alpha → v1 artifact compatibility;
- full source test matrix;
- package build;
- generated stable workflow;
- stable schemas;
- no public release side effects.

### G5 — Current-facing documentation

README, support, technical evaluation, publishing and status surfaces still correctly describe the currently published Alpha.

They must only switch to stable-v1 wording after final release. Pre-release work must not misrepresent the public state.

## Important non-blockers

The following do not block internally qualified stable v1 by themselves:

- GitHub stars/forks;
- independent third-party adoption;
- external endorsement;
- additional policy rules;
- new adapters;
- remote execution;
- OCI distribution;
- statistical-inference features;
- additional container runtimes.

Those may be valuable follow-on work, but adding them before v1 would increase risk and scope without strengthening the frozen core contract.

## Stable-v1 implementation direction

1. introduce stable v1 wire identifiers;
2. retain Alpha wire identifiers as accepted legacy input;
3. freeze the public compatibility contract;
4. pin dependencies in generated/action workflows where the repository already has vetted commit identities;
5. add v1 RC qualification and cross-version falsification;
6. do not publish until exact-source review passes.

## Current decision

`V1_G0_GAP_ANALYSIS_PASS — CONTRACT_STABILIZATION_REQUIRED`

No public v1 release is authorized by this document.
