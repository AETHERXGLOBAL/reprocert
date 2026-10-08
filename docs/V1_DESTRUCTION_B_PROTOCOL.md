# ReproCert v1 — Destruction Round B Protocol

Program: #27  
Gate: V1-G7

## Objective

Attack the cross-version and release-control boundary after stable-contract and release-control qualification.

## Attack classes

1. Premature public `v1` branch.
2. Premature immutable `v1.0.0` tag.
3. Premature GitHub Release `v1.0.0`.
4. Silent downgrade of generated stable wire identity to `v1alpha1`.
5. Silent downgrade of generated stable Action channel to `@v0.2`.
6. Old Alpha software silently accepting a new stable-v1 artifact.
7. Cross-version test attempts mutating the stable artifact under test.
8. Release workflow losing tag/version binding.
9. Release workflow losing current-main source binding.
10. Regression in Destruction A / stable-contract corpus.

## Expected cross-version behavior

Forward-reader compatibility is one-way:

- stable v1 reads supported Alpha artifacts;
- Alpha software is not required to read stable-v1 artifacts;
- unsupported backward reading must fail rather than silently reinterpret the stable artifact.

## Fail-first rule

Any counterexample blocks G7. No assertion, version check or channel check may be weakened merely to make the gate green.

## Pass condition

`V1_G7_DESTRUCTION_B_PASS_BOUNDED`
