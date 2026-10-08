# ReproCert v1 — Final Source Gate

Program: #27  
Gate: V1-G8 final-source requalification

## Purpose

Requalify the **exact source that will exist on `main` immediately before publication**.

This gate is intentionally triggered on both pull requests and pushes to `main`. It removes ambiguity between a GREEN PR head and the merge commit that becomes the authoritative release source.

## Required evidence

### FS1 — Exact stable identity
- package version is exactly `1.0.0`;
- runtime `reprocert.__version__` is exactly `1.0.0`;
- stable classifier is present;
- stable wire identities remain the default.

### FS2 — Full source matrix
Run the complete test suite on:
- Ubuntu;
- Windows;
- macOS;

for:
- Python 3.11;
- Python 3.12;
- Python 3.13;
- Python 3.14.

No matrix failure may be normalized away.

### FS3 — Contract + destruction replay
Re-run:
- stable contract tests;
- Destruction Round A;
- Destruction Round B;
- release-control tests;
- release-workflow tests.

### FS4 — Published Alpha forward compatibility
Generate a claim and certificate with exact public `aetherx-reprocert==0.2.2a1`, then prove exact final v1 source:
- verifies the legacy Alpha certificate;
- does not rewrite the legacy claim/certificate;
- can execute the legacy claim and emit a stable-v1 certificate;
- preserves claim digest binding.

### FS5 — Final distribution identity
Build wheel + sdist and require:
- wheel version `1.0.0`;
- sdist `aetherx_reprocert-1.0.0.tar.gz`;
- clean install from the built wheel;
- zero-contact `init -> doctor -> run -> verify -> inspect`.

## Publication boundary

This workflow does not create:
- tags;
- releases;
- PyPI uploads;
- stable channels.

Absence/presence of public release identities is verified separately by release-control evidence so this gate remains valid for future maintenance after v1 publication.

## Decision

A GREEN run on the exact pre-publication `main` HEAD permits the release transaction only if immutable tag governance and all prior gates remain valid.

Decision states:
- `V1_G8_FINAL_SOURCE_GATE_PASS`
- `V1_G8_FINAL_SOURCE_REWORK_REQUIRED`


## Bootstrap note

The workflow was introduced on the same merge that first placed it on `main`. The first authoritative exact-main evidence must therefore come from a subsequent protected merge after the workflow already exists on the default branch. This note intentionally creates that bootstrap transition; publication remains blocked until the resulting push run is GREEN.
