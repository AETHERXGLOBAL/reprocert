# Publishing ReproCert

## Package identity

PyPI package name:

aetherx-reprocert

Target install command:

~~~bash
python -m pip install aetherx-reprocert
~~~

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

Example:

package version: 0.2.2a1
release tag: v0.2.2a1

A mismatch fails before publication.

## Stable GitHub channel

The branch v0.2 is the stable public v0.2 action/install channel. It should move only to a commit that passed the full release gate.

~~~bash
python -m pip install "git+https://github.com/AETHERXGLOBAL/reprocert.git@v0.2"
~~~

## First published release

The first PyPI release was published as:

- package version: `0.2.2a1`
- GitHub release tag: `v0.2.2a1`
- channel: public alpha / pre-release

