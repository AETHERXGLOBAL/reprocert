# ReproCert v1 — RC Qualification Protocol

Program: #27  
Gate: V1-G6

## Objective

Qualify the release candidate as a product-consumable stable-v1 candidate without publishing any stable-v1 public identity.

## Required evidence

1. Build wheel and sdist from the exact candidate source.
2. Install the built wheel into a clean environment rather than relying only on editable-source execution.
3. Complete zero-contact `init -> doctor -> run -> verify -> inspect`.
4. Generated artifacts must use stable `reprocert.dev/v1` identities.
5. Generated GitHub workflow must use `AETHERXGLOBAL/reprocert@v1`, never `@v0.2`.
6. Repeat a deterministic PASS at least 100 times with successful verification.
7. Repeat a deterministic FAIL at least 50 times; every run must return exit 1 and still produce a verifiable FAIL certificate.
8. Any flake is retained as a qualification failure rather than rerun away.

## Boundaries

- This gate does not publish `1.0.0`, `v1.0.0`, or `@v1`.
- Repeated stability does not prove scientific truth, benchmark fairness or universal determinism.
- External adoption is not manufactured from AETHER X-controlled RC tests.

## Pass condition

`V1_G6_RC_QUALIFICATION_PASS_BOUNDED`
