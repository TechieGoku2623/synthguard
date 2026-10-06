"""Phase 0 CLI. Full screening application is Phase 2."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from synthguard import SAFETY_DISCLAIMER, __version__
from synthguard.config import get_settings
from synthguard.logging import configure_logging
from synthguard.schemas import SampleCase

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console(width=140)

SAMPLES: tuple[SampleCase, ...] = (
    SampleCase(
        sample_id="plasmid",
        filename="plasmid.fa",
        path_exercised="known lab plasmid backbone fragment",
        why_present="Common lab backbone-style fragment. Must clear and annotate as known-benign.",
        expected_behavior="CLEAR. Identity 1.000 vs plasmid_backbone_puc_style. Not a hazard hit.",
    ),
    SampleCase(
        sample_id="housekeep",
        filename="housekeep.fa",
        path_exercised="human housekeeping-style ORF excerpt",
        why_present="Public-style housekeeping ORF. Clears and exercises ORF annotation.",
        expected_behavior="CLEAR. Annotation orf-like. No auto-flag.",
    ),
    SampleCase(
        sample_id="near-miss",
        filename="near-miss.fa",
        path_exercised="high homology to a benign relative",
        why_present="Designed homolog of the committed E. coli-like reference fragment.",
        expected_behavior="CLEAR. Identity below default threshold. Must NOT auto-flag.",
    ),
    SampleCase(
        sample_id="split-orders",
        filename="split-orders/",
        path_exercised="five overlapping fragments from requester R001",
        why_present="Reassembly detection vs normal multi-order customers.",
        expected_behavior=(
            "R001 detected. Unrelated benign fragments from other requesters are not."
        ),
    ),
    SampleCase(
        sample_id="too-short",
        filename="too-short.fa",
        path_exercised="below minimum screenable length",
        why_present="20 nt query when minimum is 50. Not screenable.",
        expected_behavior="NOT SCREENABLE. Non-zero exit. Does not clear.",
    ),
)


@app.callback()
def _main() -> None:
    configure_logging()


@app.command("version")
def version() -> None:
    """Print the package version."""

    console.print(f"synthguard {__version__}")


@app.command("demo-plan")
def demo_plan(
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run"),
) -> None:
    """List the five designed benign sample cases and the path each exercises."""

    settings = get_settings()
    console.print("[bold]synthguard designed sample cases[/bold]\n")
    console.print("DETECTION ONLY. No sequence generation or modification.\n")
    for sample in SAMPLES:
        console.print(f"[bold]{sample.sample_id}[/bold]  {sample.filename}")
        console.print(f"  path:     {sample.path_exercised}")
        console.print(f"  expected: {sample.expected_behavior}")
        console.print(f"  file:     {settings.sample_dir / sample.filename}")
        console.print()
    console.print(SAFETY_DISCLAIMER)
    if dry_run:
        console.print(
            "\nDry run only. A full `synthguard screen` CLI is Phase 2; "
            "this command exists so `make demo` can show that the sample set "
            "is designed, benign, and not a hazard catalog."
        )
    console.print(f"Sample directory: {settings.sample_dir}")


@app.command("sample-path")
def sample_path() -> None:
    """Print the committed sample directory path."""

    console.print(str(get_settings().sample_dir.resolve()))


def repo_root() -> Path:
    return get_settings().repo_root
