# Integration Guide

## Self-service local CLI

```bash
python -m pip install "git+https://github.com/AETHERXGLOBAL/reprocert.git@v0.2"
reprocert init --github-actions
reprocert doctor
reprocert run reprocert.yml -o certificate.json
reprocert verify certificate.json --claim reprocert.yml --evidence-root .
reprocert inspect certificate.json --json
```

The init command supports `pytest`, `command`, and `benchmark` profiles. It refuses to overwrite existing generated files unless `--force` is supplied.

## Multi-claim suite

```bash
reprocert suite examples/suite.yml \
  --output suite-report.json \
  --certificate-dir .reprocert/certificates \
  --json
```

## JUnit-producing test systems

Generate JUnit XML using the native test framework, then point a ReproCert check at the file:

```yaml
source:
  type: junit
  path: junit.xml
  metric: failures
op: eq
expected: 0
```

## GitHub Action

```yaml
permissions:
  contents: read

steps:
  - uses: actions/checkout@v7

  - uses: AETHERXGLOBAL/reprocert@v0.2
    id: reprocert
    with:
      claim: path/to/claim.yml
      certificate: reprocert-certificate.json

  - run: |
      echo "Verdict: ${{ steps.reprocert.outputs.verdict }}"
      echo "Digest: ${{ steps.reprocert.outputs.certificate-digest }}"
```

## Custom attestation predicate

```bash
reprocert predicate reprocert-certificate.json \
  --output reprocert-predicate.json
```

In GitHub Actions, `actions/attest@v4` supports custom predicates using `predicate-type` and `predicate-path`. See the repository's `attested-demo.yml` for the exact working reference.

## Pull-request safety

A ReproCert claim can execute code. Do not run untrusted claim changes with secrets or elevated permissions.

Prefer:

- `pull_request`, not `pull_request_target`, for untrusted code execution;
- `contents: read` unless additional permissions are necessary;
- separate trusted publication/attestation jobs from untrusted test jobs when appropriate.

## Other CI providers

The ReproCert CLI has no GitHub Actions runtime dependency. Any CI system that can install Python 3.11+ and run commands can execute claims or suites and retain the resulting JSON artifacts.

Producer authentication is provider-specific and remains separate from local ReproCert verification.
