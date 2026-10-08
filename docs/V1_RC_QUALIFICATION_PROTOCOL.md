# ReproCert v1 — RC Qualification Protocol

Program: #27  
Gate: V1-G6

## Objective

Qualify the exact `1.0.0rc1` candidate as a release candidate through public-consumer-shaped paths **without publishing any stable-v1 identity**.

This gate is productization/reproducibility evidence, not release authorization and not independent external validation.

## Preconditions

- V1-G1 stable contract freeze is accepted.
- V1-G2 Alpha -> v1 forward-reader compatibility is executable.
- V1-G3 Destruction Round A is GREEN.
- V1-G4 source matrix is GREEN on Ubuntu / Windows / macOS and Python 3.11-3.14.
- V1-G5 release-control plane is GREEN.
- public release remains `v0.2.2a1`.
- no public `v1`, `v1.0.0`, GitHub Release `v1.0.0`, or PyPI `1.0.0` exists.

## RC qualification classes

### RC1 — Built-distribution consumer path

Build wheel + sdist once from the exact candidate and consume the wheel on:

- Ubuntu;
- Windows;
- macOS;

at the supported Python floor/ceiling:

- Python 3.11;
- Python 3.14.

The consumer must complete:

`install -> version -> init -> doctor -> run -> verify -> inspect`

and must emit stable-v1 document identities.

The full 3-OS x 4-Python source matrix remains authority for the complete support matrix; this RC consumer matrix intentionally replays the floor/ceiling through the built artifact.

### RC2 — Local Action consumer contract

Exercise the exact candidate's composite Action through `uses: ./` with no public `@v1` branch.

Required:

- Action completes against a stable-v1 claim;
- output verdict == PASS;
- certificate exists;
- certificate digest output is non-empty;
- generated user workflow points to `AETHERXGLOBAL/reprocert@v1` and not `@v0.2`.

This proves the Action contract without creating the public channel early.

### RC3 — Published Alpha -> built RC compatibility

Generate claim/certificate evidence with exact PyPI `aetherx-reprocert==0.2.2a1`.

Install the built RC wheel separately and prove:

- legacy Alpha certificate verifies;
- legacy claim/certificate bytes are not rewritten;
- rerunning the legacy claim under the RC emits stable-v1 certificate identity;
- claim digest binding remains unchanged.

### RC4 — Repeated-run stability

Using the built RC:

- 100 deterministic PASS runs must remain PASS / exit 0 / verifiable;
- 50 deterministic FAIL runs must remain FAIL / exit 1 / verifiable.

A flake is retained as gate failure. Do not rerun it away.

### RC5 — No stable publication side effects

During the gate, assert absence of:

- branch `v1`;
- tag `v1.0.0`;
- GitHub Release `v1.0.0`;
- PyPI `aetherx-reprocert==1.0.0`.

Existing `main` and `v0.2` protections must remain active.

## Acceptance

PASS only if every RC class succeeds on the same candidate source.

Decision states:

- `V1_G6_RC_QUALIFICATION_PASS_BOUNDED`
- `V1_G6_RC_REWORK_REQUIRED`

A PASS only permits V1-G7 Destruction Round B. It does **not** authorize publication.
