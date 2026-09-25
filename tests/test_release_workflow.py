from pathlib import Path


def test_release_workflow_uses_live_github_expression() -> None:
    workflow = Path(".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "\\${{" not in workflow
    assert "RELEASE_TAG: ${{ github.event.release.tag_name }}" in workflow
