# Architecture

## Execution path

```text
claim.yml / claim.json
        │
        ├─ validate bounded claim semantics
        ├─ execute argv with shell=False
        ├─ capture stdout / stderr / exit state
        ├─ resolve declared observations
        ├─ adjudicate explicit comparators
        ├─ hash declared evidence files
        ├─ capture non-secret environment metadata
        └─ emit canonical certificate + SHA-256 content identity
                │
                ├─ offline certificate/evidence verification
                └─ optional external producer attestation
```

## Primary modules

- `claim.py` — claim parsing and validation;
- `runner.py` — bounded execution, evidence resolution, check adjudication;
- `certificate.py` — canonical certificate sealing;
- `verification.py` — offline consistency and evidence verification;
- `environment.py` — runtime metadata capture;
- `cli.py` — developer interface.

## Why commands are argv arrays

ReproCert deliberately avoids shell interpretation for claim commands. Commands are represented as argument arrays and executed with `shell=False`, reducing ambiguity and shell-injection surface.

This does not make arbitrary repository code safe. A claim author still controls which executable is invoked.

## Why signing is external

ReproCert does not invent a long-lived private-key management layer. In CI, workload identity systems such as GitHub OIDC + Sigstore can bind an artifact to a workflow identity without embedding a signing secret in ReproCert.

## Certificate content identity

The certificate includes a canonical SHA-256 content identity. This is useful for stable artifact identity and as a subject digest for external attestation.

It is not authentication by itself.
