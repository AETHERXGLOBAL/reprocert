# Claim Suites

ReproCert v0.2 introduces a bounded suite format for running multiple independent claims under one aggregate report.

## Why suites exist

Projects often need more than one claim:

- a benchmark threshold;
- a unit/integration quality gate;
- an artifact identity check;
- a data-quality assertion.

A suite lets these claims remain individually inspectable while producing one aggregate CI result.

## Example

```yaml
apiVersion: reprocert.dev/suite/v1alpha1
kind: ReproCertSuite
metadata:
  id: developer-quality-suite
  title: Developer quality suite
spec:
  claims:
    - basic/claim.yml
    - junit/claim.yml
```

Run it:

```bash
reprocert suite examples/suite.yml \
  --output suite-report.json \
  --certificate-dir .reprocert/certificates
```

## Aggregate verdict

The suite does not overwrite individual claim semantics.

- if any claim is explicitly `FAIL`, the suite is `FAIL`;
- otherwise, if any claim is `ERROR`, the suite is `ERROR`;
- otherwise, if any claim is `INCONCLUSIVE`, the suite is `INCONCLUSIVE`;
- otherwise the suite is `PASS`.

This ordering means a known false requirement is not hidden by an unrelated execution error.

## Boundary

A suite is orchestration, not a new proof system. Every member claim still emits its own certificate and evidence identity.
