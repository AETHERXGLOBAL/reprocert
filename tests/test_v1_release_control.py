from __future__ import annotations

from pathlib import Path

import tomllib
import yaml


def test_release_workflow_binds_tag_version_and_main_source() -> None:
    workflow = Path(".github/workflows/release.yml").read_text(encoding="utf-8")

    assert "types: [published]" in workflow
    assert "RELEASE_TAG: ${{ github.event.release.tag_name }}" in workflow
    assert 'expected = f"v{version}"' in workflow
    assert 'git fetch --no-tags origin main' in workflow
    assert 'released="$(git rev-parse HEAD)"' in workflow
    assert 'current_main="$(git rev-parse FETCH_HEAD)"' in workflow
    assert 'test "$released" = "$current_main"' in workflow
    assert "persist-credentials: false" in workflow
    assert "fetch-depth: 0" in workflow


def test_release_workflow_uses_trusted_publishing_and_pinned_actions() -> None:
    workflow = Path(".github/workflows/release.yml").read_text(encoding="utf-8")

    assert "environment:\n      name: pypi" in workflow
    assert "id-token: write" in workflow
    assert "PYPI_TOKEN" not in workflow
    assert "pypa/gh-action-pypi-publish@dc37677b2e1c63e2034f94d8a5b11f265b73ba33" in workflow
    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in workflow
    assert "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97" in workflow
    assert "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a" in workflow
    assert "actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c" in workflow


def test_release_candidate_identity_is_not_stable_public_version_yet() -> None:
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["version"] == "1.0.0rc1"
    assert "Development Status :: 4 - Beta" in data["project"]["classifiers"]


def test_action_contract_remains_stable_and_bounded() -> None:
    action = yaml.safe_load(Path("action.yml").read_text(encoding="utf-8"))

    assert set(action["inputs"]) == {"claim", "certificate", "python-version"}
    assert action["inputs"]["claim"]["required"] is True
    assert action["inputs"]["certificate"]["default"] == "reprocert-certificate.json"
    assert set(action["outputs"]) == {"verdict", "certificate", "certificate-digest"}
    assert action["runs"]["using"] == "composite"
