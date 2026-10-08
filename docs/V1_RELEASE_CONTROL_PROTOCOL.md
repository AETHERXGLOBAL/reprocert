# ReproCert v1 — Release Control Protocol

Program: #27  
Gate: V1-G5

## Objective

Make stable publication fail closed around source identity, package identity and channel ordering.

## Pre-release invariant

Before final authorization there must be no public:

- branch `v1`;
- tag `v1.0.0`;
- GitHub Release `v1.0.0`;
- PyPI `aetherx-reprocert==1.0.0`.

The source tree may carry `1.0.0rc1` only as a non-published release candidate.

## Stable publication transaction

The intended order is:

1. qualify the exact v1 RC source;
2. run destruction round B;
3. perform exact-source final review;
4. create/verify immutable tag protection for `v1.*`;
5. merge the final identity change from `1.0.0rc1` to `1.0.0`;
6. verify all required workflows on that exact main HEAD;
7. create GitHub Release `v1.0.0` targeting that exact HEAD;
8. release workflow must prove:
   - GitHub Release tag == `v` + package version;
   - checked-out release source == current `main` HEAD;
   - package builds from that source;
   - PyPI publication uses Trusted Publishing / OIDC;
9. verify PyPI `1.0.0`;
10. create branch `v1` at the immutable release source;
11. protect `v1` as a deliberately movable channel: no force-push, no delete, no bypass;
12. run public consumer proof against `AETHERXGLOBAL/reprocert@v1`;
13. only then switch README/STATUS from current Alpha to stable v1 wording.

## Failure policy

Any mismatch in tag/version/source stops publication.

A failed publish or consumer proof is retained as evidence and must not be normalized away.

The mutable `v1` channel is not an immutable release identity. Exact releases use `v1.x.y`.

## Existing channels

- `v0.2.2a1` remains immutable historical release identity;
- `v0.2` remains the protected movable Alpha channel for historical/rollback reproduction until explicitly retired;
- stable v1 does not rewrite the Alpha channel.

## Trust / adoption boundary

Successful release engineering does not create independent adoption or external validation.
