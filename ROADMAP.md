# Roadmap

The roadmap is directional, not a promise of release dates.

## v1.0 — Stable productization

Stable `v1.0.0` published and qualified under Issue #27.

Completed release gates:

- [x] deep productization gap analysis;
- [x] stable contract freeze accepted by CI;
- [x] stable v1 document identities with Alpha reader compatibility;
- [x] exact published Alpha -> v1 certificate verification replay;
- [x] full source matrix on Linux / Windows / macOS and Python 3.11–3.14;
- [x] destruction round A;
- [x] stable release-control and `@v1` channel plan;
- [x] RC zero-contact/productization qualification;
- [x] destruction round B;
- [x] exact-source final review;
- [x] immutable `v1.*` tag governance verified;
- [x] final `1.0.0` source identity merged and requalified;
- [x] explicit `v1.0.0` release transaction completed.
- [x] exact public PyPI `aetherx-reprocert==1.0.0` qualified on 12 OS/Python combinations;
- [x] real `@v1` Action consumer, channel/tag binding and certificate tamper checks passed;
- [x] moving `v1` branch protected without bypass and with normal forward movement;

Scope rule: v1.0 is a **contract-stabilization release**, not a feature-expansion release.

Exact release evidence: [Release workflow #37844876488](https://github.com/AETHERXGLOBAL/reprocert/actions/runs/37844876488), [Final Source Gate #37834370993](https://github.com/AETHERXGLOBAL/reprocert/actions/runs/37834370993), and [Public Consumer Qualification #37846420495](https://github.com/AETHERXGLOBAL/reprocert/actions/runs/37846420495).

Next work (not retroactive v1 blockers): external adoption/independent review, evidence-driven adapters and security hardening following explicit new gates.


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
- [x] one-time PyPI Trusted Publisher account configuration
- [x] first PyPI publication

PyPI self-service distribution is now operational through Trusted Publishing.

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
