# Contributing to ReproCert

ReproCert accepts narrowly scoped, test-backed contributions that preserve explicit evidence and trust semantics.

## Development setup

```bash
git clone https://github.com/AETHERXGLOBAL/reprocert.git
cd reprocert
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
python -m build
```

## Before opening a pull request

1. Keep the change focused.
2. Add or update tests for changed behavior.
3. Run the reference example when execution/evidence behavior changes.
4. Update public documentation when an interface changes.
5. State any change to the trust boundary explicitly.

## Non-negotiable semantics

- `FAIL` means the declared claim check was false after a valid execution.
- `INCONCLUSIVE` means evidence could not be resolved or adjudicated.
- `ERROR` means the declared execution itself did not complete as specified.
- A certificate self-digest is not a producer signature.
- Producer authentication is not evidence-source truth.
- ReproCert does not adjudicate scientific truth.

## Security-sensitive changes

Changes affecting command execution, path handling, evidence resolution, signing/attestation, secrets, or workflow permissions require an explicit threat-model note in the pull request.

Do not include sensitive vulnerability details in a public pull request. Follow [SECURITY.md](SECURITY.md).

## Project direction

See [GOVERNANCE.md](GOVERNANCE.md) for decision rules and [ROADMAP.md](ROADMAP.md) for planned work.
