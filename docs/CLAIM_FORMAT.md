# Claim Format

The current claim API is:

`reprocert.dev/v1alpha1`

## Minimal structure

```yaml
apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata:
  id: unique-claim-id
  title: Human-readable title
spec:
  command: [python, experiment.py]
  timeout_seconds: 300
  evidence:
    - results.json
  checks:
    - id: result-check
      source:
        type: json
        path: results.json
        pointer: /value
      op: lt
      expected: 10
```

## Command

`spec.command` must be a non-empty list of strings. ReproCert does not pass the declaration through a shell.

## Evidence

`spec.evidence` lists files whose SHA-256 and size will be recorded in the certificate.

Paths must remain within the declared working directory.

## Observation source types

- `json` — read JSON and optionally resolve a JSON Pointer;
- `text` — read UTF-8 text;
- `stdout` / `stderr` — observe process output;
- `exit_code` — observe process exit state;
- `file_sha256` — observe exact file digest;
- `file_size` — observe file size.

## Operators

`eq`, `ne`, `lt`, `le`, `gt`, `ge`, `approx`, `contains`

`approx` requires a non-negative `abs_tolerance`.

The normative machine-readable shape is in [schemas/claim-v1alpha1.schema.json](../schemas/claim-v1alpha1.schema.json).
