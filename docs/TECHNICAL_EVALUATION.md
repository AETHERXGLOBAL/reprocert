# ReproCert — Technical Evaluation Pack v1

**Purpose:** give an external engineer one bounded, independently runnable path from public installation to machine-readable evidence in roughly 5–10 minutes.

**Status:** Public Alpha. This evaluation pack does not create an endorsement, certification, production-readiness claim, or independent-adoption claim.

## What this evaluation exercises

The path below checks the public PyPI distribution against ReproCert's own public test repository through the pytest-native adapter. It produces:

- an explicit generated claim;
- JUnit evidence;
- a ReproCert certificate;
- an independently repeatable verification step.

It is intentionally narrow. It demonstrates the claim-to-evidence workflow; it does not prove that ReproCert is suitable for every project or that a passing test suite is complete.

## 1. Clean evaluator environment

Requirements:

- Git;
- Python 3.11+;
- network access to GitHub and PyPI for acquisition only.

```bash
git clone --depth 1 https://github.com/AETHERXGLOBAL/reprocert.git
cd reprocert

python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install aetherx-reprocert pytest

reprocert --help >/dev/null
```

The command under evaluation is the installed public distribution, not an editable installation of the checkout.

## 2. Execute the bounded evaluation

```bash
reprocert pytest \
  --workdir . \
  --output technical-evaluation-certificate.json \
  -- -q
```

Expected top-level outcome on a healthy supported environment:

```text
PASS
```

The adapter also writes:

```text
.reprocert-pytest-claim.json
.reprocert-pytest-junit.xml
technical-evaluation-certificate.json
```

## 3. Verify the produced certificate

```bash
reprocert verify \
  technical-evaluation-certificate.json \
  --claim .reprocert-pytest-claim.json \
  --evidence-root .
```

The verification step is local. It does not call an AETHER X service.

## 4. Evidence to retain

For a reproducible evaluation record, retain or attach:

- `technical-evaluation-certificate.json`;
- `.reprocert-pytest-claim.json`;
- `.reprocert-pytest-junit.xml`;
- Python version;
- `reprocert` package version;
- repository commit SHA used for the evaluation.

Suggested environment capture:

```bash
python --version
python -m pip show aetherx-reprocert
git rev-parse HEAD
```

## 5. Negative-path review

A useful evaluator should inspect more than a happy path. ReproCert distinguishes:

- `PASS` — declared checks passed;
- `FAIL` — execution completed and a declared check was false;
- `INCONCLUSIVE` — execution completed but required evidence could not be adjudicated;
- `ERROR` — the declared execution could not run as specified.

For the exact semantics and additional examples, use:

- [`QUICKSTART_5_MIN.md`](./QUICKSTART_5_MIN.md)
- [`PYTEST.md`](./PYTEST.md)
- [`JUNIT.md`](./JUNIT.md)
- [`THREAT_MODEL.md`](./THREAT_MODEL.md)

## 6. What a successful run establishes

A successful run supports only a bounded statement such as:

> The evaluator independently installed the public ReproCert distribution, executed the declared public test scope, produced a machine-readable certificate, and verified that certificate against the recorded claim and evidence.

It does **not** establish:

- scientific truth;
- benchmark fairness;
- security of the evaluated software;
- test completeness;
- production readiness;
- third-party adoption;
- endorsement of AETHER X.

`CERTIFICATE INTEGRITY ≠ PRODUCER AUTHENTICITY ≠ SCIENTIFIC TRUTH`

`SELF-EVALUATION PASS ≠ INDEPENDENT ADOPTION`

## 7. Independent external evidence

If you are evaluating ReproCert from outside AETHER X and are willing to make the result public, preserve a link to your repository, CI run, certificate, or reproducible evaluation record.

The external-adoption program counts evidence only when it originates from or is confirmed by an independent repository or maintainer outside AETHER X. Stars, impressions, private praise, and AETHER X self-tests do not count as independent adoption evidence.

---

**Related tracking:** Issue #18 — Technical Evaluation Pack v1.