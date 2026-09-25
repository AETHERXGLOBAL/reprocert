from __future__ import annotations

from pathlib import Path

import pytest

from reprocert.claim import load_claim
from reprocert.doctor import run_doctor
from reprocert.init_project import InitError, initialize_project
from reprocert.runner import run_claim


def test_init_command_profile_is_immediately_runnable(tmp_path: Path) -> None:
    result = initialize_project(tmp_path, profile="command")
    assert result.profile == "command"
    assert "reprocert.yml" in result.created
    assert (tmp_path / ".reprocert" / "README.md").is_file()
    certificate = run_claim(load_claim(tmp_path / "reprocert.yml"))
    assert certificate["verdict"] == "PASS"


def test_init_auto_detects_pytest_and_generated_claim_runs(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "sample"\n'
        '[project.optional-dependencies]\n'
        'dev = ["pytest"]\n',
        encoding="utf-8",
    )
    (tmp_path / "test_sample.py").write_text(
        "def test_ok():\n    assert 6 * 7 == 42\n",
        encoding="utf-8",
    )
    result = initialize_project(tmp_path)
    assert result.profile == "pytest"
    certificate = run_claim(load_claim(tmp_path / "reprocert.yml"))
    assert certificate["verdict"] == "PASS"
    assert (tmp_path / "reprocert-junit.xml").is_file()


def test_init_can_generate_github_actions_workflow(tmp_path: Path) -> None:
    initialize_project(tmp_path, profile="command", github_actions=True)
    workflow = (
        tmp_path / ".github" / "workflows" / "reprocert.yml"
    ).read_text(encoding="utf-8")
    assert "AETHERXGLOBAL/reprocert@v0.2" in workflow
    assert "claim: reprocert.yml" in workflow


def test_init_refuses_overwrite_without_force(tmp_path: Path) -> None:
    initialize_project(tmp_path, profile="command")
    original = (tmp_path / "reprocert.yml").read_text(encoding="utf-8")
    with pytest.raises(InitError):
        initialize_project(tmp_path, profile="benchmark")
    assert (tmp_path / "reprocert.yml").read_text(encoding="utf-8") == original


def test_init_force_replaces_existing_scaffold(tmp_path: Path) -> None:
    initialize_project(tmp_path, profile="command")
    initialize_project(tmp_path, profile="benchmark", force=True)
    claim = (tmp_path / "reprocert.yml").read_text(encoding="utf-8")
    assert "benchmark-threshold" in claim


def test_doctor_passes_for_initialized_project(tmp_path: Path) -> None:
    initialize_project(tmp_path, profile="command")
    result = run_doctor(tmp_path)
    assert result["status"] == "PASS"
    by_name = {item["name"]: item for item in result["checks"]}
    assert by_name["python"]["status"] == "PASS"
    assert by_name["reprocert"]["status"] == "PASS"
    assert by_name["claim"]["status"] == "PASS"


def test_doctor_fails_for_invalid_claim(tmp_path: Path) -> None:
    (tmp_path / "reprocert.yml").write_text(
        "apiVersion: wrong\nkind: Nope\n",
        encoding="utf-8",
    )
    result = run_doctor(tmp_path)
    assert result["status"] == "FAIL"
    claim_check = next(
        item for item in result["checks"] if item["name"] == "claim"
    )
    assert claim_check["status"] == "FAIL"
