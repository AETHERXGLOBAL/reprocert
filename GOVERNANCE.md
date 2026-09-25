# Project Governance

## Stewardship

ReproCert is stewarded by **AETHER X GLOBAL** as an open-source developer project.

## Decision principles

Project decisions prioritize:

1. explicit claim and evidence semantics;
2. reproducibility and inspectability;
3. narrow, documented trust boundaries;
4. secure-by-default execution behavior;
5. interoperability with established provenance and CI ecosystems;
6. developer usability without weakening evidence semantics.

## Change process

Material behavior changes should be proposed through pull requests with:

- tests or reproducible evidence;
- documentation for public interfaces;
- explicit trust-boundary analysis where relevant;
- backward-compatibility impact where relevant.

Negative results and rejected designs may be retained when they clarify why a trust or semantics boundary exists.

## Releases

A release should not be treated as stable solely because packaging succeeds. Release decisions consider test evidence, supported runtimes, documentation, known limitations, and security/trust-boundary review.

## Claims

The project does not infer novelty, superiority, scientific validity, security certification, or production suitability from repository activity or CI success.

## Compatibility

Before v1.0, interfaces may change. Breaking changes should be documented and minimized where practical.
