# ReproCert Compatibility Contract

Status: **V1 CANDIDATE CONTRACT — NOT YET A PUBLIC STABLE RELEASE**

## Product version and wire format are separate contracts

ReproCert package versions and ReproCert document API versions are related but not identical.

The stable-v1 candidate introduces these preferred document identities:

- claim: `reprocert.dev/v1`
- certificate: `reprocert.dev/certificate/v1`
- policy: `reprocert.dev/policy/v1`
- policy result: `reprocert.dev/policy-result/v1`
- suite: `reprocert.dev/suite/v1`
- suite report: `reprocert.dev/suite-report/v1`
- attestation predicate: existing versioned predicate v1

## Legacy Alpha compatibility

Stable v1 must continue to **read** the supported Alpha document identities:

- `reprocert.dev/v1alpha1`
- `reprocert.dev/certificate/v1alpha1`
- `reprocert.dev/policy/v1alpha1`
- `reprocert.dev/suite/v1alpha1`

Rules:

1. a legacy document is parsed under its recorded identity;
2. its canonical claim/certificate digest is not silently rewritten;
3. v1 may produce a new stable-v1 certificate when executing a legacy claim;
4. v1 verification must accept an intact legacy Alpha certificate;
5. tampered legacy artifacts must fail under the same integrity rules;
6. backward compatibility is **forward-reader compatibility**: v1 reads Alpha artifacts;
7. no claim is made that `0.2.2a1` can read new stable-v1 documents.

## CLI contract

The stable line freezes these public command families:

- `reprocert init`
- `reprocert doctor`
- `reprocert run`
- `reprocert pytest`
- `reprocert suite`
- `reprocert verify`
- `reprocert policy`
- `reprocert predicate`
- `reprocert inspect`
- `reprocert diff`
- `reprocert --version`

Removing or silently redefining one of these requires a future compatibility decision.

## Verdict / process-exit contract

For claim execution paths:

- PASS → 0
- FAIL → 1
- malformed/load/CLI error → 2
- INCONCLUSIVE → 3
- ERROR → 4

Verification and policy evaluation remain binary command outcomes:
- successful verification/evaluation → 0
- failed verification/evaluation → 1
- malformed/load/CLI failure → 2 where the CLI parser/loader rejects the input

A failed claim is not an execution error. An execution error is not a failed scientific claim.

## GitHub Action contract

Stable v1 Action inputs:

- `claim` — required
- `certificate` — optional, default `reprocert-certificate.json`
- `python-version` — optional

Stable outputs:

- `verdict`
- `certificate`
- `certificate-digest`

The Action fails the job unless the ReproCert verdict is PASS.

Stable channel plan:
- immutable: `AETHERXGLOBAL/reprocert@v1.0.0`
- movable: `AETHERXGLOBAL/reprocert@v1`

## Runtime support contract

Stable-v1 qualification target:

- Python 3.11, 3.12, 3.13 and 3.14;
- GitHub-hosted Ubuntu, Windows and macOS for the normal Python/CLI path;
- hardened Docker profile only where separately qualified on the Linux/Docker path.

This is not a universal OS/container guarantee.

## Trust boundary

Stable v1 does not collapse these propositions:

`CERTIFICATE INTEGRITY != PRODUCER AUTHENTICITY != EVIDENCE-SOURCE TRUTH != SCIENTIFIC VALIDITY`

A valid certificate proves the bounded recorded ReproCert checks and integrity conditions. Producer authenticity requires separate signed provenance/attestation when it matters.

## Upgrade / rollback

- upgrading to v1 must preserve the ability to inspect and verify supported Alpha artifacts;
- upgrading does not mutate existing claim, certificate, policy or suite files automatically;
- users may continue pinning immutable `v0.2.2a1` for historical reproduction;
- stable-v1 artifacts use the new stable document identities by default;
- rollback cannot make new stable-v1 artifacts readable by old Alpha software unless that older software already supports them.

## Change policy

Within v1.x:
- breaking CLI/wire-format changes are not allowed silently;
- additive fields must preserve deterministic verification semantics;
- trust-boundary changes require explicit review;
- verdict meaning and exit codes are stable;
- certificate canonicalization/digest semantics are stable unless a separately versioned format is introduced.

No external validation or universal correctness claim is implied by this compatibility contract.
