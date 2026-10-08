# Publishing ReproCert

## Package identity

PyPI package name:

aetherx-reprocert

Recommended reproducible current stable install:

~~~bash
python -m pip install "aetherx-reprocert==1.0.0"
~~~

Current immutable [GitHub Release `v1.0.0`](https://github.com/AETHERXGLOBAL/reprocert/releases/tag/v1.0.0) and exact [public PyPI package `1.0.0`](https://pypi.org/project/aetherx-reprocert/1.0.0/) were published via [successful release workflow](https://github.com/AETHERXGLOBAL/reprocert/actions/runs/37844876488). The [public consumer proof](https://github.com/AETHERXGLOBAL/reprocert/actions/runs/37846420495) exercised exact PyPI 1.0.0 and the public `@v1` Action, not editable candidate source. Newer releases require their own independent gate; do not infer current stable automatically.

## Security model

The release workflow uses PyPI Trusted Publishing through GitHub OIDC. It does not require a long-lived PYPI_TOKEN secret.

The publishing job is isolated behind the GitHub environment named pypi and runs only when a GitHub Release is published.

## Trusted Publisher configuration

Trusted Publishing is configured and the first PyPI publication has completed successfully.

Current publisher identity:

- PyPI project: aetherx-reprocert
- GitHub owner: AETHERXGLOBAL
- Repository: reprocert
- Workflow: release.yml
- Environment: pypi

The release workflow uses GitHub OIDC and does not require a long-lived PyPI API token.

## Release identity

The release workflow requires the GitHub Release tag to exactly match the package version in pyproject.toml with a leading v.

Current stable example:

package version: `1.0.0`
release tag: `v1.0.0`

Historical Alpha example retained below: `0.2.2a1` ↔ `v0.2.2a1`.

A mismatch fails before publication.

## Stable GitHub channel

The protected `v1` branch is the **current moving stable major Action/install channel**. Its initial source is the same as immutable `v1.0.0` (`1b471deafc747909fb419a05048546bc74bd4c29`), and future forward moves require independent qualification. No force pushes or deletion are allowed under active no-bypass branch ruleset #24751782.

~~~bash
python -m pip install "git+https://github.com/AETHERXGLOBAL/reprocert.git@v1"
~~~

For the immutable current release, prefer pinning `v1.0.0` or exact PyPI `==1.0.0` instead of a moving branch.

**Historical supported Alpha:** `v0.2.2a1` is immutable; the protected movable `v0.2` branch remains a rollback/legacy channel, not the current stable default.

## First published release

The first PyPI release was published as:

- package version: `0.2.2a1`
- GitHub release tag: `v0.2.2a1`
- channel: public alpha / pre-release

