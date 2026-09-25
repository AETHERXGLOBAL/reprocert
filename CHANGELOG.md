# Changelog

All notable public project changes are recorded here.

The project is pre-1.0; interfaces may evolve while the public alpha is hardened.

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
