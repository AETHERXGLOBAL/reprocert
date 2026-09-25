<p align="center">
  <img src="https://raw.githubusercontent.com/AETHERXGLOBAL/.github/main/profile/assets/aether-x-premium-banner.png" alt="AETHER X GLOBAL" width="100%" />
</p>

<h1 align="center">ReproCert</h1>

<p align="center"><strong>Claim-to-evidence reproducibility certificates for software, AI and research workflows.</strong></p>

<p align="center">
  <a href="https://github.com/AETHERXGLOBAL/reprocert/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/AETHERXGLOBAL/reprocert/actions/workflows/ci.yml/badge.svg"></a>
  <a href="./LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/badge/License-Apache--2.0-blue.svg"></a>
  <img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-blue.svg">
  <img alt="Status: Public Alpha" src="https://img.shields.io/badge/Status-Public%20Alpha-orange.svg">
</p>

<p align="center">
  <code>CLAIM → EXACT COMMAND → EVIDENCE → VERDICT → CERTIFICATE</code>
</p>

---

## What ReproCert does

ReproCert is an open-source developer tool from **AETHER X GLOBAL** that turns explicit technical claims into machine-checkable, reproducible evidence records.

Instead of writing an unsupported statement such as:

> “This benchmark completes in under two seconds.”

you define the claim, command, evidence files and acceptance conditions. ReproCert executes the declared workflow, records evidence and environment metadata, evaluates the checks, and emits a machine-readable certificate with one of four explicit outcomes:

`PASS` · `FAIL` · `INCONCLUSIVE` · `ERROR`

ReproCert is intentionally narrow. It does **not** claim that a benchmark is unbiased, a scientific hypothesis is true, or software is secure merely because a certificate passes.

`CERTIFICATE INTEGRITY ≠ PRODUCER AUTHENTICITY ≠ SCIENTIFIC TRUTH`

## Why it exists

Modern software and AI projects routinely publish performance, compatibility, reproducibility and data-quality claims. The evidence behind those claims is often fragmented across scripts, CI logs, screenshots and human interpretation.

ReproCert creates a portable boundary between a claim and its supporting execution evidence:

```text
CLAIM
  ↓
DECLARED EXECUTION
  ↓
OBSERVED EVIDENCE
  ↓
EXPLICIT CHECKS
  ↓
PASS / FAIL / INCONCLUSIVE / ERROR
  ↓
REPRODUCIBILITY CERTIFICATE
```

It is designed to complement — not replace — test frameworks, benchmark harnesses, SLSA, in-toto, Sigstore, GitHub Artifact Attestations and experiment-tracking systems.

## Quickstart

Requires Python 3.11+.

```bash
git clone https://github.com/AETHERXGLOBAL/reprocert.git
cd reprocert
python -m pip install -e .
cd examples/basic
reprocert run claim.yml --output certificate.json
reprocert verify certificate.json --claim claim.yml --evidence-root .
reprocert inspect certificate.json
```

Expected verdict:

```text
ReproCert verdict: PASS
```

## Example claim

```yaml
apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata:
  id: api-latency
  title: Median latency stays below the declared threshold
spec:
  command: [python, benchmark.py]
  timeout_seconds: 60
  evidence:
    - results.json
  checks:
    - id: latency
      source:
        type: json
        path: results.json
        pointer: /median_ms
      op: lt
      expected: 2000
```

### Supported observation sources

`json` · `text` · `stdout` · `stderr` · `exit_code` · `file_sha256` · `file_size` · `junit`

### Supported comparators

`eq` · `ne` · `lt` · `le` · `gt` · `ge` · `approx` · `contains`

## Verdict semantics

| Verdict | Meaning |
|---|---|
| **PASS** | Execution completed as specified, required evidence was available, and every declared check passed. |
| **FAIL** | Execution completed, evidence was available, and at least one declared claim check was false. |
| **INCONCLUSIVE** | Execution completed but required evidence could not be resolved or adjudicated. |
| **ERROR** | The declared execution could not run as specified, timed out, or returned an unexpected process exit code. |

