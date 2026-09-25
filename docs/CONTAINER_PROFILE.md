# Hardened Container Execution Profile

ReproCert v0.2.1 can execute a claim command through a constrained Docker profile.

This feature is called a **hardened container execution profile**, not a guarantee of deterministic or universally reproducible computation.

## Claim example

```yaml
spec:
  command: [python, experiment.py]
  container:
    engine: docker
    image: registry.example/tool@sha256:<64-hex-digest>
    network: none
    read_only_root: true
    drop_capabilities: true
    no_new_privileges: true
    pids_limit: 256
  evidence:
    - result.json
  checks:
    - id: result
      source: {type: json, path: result.json, pointer: /value}
      op: eq
      expected: 42
```

## Enforced profile

The current Docker profile requires:

- image identity pinned as `name@sha256:<digest>`;
- network mode `none`;
- read-only container root filesystem;
- all Linux capabilities dropped;
- `no-new-privileges`;
- bounded PID count;
- a small `/tmp` tmpfs;
- only the claim working directory mounted writable at `/workspace`.

Mutable tags such as `python:3.13` are rejected.

## Evidence

The certificate records the normalized container profile and Docker server version when available.

## Current validation boundary

The actual container-execution integration path is continuously exercised on GitHub-hosted Ubuntu runners.

The ordinary ReproCert CLI remains cross-platform. Equivalent hardened container execution on Windows/macOS hosts is not claimed by this profile.

## What this does not prove

A digest-pinned image can still contain nondeterministic software. CPU behavior, kernel behavior, clocks, randomness, external mounted data and other execution factors can still influence results.

`PINNED IMAGE + NETWORK NONE != MATHEMATICAL DETERMINISM`
