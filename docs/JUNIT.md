# JUnit Integration

ReproCert v0.2 can read aggregate metrics from JUnit XML and use those metrics as explicit claim observations.

Supported metrics:

`tests` · `failures` · `errors` · `skipped` · `passed` · `time_seconds`

## Example

```yaml
checks:
  - id: no-test-failures
    source:
      type: junit
      path: junit.xml
      metric: failures
    op: eq
    expected: 0
```

This makes ReproCert usable with tools that already emit JUnit XML, including many Python, JVM, JavaScript and CI testing ecosystems.

## Security boundary

DTD and entity declarations are rejected before parsing. ReproCert treats the XML as local evidence and does not resolve external entities.

## Semantic boundary

A zero-failure JUnit report establishes only the declared observation about that report. It does not prove test completeness, absence of hidden failures, or correctness outside the test scope.
