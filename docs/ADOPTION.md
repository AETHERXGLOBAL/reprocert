# Adoption Evidence

ReproCert is intended to be used as an independent developer tool across repositories, not only inside its own test suite.

## First cross-repository consumer integration

The first verified cross-repository consumer is:

**AETHERXGLOBAL/aether-x-governed-intelligence**

Consumer commit:

`58f4ad83896d675e3cf3a412fe01bdc2b3f52dee`

Consumer workflow:

`.github/workflows/reprocert-consumer-proof.yml`

Consumer configuration:

`.reprocert/public-surface-boundary.yml`  
`.reprocert/public-surface-policy.yml`

### Real use case

The consumer repository already had an independent public-disclosure checker:

`tools/check_public_surface.py`

ReproCert was integrated **without changing that checker or any Governed Intelligence product logic**.

The resulting flow is:

```text
existing disclosure checker
        ↓
ReproCert claim
        ↓
certificate + evidence hashes
        ↓
offline verification
        ↓
repository acceptance policy
        ↓
privacy-minimized ReproCert predicate
        ↓
signed producer provenance + custom predicate attestation
```

### Verified result

On the consumer repository's `main` branch:

- existing public-disclosure gate: **PASS**;
- ReproCert consumer claim: **PASS**;
- certificate verification: **PASS**;
- repository policy: **PASS**;
- custom predicate generation: **PASS**;
- artifact bundle publication: **PASS**;
- general producer-provenance attestation: **PASS**;
- custom ReproCert predicate attestation: **PASS**.

Reference workflow run:

https://github.com/AETHERXGLOBAL/aether-x-governed-intelligence/actions/runs/36149220250

### Isolation result

The integration added only consumer configuration and CI workflow files. It did not modify:

- Governed Intelligence implementation logic;
- the existing disclosure checker;
- proprietary architecture;
- licensing boundaries;
- product maturity claims.

This matters because a developer tool is more credible when it can be introduced into an existing repository without forcing the target project to reorganize around the tool.

## What this establishes

This integration establishes:

- cross-repository consumption of ReproCert from its independent repository;
- use of the reusable GitHub Action pinned by commit SHA;
- a real claim/evidence/policy workflow outside ReproCert's own repository;
- signed provenance for a certificate produced by a consumer repository;
- compatibility with an existing CI control rather than a ReproCert-specific toy workload.

## What this does not establish

This is an **AETHER X internal cross-repository adoption proof**, not independent third-party adoption.

It does not establish:

- external community adoption;
- production deployment;
- security certification;
- scientific validity;
- superiority over other provenance or CI systems;
- stable v1 API compatibility.

Independent external integrations remain an explicit next validation target.
