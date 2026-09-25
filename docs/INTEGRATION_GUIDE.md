# Integration Guide

## Local CLI

```bash
python -m pip install -e .
reprocert run path/to/claim.yml -o certificate.json
reprocert verify certificate.json --claim path/to/claim.yml --evidence-root path/to/evidence
```

## GitHub Action

```yaml
permissions:
  contents: read

steps:
  - uses: actions/checkout@v7

  - uses: AETHERXGLOBAL/reprocert@main
    id: reprocert
    with:
      claim: path/to/claim.yml
      certificate: reprocert-certificate.json

  - run: echo "Verdict: ${{ steps.reprocert.outputs.verdict }}"
```

## Pull-request safety

A ReproCert claim can execute code. Do not run untrusted claim changes with secrets or elevated permissions.

Prefer:

- `pull_request`, not `pull_request_target`, for untrusted code execution;
- `contents: read` unless additional permissions are necessary;
- separate trusted publication/attestation jobs from untrusted test jobs when appropriate.

## Signed producer provenance

If producer/workflow identity matters, attest the emitted certificate separately using your CI platform's workload identity and signing/attestation mechanism.

The repository's `attested-demo.yml` provides a GitHub reference path.
