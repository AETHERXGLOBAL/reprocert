# 5-Minute Start

ReproCert is designed to work without an AETHER X account, API key, hosted service, or approval.

## 1. Install

Install from PyPI:

~~~bash
python -m pip install aetherx-reprocert
~~~

Alternative stable GitHub channel:

~~~bash
python -m pip install "git+https://github.com/AETHERXGLOBAL/reprocert.git@v0.2"
~~~

## 2. Initialize your project

For pytest:

~~~bash
reprocert init pytest --github-actions
~~~

For a normal command:

~~~bash
reprocert init command --github-actions
~~~

For a benchmark:

~~~bash
reprocert init benchmark --github-actions
~~~

Or let ReproCert conservatively auto-detect pytest:

~~~bash
reprocert init --github-actions
~~~

ReproCert refuses to overwrite generated files unless you explicitly pass --force.

## 3. Check readiness

~~~bash
reprocert doctor
~~~

Doctor checks Python, the claim, project write access, Git availability, optional Docker availability, and whether the generated GitHub Actions workflow exists.

WARN and INFO entries do not fail Doctor. A required-condition failure does.

## 4. Run

~~~bash
reprocert run reprocert.yml -o reprocert-certificate.json
~~~

You receive one explicit verdict:

PASS / FAIL / INCONCLUSIVE / ERROR

## 5. Verify locally

~~~bash
reprocert verify reprocert-certificate.json --claim reprocert.yml --evidence-root .
~~~

This verification does not call AETHER X.

## Existing pytest project with no scaffold

~~~bash
reprocert pytest --workdir . --output pytest-certificate.json -- -q
~~~
