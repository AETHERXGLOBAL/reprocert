# Changelog

All notable public project changes are recorded here.

The project is pre-1.0; interfaces may evolve while the public alpha is hardened.

## Unreleased — v0.2.2 self-service

### Added

- `reprocert init` for pytest, command and benchmark scaffolding;
- conservative pytest auto-detection;
- optional generated GitHub Actions workflow using the stable v0.2 channel;
- overwrite protection unless `--force` is explicit;
- `reprocert doctor` for project/readiness diagnostics;
- five-minute self-service onboarding guide;
- troubleshooting guide;
- PyPI Trusted Publishing release workflow using GitHub OIDC;
- release tag/package-version identity check.

### Distribution

The public GitHub v0.2 channel provides self-service installation independently of PyPI. PyPI publication remains gated on one-time Trusted Publisher account configuration.

## Unreleased — v0.2.1 adoption layer

### Added

- `reprocert pytest` native convenience adapter;
- accepted exit-code contracts so domain failures can remain `FAIL` rather than becoming `ERROR`;
- digest-pinned hardened Docker execution profile;
- `reprocert policy` and machine-readable policy results;
- policy schema and reference policies;
- real Docker integration validation on GitHub-hosted Ubuntu;
- JUnit XML evidence size limit.

### Security / semantics

- mutable container image tags are rejected;
- container profile forces network-none, read-only root, capability drop and no-new-privileges;
- policy evaluation verifies certificate integrity before applying acceptance rules;
- policy results remain separate from claim verdicts.

## v0.2.0a1 — Integration-depth development line

### Added

- multi-claim suites;
- JUnit XML observations;
- privacy-minimized custom attestation predicate;
- richer automation outputs;
- general + custom GitHub Artifact Attestation reference flow.

## 0.1.0a1 — Initial public-alpha package identity

Initial public source baseline with single-claim execution, evidence hashing, offline verification, cross-platform CI and reusable GitHub Action.

A package-version identifier does not by itself imply publication to a package registry or a GitHub Release.
