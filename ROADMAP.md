# Roadmap

The roadmap is directional, not a promise of release dates.

## v0.1 — Claim-to-evidence core

Current public-alpha baseline:

- [x] YAML/JSON claim format
- [x] explicit PASS / FAIL / INCONCLUSIVE / ERROR semantics
- [x] bounded argv execution with `shell=False`
- [x] JSON, text, stdout/stderr, file-hash and file-size observations
- [x] evidence SHA-256 records
- [x] environment capture without environment-variable values
- [x] canonical certificate content identity
- [x] offline certificate verification
- [x] certificate diff
- [x] reusable GitHub Action
- [x] open schemas
- [x] Linux / Windows / macOS CI
- [x] reference signed producer-attestation workflow

## v0.2 — Integration depth

Candidates, subject to evidence and review:

- custom ReproCert attestation predicate/profile;
- stable reusable workflow examples;
- pytest/JUnit/benchmark adapters;
- deterministic container-runner profile;
- richer certificate inspection and machine output;
- policy hooks that preserve verdict semantics;
- documentation for CI providers beyond GitHub Actions.

## v0.3 — Reproducibility systems research

Research candidates:

- independent-runner reproducibility quorum;
- evidence freshness and temporal validity;
- claim dependency graphs;
- statistically explicit benchmark profiles;
- longitudinal regression certificates;
- portable producer identity across CI providers.

## Explicit non-goal

ReproCert will not turn a successful execution into an unsupported claim of scientific truth, security, or universal correctness.
