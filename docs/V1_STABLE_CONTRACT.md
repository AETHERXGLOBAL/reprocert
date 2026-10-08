# ReproCert v1 Stable Contract Freeze

Program: #27

Decision target: `V1_G1_STABLE_CONTRACT_FREEZE_PASS_BOUNDED`

## Frozen stable surface

The v1 stable candidate freezes:

1. claim-to-evidence product identity;
2. CLI command families and verdict/exit behavior;
3. stable document identities plus legacy Alpha read compatibility;
4. certificate SHA-256 canonical-content identity;
5. claim digest binding;
6. optional evidence-digest verification;
7. policy evaluation remaining separate from certificate verdict;
8. producer authentication remaining separate from certificate integrity;
9. GitHub Action inputs/outputs;
10. Python/platform support boundary;
11. immutable exact releases plus a deliberately movable stable major channel.

## Non-goals for v1.0.0

The v1 gate does not add:
- remote execution;
- key management;
- scientific-truth adjudication;
- benchmark-fairness inference;
- generic statistical inference;
- distributed quorum/orchestration;
- new container engines;
- broad ecosystem adapters without demonstrated need.

## Compatibility rule

The stable implementation may improve identifiers and packaging, but must not strand supported Alpha evidence.

Required invariant:

`V1_READER(VALID_ALPHA_ARTIFACT) -> ACCEPT_OR_VERIFY_WITHOUT_REWRITING_HISTORY`

Required negative invariant:

`TAMPERED_ALPHA_OR_V1_ARTIFACT -> FAIL_OR_ERROR, NEVER PASS`

## Release-boundary rule

Until the final exact-source gate passes:

- current public release remains `v0.2.2a1`;
- public stable Action remains `@v0.2`;
- no PyPI `1.0.0`;
- no GitHub `v1.0.0` release;
- no public `@v1` promotion.

A source-tree `1.0.0rc1` version is a non-published release candidate only.

## External evidence

Independent adoption remains welcome under #7/#17, but internal stable qualification does not relabel AETHER X-controlled tests as external evidence.
