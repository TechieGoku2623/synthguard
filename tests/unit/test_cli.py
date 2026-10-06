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


def test_screen_plasmid_clears_with_hash() -> None:
    result = runner.invoke(app, ["screen", "--fasta", "data/sample/plasmid.fa"])
    assert result.exit_code == 0
    assert "CLEAR" in result.stdout
    assert "query_hash:" in result.stdout
    assert "decision log" in result.stdout
    assert "plasmid_backbone_puc_style" in result.stdout
    assert "auto-clear" in result.stdout
    assert "DETECTION ONLY" in result.stdout


def test_screen_near_miss_explain() -> None:
    result = runner.invoke(app, ["screen", "--fasta", "data/sample/near-miss.fa", "--explain"])
    assert result.exit_code == 0
    assert "CLEAR" in result.stdout
    assert "why not escalated" in result.stdout
    assert "threshold vs identity" in result.stdout
    assert "near-miss-benign-homolog" in result.stdout


def test_screen_too_short_does_not_clear() -> None:
    result = runner.invoke(app, ["screen", "--fasta", "data/sample/too-short.fa"])
    assert result.exit_code == 1
    assert "NOT SCREENABLE" in result.stdout or "NOT_SCREENABLE" in result.stdout
    assert "does NOT clear" in result.stdout
    assert "CLEAR: no" in result.stdout
    assert "CLEAR: yes" not in result.stdout


def test_orders_ingest_and_analyze() -> None:
    ingest = runner.invoke(app, ["orders", "ingest", "data/sample/split-orders/"])
    assert ingest.exit_code == 0
    assert "R001-frag1" in ingest.stdout
    analyze = runner.invoke(app, ["orders", "analyze", "--requester", "R001"])
    assert analyze.exit_code == 0
    assert "detected=True" in analyze.stdout
    assert "REASSEMBLY" in analyze.stdout


def test_eval_prints_tradeoff() -> None:
    result = runner.invoke(app, ["eval"])
    assert result.exit_code == 0
    assert "FPR" in result.stdout
    assert "unmeasured" in result.stdout
    assert "latency=" in result.stdout


def test_demo_walkthrough() -> None:
    result = runner.invoke(app, ["demo"])
    assert result.exit_code == 0
    assert "plasmid" in result.stdout.lower() or "CLEAR" in result.stdout
    assert "why not escalated" in result.stdout
    assert "NOT SCREENABLE" in result.stdout or "NOT_SCREENABLE" in result.stdout
    assert "REASSEMBLY" in result.stdout
    assert "FPR" in result.stdout
