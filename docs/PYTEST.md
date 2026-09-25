# Pytest-Native Adapter

ReproCert v0.2.1 adds a convenience adapter for projects that already use pytest.

## Run

```bash
reprocert pytest --workdir . --output pytest-certificate.json -- -q
```

Arguments after `--` are passed to pytest.

## Why this is not just `pytest && reprocert`

Pytest uses distinct process exit codes. In particular, exit code `1` means tests ran and at least one failed.

ReproCert's adapter preserves that distinction:

- pytest exit `0` + zero JUnit failures/errors → `PASS`;
- pytest exit `1` + failed JUnit checks → `FAIL`;
- unexpected pytest exit codes → `ERROR`;
- unresolved JUnit evidence → `INCONCLUSIVE`.

This prevents a normal test failure from being mislabeled as an infrastructure/execution error.

## Generated artifacts

The adapter writes:

- `.reprocert-pytest-claim.json` — the explicit generated claim;
- `.reprocert-pytest-junit.xml` by default — pytest's JUnit evidence;
- the certificate path selected with `--output`.

The generated claim can be supplied to `reprocert verify`.

## Boundary

The adapter does not establish test completeness. A passing pytest suite is evidence only for the declared test scope.
