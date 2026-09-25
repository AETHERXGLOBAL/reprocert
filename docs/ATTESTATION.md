# Producer Attestation Model

ReproCert's local verifier answers whether a certificate is internally consistent with the claim and evidence available to the verifier.

It deliberately does **not** treat a self-digest as producer authentication.

## Reference workflow

The repository's `Attested Demo` workflow:

1. checks out the exact Git revision;
2. installs ReproCert;
3. runs the reference claim;
4. verifies the resulting certificate against the local claim and evidence;
5. creates a GitHub Artifact Attestation for the certificate;
6. uploads the certificate as a workflow artifact.

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

A valid signed producer attestation strengthens provenance: it can establish where/how an artifact was produced under the attestation system's trust model.

It does not establish that the benchmark design is unbiased, the measured environment is representative, the source data is physically truthful, or the software is secure.
