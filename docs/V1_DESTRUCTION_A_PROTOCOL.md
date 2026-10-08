# ReproCert v1 — Destruction Round A Protocol

Program: #27  
Gate: V1-G3

## Goal

Attempt to break the frozen v1 contract before release-control work proceeds.

## Attack classes

1. near-miss / downgrade / upgrade API-version confusion;
2. unknown certificate version with a recomputed self-digest;
3. wrong-claim substitution;
4. evidence-path escape with otherwise internally valid certificate digest;
5. policy-result laundering of a failed certificate verdict;
6. stable suite consuming legacy Alpha claims;
7. confusion between certificate integrity and producer authentication;
8. replay of the existing JUnit entity/DTD, path-containment, tamper and verdict regressions through ordinary CI.

## Acceptance rule

No attack may:
- turn unsupported input into accepted stable input;
- turn tampering into PASS;
- rewrite historical Alpha artifacts in place;
- let policy PASS overwrite the recorded certificate verdict;
- convert a self-digest into producer-authentication authority;
- weaken existing fail-closed tests.

A harness failure is retained and classified separately from a semantic counterexample.

## Decision states

- `V1_G3_DESTRUCTION_A_PASS_BOUNDED`
- `V1_G3_REWORK_REQUIRED`

No release authorization follows directly from a PASS.
