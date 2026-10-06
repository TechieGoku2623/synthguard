from __future__ import annotations

from typer.testing import CliRunner

from synthguard.cli import app, repo_root

runner = CliRunner()


def test_demo_plan_lists_five_cases() -> None:
    result = runner.invoke(app, ["demo-plan", "--dry-run"])
    assert result.exit_code == 0
    assert "plasmid" in result.stdout
    assert "housekeep" in result.stdout
    assert "near-miss" in result.stdout
    assert "split-orders" in result.stdout
    assert "too-short" in result.stdout
    assert "DETECTION ONLY" in result.stdout
    assert "Dry run only" in result.stdout


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "synthguard" in result.stdout


def test_sample_path() -> None:
    result = runner.invoke(app, ["sample-path"])
    assert result.exit_code == 0
    assert "data/sample" in result.stdout
    assert (repo_root() / "CONTRIBUTING.md").is_file()
