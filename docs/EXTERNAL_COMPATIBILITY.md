# External Compatibility Lab

ReproCert validates selected public integrations against real open-source repositories before asking maintainers to adopt anything.

This is deliberately **not** described as third-party adoption. The external project has not endorsed or merged ReproCert unless its maintainers explicitly do so.

## pytest-django-queries

Target:

https://github.com/NyanKiyoshi/pytest-django-queries

Pinned compatibility commit:

`d9ef71f281db2498c614986c5dbacd2592923f54`

Why this is a useful fit:

- the project is a real pytest/Django performance-reporting plugin;
- its example application produces the existing `.pytest-queries` machine-readable report;
- its README currently contains an **Integrating with GitHub — TBA** section;
- ReproCert can wrap that existing evidence without changing the plugin.

The lab reproduces the example consumer environment, runs the existing example tests, and requires:

- zero JUnit failures;
- zero JUnit errors;
- a non-empty `.pytest-queries` report.

It then verifies the ReproCert certificate against the local claim and evidence and uploads the proof bundle.

## Boundary

A passing lab means:

**ReproCert interoperated successfully with the pinned public version of that repository under the declared CI environment.**

It does not mean:

- the external maintainer adopted ReproCert;
- the project endorses AETHER X;
- ReproCert certifies the benchmark methodology;
- compatibility is guaranteed for future commits.

The workflow runs weekly after merge so compatibility evidence does not silently become stale.
