# Changelog

All notable public project changes are recorded here.

The project is pre-1.0; interfaces may evolve while the public alpha is hardened.

## Unreleased — v0.2 development line

### Added

- `reprocert suite` for multi-claim execution and aggregate reports;
- JUnit XML observation source with bounded aggregate metrics;
- `reprocert predicate` for privacy-minimized custom attestation predicates;
- JSON output for `reprocert inspect`;
- reusable Action output for certificate digest;
- suite, JUnit and custom predicate schemas/examples;
- expanded adversarial coverage.

### Changed

- package identity advanced to `0.2.0a1`;
- reference attestation workflow now emits both general producer provenance and a custom ReproCert predicate attestation.

## 0.1.0a1 — Initial public-alpha package identity

Initial public source baseline with single-claim execution, evidence hashing, offline verification, cross-platform CI and reusable GitHub Action.

A package-version identifier does not by itself imply publication to a package registry or a GitHub Release.
