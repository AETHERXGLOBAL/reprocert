# Troubleshooting

## Doctor shows WARN for Git

Local ReproCert execution does not require Git. The warning means the directory is not a Git work tree or Git is unavailable.

## Docker is missing

Docker is optional unless the claim contains a container profile or you run:

~~~bash
reprocert doctor --require-docker
~~~

## Verdict is FAIL

Execution completed and at least one declared check was false.

~~~bash
reprocert inspect reprocert-certificate.json
~~~

## Verdict is ERROR

The declared execution did not complete as specified. Common causes include an executable not being found, timeout, unexpected exit code, or unavailable container runtime.

## Verdict is INCONCLUSIVE

Execution completed, but required evidence could not be resolved or evaluated. Check evidence paths, JSON pointers, JUnit files, and permissions.

## init refuses to write

ReproCert does not overwrite an existing scaffold by default. If replacement is intentional:

~~~bash
reprocert init pytest --github-actions --force
~~~

## My project does not use pip

Replace the generated dependency-install step with uv, Poetry, Hatch, PDM, Conda, or your existing setup. The ReproCert action remains independent.

## Windows

The normal CLI, pytest/JUnit integration, policy layer, init, doctor, and GitHub Action are tested on Windows.

The hardened Docker execution profile has a narrower POSIX-host support boundary.

## I still need help

Self-service usage is the default. The Adoption / Integration issue form is optional for unusual CI, evidence, or policy requirements.
