# Producer Attestation Model

ReproCert's local verifier answers whether a certificate is internally consistent with the claim and evidence available to the verifier.

It deliberately does **not** treat a self-digest as producer authentication.

## Two attestation layers

The repository's `Attested Demo` workflow produces two signed attestations for the same certificate:

1. **General artifact provenance** — GitHub/Sigstore provenance describing where and how the certificate artifact was produced.
2. **ReproCert custom predicate** — a privacy-minimized predicate containing claim identity, certificate identity, verdict, check statuses, evidence digests, selected CI identity, and ReproCert version.

The custom predicate type is the versioned schema URI:

`https://raw.githubusercontent.com/AETHERXGLOBAL/reprocert/main/schemas/attestation-predicate-v1.schema.json`

## Generate a predicate locally

```bash
reprocert predicate certificate.json -o reprocert-predicate.json
```

The predicate intentionally omits command text and stdout/stderr excerpts. Those fields can contain sensitive or irrelevant operational content and are not needed to express the bounded ReproCert result.

## Separation of concerns

```text
certificate/evidence integrity
        !=
producer/workflow identity
        !=
truth of the evidence source
        !=
scientific validity of a claim
```

A valid signed producer attestation strengthens provenance. It does not establish benchmark fairness, security certification, physical truth, or scientific validity.
