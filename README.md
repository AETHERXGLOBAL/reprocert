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

## Looking for early adopters

Have a real CI, benchmark, testing, AI, or research workflow where a technical claim should be backed by portable evidence?

**ReproCert is actively looking for early adopters.**

Good first integrations include:

- pytest or JUnit quality gates;
- benchmark thresholds;
- reproducible build or artifact checks;
- data-quality assertions;
- CI policies that require explicit evidence;
- workflows that would benefit from signed provenance.

You do **not** need to redesign your project around ReproCert. The preferred first integration is small, isolated, and reversible.

**[Open an Adoption / Integration request →](https://github.com/AETHERXGLOBAL/reprocert/issues/new?template=adoption.yml)**

You can also read the public adopter call in [Issue #7](https://github.com/AETHERXGLOBAL/reprocert/issues/7).

## Quickstart — self-service

No AETHER X account, API key, hosted service, or approval is required.

Until the first PyPI publication is completed, install the stable v0.2 channel directly from GitHub:

```bash
python -m pip install "git+https://github.com/AETHERXGLOBAL/reprocert.git@v0.2"
```

Initialize a pytest project and generate a GitHub Actions workflow:

```bash
reprocert init pytest --github-actions
reprocert doctor
reprocert run reprocert.yml -o reprocert-certificate.json
reprocert verify reprocert-certificate.json --claim reprocert.yml --evidence-root .
```

For other workflows:

```bash
reprocert init command --github-actions
reprocert init benchmark --github-actions
```

Or run `reprocert init --github-actions` and let ReproCert conservatively detect pytest.

Expected result:

```text
ReproCert verdict: PASS
```

See the [5-Minute Start](docs/QUICKSTART_5_MIN.md) and [Troubleshooting](docs/TROUBLESHOOTING.md).

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
- uses: AETHERXGLOBAL/reprocert@v0.2
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

## Pytest-native adapter

Projects that already use pytest can create a ReproCert certificate directly:

```bash
reprocert pytest --workdir . --output pytest-certificate.json -- -q
```

The adapter preserves pytest semantics: ordinary test failures become ReproCert `FAIL`, while unexpected pytest execution states remain `ERROR`. See [Pytest-Native Adapter](docs/PYTEST.md).

## Hardened container execution profile

A claim may run through a constrained Docker profile using an immutable image digest:

```yaml
container:
  engine: docker
  image: registry.example/tool@sha256:<64-hex-digest>
  network: none
  read_only_root: true
  drop_capabilities: true
  no_new_privileges: true
```

Mutable image tags are rejected. The profile is continuously exercised on GitHub-hosted Ubuntu, but it is **not** described as a proof of deterministic computation. See [Container Profile](docs/CONTAINER_PROFILE.md).

## Certificate policy layer

Organizations can apply acceptance requirements without rewriting the underlying claim verdict:

```bash
reprocert policy certificate.json policy.yml -o policy-result.json
```

A certificate may remain `PASS` while the policy result is `FAIL` because, for example, CI or container execution was required. Policy evaluation verifies certificate integrity first. See [Policy Layer](docs/POLICY.md).

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
- [Pytest-native adapter](docs/PYTEST.md)
- [Container profile](docs/CONTAINER_PROFILE.md)
- [Policy layer](docs/POLICY.md)
- [5-minute start](docs/QUICKSTART_5_MIN.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Integration guide](docs/INTEGRATION_GUIDE.md)
- [Publishing](docs/PUBLISHING.md)
- [Adoption evidence](docs/ADOPTION.md)
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
- pytest-native quality-gate adapter;
- digest-pinned hardened Docker execution profile;
- certificate acceptance policies kept separate from claim verdicts;
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
- richer JSON output for automation;
- self-service project scaffolding with `reprocert init`;
- environment/readiness checks with `reprocert doctor`;
- generated GitHub Actions workflow on request.

Not included today:

- remote execution;
- embedded private-key management;
- OCI publication;
- distributed benchmark orchestration;
- general statistical inference;
- scientific correctness adjudication.

## Verified cross-repository adoption

ReproCert is now consumed by a separate existing AETHER X repository, **AETHER X Governed Intelligence**, without modifying that project's product logic or existing disclosure checker.

The consumer workflow produces and verifies a ReproCert certificate, applies an explicit policy, generates a privacy-minimized predicate, and creates signed GitHub attestations on `main`.

This is a **same-organization cross-repository adoption proof**, not independent third-party adoption.

See [Adoption Evidence](docs/ADOPTION.md).

## Project status

**Public Alpha — v0.2.2 self-service line (`0.2.2a1`)**

ReproCert is suitable for evaluation and contribution. Interfaces may still change before a stable v1.0 release.

## License

Apache License 2.0. See [LICENSE](LICENSE).

---

<p align="center"><strong>AETHER X GLOBAL</strong></p>
<p align="center">Financial Markets · Artificial Intelligence · Advanced Technology · Research</p>