The distinction matters: a crashed benchmark is not automatically evidence that the benchmark claim is false.

## GitHub Action

Use ReproCert directly in another repository:

```yaml
- uses: AETHERXGLOBAL/reprocert@main
  id: reprocert
  with:
    claim: path/to/claim.yml
    certificate: reprocert-certificate.json

- run: |
    echo "Verdict: ${{ steps.reprocert.outputs.verdict }}"
    echo "Digest: ${{ steps.reprocert.outputs.certificate-digest }}"
```

For untrusted pull requests, use least-privilege workflow permissions and never expose secrets to code you do not trust.

## Multi-claim suites

ReproCert v0.2 can execute several independent claims under one aggregate report while preserving a separate certificate for every member claim.

```bash
reprocert suite examples/suite.yml \
  --output suite-report.json \
  --certificate-dir .reprocert/certificates
```

A known false claim remains `FAIL`; it is not hidden by an unrelated execution error. See [Claim Suites](docs/SUITES.md).

## JUnit integration

Existing test systems can feed ReproCert without rewriting their test runners. Point a check at JUnit XML and select an aggregate metric:

```yaml
source:
  type: junit
  path: junit.xml
  metric: failures
op: eq
expected: 0
```

Supported metrics are `tests`, `failures`, `errors`, `skipped`, `passed`, and `time_seconds`. See [JUnit Integration](docs/JUNIT.md).

## Custom attestation predicate

Generate a privacy-minimized predicate from a certificate:

```bash
reprocert predicate certificate.json -o reprocert-predicate.json
```

The reference workflow signs both general artifact provenance and the ReproCert-specific predicate with GitHub Artifact Attestations. The predicate deliberately excludes command text and stdout/stderr excerpts.

## Certificate verification

ReproCert separates two questions:

1. **Is the certificate internally consistent with the claim and evidence I have?**  
   `reprocert verify` checks certificate integrity, verdict consistency, optional claim identity and optional evidence hashes.

2. **Who produced the certificate and in which repository/workflow?**  
   Use a signed external attestation. This repository includes a reference workflow using GitHub Artifact Attestations.

A certificate self-digest is a stable content identifier. It is **not** a digital signature.

## Developer surface

- [Architecture](docs/ARCHITECTURE.md)
- [Attestation model](docs/ATTESTATION.md)
- [Claim suites](docs/SUITES.md)
- [JUnit integration](docs/JUNIT.md)
- [Integration guide](docs/INTEGRATION_GUIDE.md)
- [Threat model](docs/THREAT_MODEL.md)
- [Roadmap](ROADMAP.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Governance](GOVERNANCE.md)
- [Support](SUPPORT.md)

## Current public-alpha scope

Included today:

- YAML and JSON claim definitions;
- bounded argv execution with `shell=False`;
- deterministic claim hashing;
- JSON Pointer observations;
- stdout/stderr/file/JUnit observations;
- multi-claim suites with aggregate reports;
- SHA-256 evidence records;
- non-secret environment capture;
- canonical certificate digest;
- offline certificate verification;
- certificate comparison;
- reusable composite GitHub Action;
- open JSON Schemas;
- cross-platform CI;
- adversarial path-boundary tests;
- general producer-provenance attestation plus a custom ReproCert predicate;
- privacy-minimized predicate generation;
- richer JSON output for automation.

Not included today:

- remote execution;
- embedded private-key management;
- OCI publication;
- policy engines;
- distributed benchmark orchestration;
- general statistical inference;
- scientific correctness adjudication.

## Project status

**Public Alpha — v0.2 development line (`0.2.0a1`)**

ReproCert is suitable for evaluation and contribution. Interfaces may still change before a stable v1.0 release.

## License

Apache License 2.0. See [LICENSE](LICENSE).

---

<p align="center"><strong>AETHER X GLOBAL</strong></p>
<p align="center">Financial Markets · Artificial Intelligence · Advanced Technology · Research</p>
