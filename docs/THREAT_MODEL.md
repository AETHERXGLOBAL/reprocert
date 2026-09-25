# Threat Model

## Explicit non-goals

ReproCert does not prove that:

- a claim is scientifically meaningful;
- an evidence source is physically truthful;
- a benchmark is unbiased or representative;
- arbitrary repository code is safe;
- a producer is trustworthy without a separate producer-identity mechanism;
- a PASS result generalizes beyond the declared environment.

## Threats and current controls

### Shell injection

**Control:** `spec.command` is an argv array and execution uses `subprocess.run(..., shell=False)`.

### Path escape

**Control:** absolute paths and `..` traversal are rejected during claim validation; runtime path resolution re-checks containment.

### Secret exposure

**Control:** ReproCert does not intentionally capture environment-variable values. CI workflows must still avoid exposing secrets to untrusted code.

### Certificate editing

**Control:** canonical SHA-256 content identity detects modification when the expected digest is independently trusted. It is not a signature.

### Producer impersonation

**Control:** use an external producer-identity mechanism such as GitHub Artifact Attestations / Sigstore.

### Verdict laundering

**Control:** offline verification recomputes verdict consistency from recorded execution and check states.

### Missing evidence mislabeled as a false claim

**Control:** unresolved required evidence maps to `INCONCLUSIVE`; execution failures map to `ERROR`; false declared checks map to `FAIL`.

## Core trust statement

```text
LOCAL CERTIFICATE INTEGRITY
!= PRODUCER AUTHENTICATION
!= EVIDENCE-SOURCE TRUTH
!= SCIENTIFIC VALIDITY
```
