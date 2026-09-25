# Roadmap

The roadmap is directional, not a promise of release dates.

## v0.1 — Claim-to-evidence core

Completed baseline:

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

Implemented on the v0.2 development line:

- [x] multi-claim suite execution and aggregate reports
- [x] direct JUnit XML metrics adapter
- [x] privacy-minimized custom ReproCert attestation predicate
- [x] general + custom GitHub Artifact Attestation reference flow
- [x] JSON inspection output for automation
- [x] GitHub Action certificate-digest output
- [x] expanded adversarial tests for XML and suite boundaries
- [x] CI-provider-neutral CLI integration guidance

Still open for later v0.2.x evaluation:

- [ ] pytest-native convenience adapter beyond JUnit interoperability
- [ ] deterministic container-runner profile
- [ ] policy hooks that preserve verdict semantics
- [ ] wider external integration feedback

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
