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

Established:

- [x] multi-claim suite execution and aggregate reports
- [x] direct JUnit XML metrics adapter
- [x] privacy-minimized custom ReproCert attestation predicate
- [x] general + custom GitHub Artifact Attestation reference flow
- [x] JSON inspection output for automation
- [x] GitHub Action certificate-digest output
- [x] expanded adversarial tests for XML and suite boundaries
- [x] CI-provider-neutral CLI integration guidance

## v0.2.1 — Adoption layer

Implemented on the current development line:

- [x] pytest-native convenience adapter with test-failure semantics preserved
- [x] digest-pinned hardened Docker execution profile
- [x] policy layer separate from certificate verdict semantics
- [x] policy integrity pre-check
- [x] accepted-exit-code contracts for adapters
- [x] real Docker integration gate on GitHub-hosted Ubuntu
- [x] JUnit evidence size bound
- [x] adoption-focused examples and documentation
- [x] first same-organization cross-repository consumer integration with signed certificate attestations

Still open for evidence-driven follow-up:

- [ ] independent third-party project integration feedback
- [ ] additional policy rules justified by real use cases
- [ ] container-runtime portability beyond the validated Linux/Docker path
- [ ] stable pre-1.0 compatibility policy based on adopter feedback

## v0.2.2 — Self-service developer onboarding

Implemented on the current development line:

- [x] `reprocert init` with pytest, command, benchmark and conservative auto-detection profiles
- [x] optional generated GitHub Actions workflow
- [x] overwrite protection with explicit `--force`
- [x] `reprocert doctor` with machine-readable output
- [x] five-minute start guide
- [x] troubleshooting guide
- [x] stable `v0.2` GitHub action/install channel design
- [x] PyPI Trusted Publishing workflow using GitHub OIDC
- [x] release tag/package-version consistency gate
- [ ] one-time PyPI Trusted Publisher account configuration
- [ ] first PyPI publication

The remaining PyPI items are account/release operations, not missing package functionality.

## v0.3 — Reproducibility systems research

Research candidates:

- independent-runner reproducibility quorum;
- evidence freshness and temporal validity;
- claim dependency graphs;
- statistically explicit benchmark profiles;
- longitudinal regression certificates;
- portable producer identity across CI providers.

## Explicit non-goal

ReproCert will not turn a successful execution into an unsupported claim of scientific truth, security, determinism, or universal correctness.
