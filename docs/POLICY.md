# Certificate Policy Layer

ReproCert v0.2.1 adds an explicit policy layer for organizations that need acceptance rules beyond the underlying claim verdict.

A policy **does not rewrite a certificate verdict**.

## Example

```yaml
apiVersion: reprocert.dev/policy/v1alpha1
kind: ReproCertPolicy
metadata:
  id: release-gate
spec:
  allowed_verdicts: [PASS]
  require_ci: true
  min_evidence_files: 1
  max_diagnostics: 0
  required_check_ids:
    - benchmark-threshold
```

Evaluate it:

```bash
reprocert policy certificate.json policy.yml -o policy-result.json
```

## Current policy rules

- `allowed_verdicts`
- `require_ci`
- `require_git_clean`
- `min_evidence_files`
- `max_diagnostics`
- `required_check_ids`
- `require_container`

Boolean `require_*` rules activate when set to `true`.

## Integrity first

Policy evaluation first checks certificate digest and verdict consistency. A tampered certificate cannot satisfy policy merely because its visible fields look acceptable.

## Separate semantics

A certificate can be:

`Certificate verdict: PASS`

while an organizational policy is:

`Policy result: FAIL`

For example, the claim may be true but the organization may require execution in CI or through the hardened container profile.

This separation is deliberate:

`CLAIM VERDICT != ORGANIZATIONAL ACCEPTANCE POLICY`
