"""Phase 0–3 CLI: screen, split-order graph, and benign tradeoff eval."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from synthguard import SAFETY_DISCLAIMER, __version__
from synthguard.config import get_settings
from synthguard.eval_curve import format_tradeoff, tradeoff_rows
from synthguard.logging import configure_logging
from synthguard.orders import (
    analyze_requester,
    default_store_path,
    ingest_directory,
    read_store,
    write_store,
)
from synthguard.schemas import SampleCase, ScreenResult
from synthguard.screen import screen_fasta_path

app = typer.Typer(no_args_is_help=True, add_completion=False)
orders_app = typer.Typer(no_args_is_help=True, add_completion=False)
app.add_typer(orders_app, name="orders")
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


def _disclaimer() -> None:
    console.print(SAFETY_DISCLAIMER)


def _print_result(result: ScreenResult, explain: bool) -> None:
    console.print(f"query: {result.query_id}")
    console.print(f"query_hash: {result.query_hash}")
    console.print(f"status: {result.status}  tier: {result.tier}  exit: {result.exit_code}")
    console.print(
        f"length: {result.length}  min_length: {result.min_length}  "
        f"identity: {result.max_identity:.3f}  threshold: {result.identity_threshold:.3f}"
    )
    if result.best_hit is not None:
        console.print(
            f"hit: {result.best_hit.reference_id}  "
            f"identity={result.best_hit.identity:.3f}  jaccard={result.best_hit.jaccard:.3f}"
        )
    else:
        console.print("hit: none")
    console.print("rules:")
    for rule in result.rules:
        console.print(f"  - {rule}")
    console.print("decision log:")
    for line in result.decision_log:
        console.print(f"  {line}")
    if explain:
        console.print("[bold]explain[/bold]")
        if result.status == "NOT_SCREENABLE":
            console.print(
                f"  not escalated to CLEAR: measured {result.length} < min {result.min_length}"
            )
        elif result.best_hit is not None:
            console.print(f"  hit: {result.best_hit.reference_id}")
            console.print(f"  rule: {result.annotation}")
            if result.max_identity < result.identity_threshold:
                console.print(
                    f"  why not escalated: identity {result.max_identity:.3f} "
                    f"< threshold {result.identity_threshold:.3f}"
                )
            else:
                console.print("  why not escalated: known-benign backbone is auto-clear")
            console.print(
                f"  threshold vs identity: {result.identity_threshold:.3f} vs "
                f"{result.max_identity:.3f}"
            )
    if result.status == "NOT_SCREENABLE":
        console.print("NOT SCREENABLE — this query does NOT clear.")
    queue = Table(title="Reviewer queue (above auto-clear)")
    queue.add_column("query")
    queue.add_column("tier")
    queue.add_column("reason")
    if result.tier != "auto-clear":
        reason = (
            f"measured {result.length} < min {result.min_length}"
            if result.status == "NOT_SCREENABLE"
            else result.annotation
        )
        queue.add_row(result.query_id, result.tier, reason)
        console.print(queue)
    else:
        console.print("Reviewer queue: empty (auto-clear).")
    for note in result.notes:
        console.print(f"  note: {note}")


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
    _disclaimer()
    if dry_run:
        console.print(
            "\nDry run only. Designed fixtures listed above. "
            "`make demo` runs screen, split-order analyze, and eval."
        )
    console.print(f"Sample directory: {settings.sample_dir}")


@app.command("sample-path")
def sample_path() -> None:
    """Print the committed sample directory path."""

    console.print(str(get_settings().sample_dir.resolve()))


def run_screen(fasta: Path, explain: bool = False) -> int:
    settings = get_settings()
    path = fasta if fasta.is_file() else settings.sample_dir / fasta.name
    if not path.is_file():
        raise typer.BadParameter(f"FASTA not found: {fasta}")
    console.print("[bold]synthguard screen[/bold]")
    console.print("DETECTION ONLY. No sequence generation or modification.")
    results = screen_fasta_path(path)
    exit_code = 0
    for result in results:
        _print_result(result, explain=explain)
        if result.status != "CLEAR":
            console.print("CLEAR: no")
        else:
            console.print("CLEAR: yes")
        exit_code = max(exit_code, result.exit_code)
    _disclaimer()
    return exit_code


@app.command("screen")
def screen(
    fasta: Annotated[Path, typer.Option("--fasta", help="FASTA query path")],
    explain: bool = typer.Option(False, "--explain"),
) -> None:
    """Screen a FASTA query. Detection only. Never rewrites the sequence."""

    raise typer.Exit(code=run_screen(fasta, explain=explain))


@orders_app.command("ingest")
def orders_ingest(
    path: Annotated[Path, typer.Argument(help="Directory of FASTA fragments")],
) -> None:
    """Ingest designed order fragments. Does not reconstruct a parent sequence."""

    settings = get_settings()
    fragments = ingest_directory(path)
    store = default_store_path(settings.repo_root)
    write_store(store, fragments)
    console.print("[bold]synthguard orders ingest[/bold]")
    console.print(f"directory: {path}")
    console.print(f"fragments: {len(fragments)}  store: {store}")
    for item in fragments:
        console.print(
            f"  {item.order_id}  requester={item.requester_id}  length={len(item.sequence)}"
        )
    console.print("Detection only. Ingest stores fragments; it does not emit a gene.")
    _disclaimer()


@orders_app.command("analyze")
def orders_analyze(
    requester: str = typer.Option(..., "--requester"),
) -> None:
    """Flag overlapping fragments from one requester. No assembler output."""

    settings = get_settings()
    store = default_store_path(settings.repo_root)
    fragments = read_store(store)
    detection = analyze_requester(fragments, requester)
    console.print("[bold]synthguard orders analyze[/bold]")
    console.print(f"requester: {requester}")
    console.print(
        f"detected={detection.detected}  fragments={detection.n_fragments}  "
        f"edges={detection.n_edges}  reconstructed_fraction="
        f"{detection.reconstructed_fraction:.3f}"
    )
    console.print(f"notes: {detection.notes}")
    table = Table(title="Reviewer queue (graph reassembly)")
    table.add_column("requester")
    table.add_column("flag")
    table.add_column("fragments")
    table.add_column("edges")
    table.add_column("reconstructed")
    table.add_row(
        detection.requester_id,
        "REASSEMBLY" if detection.detected else "none",
        str(detection.n_fragments),
        str(detection.n_edges),
        f"{detection.reconstructed_fraction:.3f}",
    )
    console.print(table)
    if detection.detected:
        console.print(
            "Graph reassembly flag: overlapping tiles from one requester. "
            "The parent sequence is not emitted."
        )
    _disclaimer()


@app.command("eval")
def eval_cmd() -> None:
    """Print FP/FN tradeoff on the benign corpus plus screening latency."""

    rows, elapsed, n = tradeoff_rows()
    console.print(format_tradeoff(rows, elapsed, n))
    _disclaimer()


@app.command("demo")
def demo() -> None:
    """Full walkthrough on committed benign samples. No credentials."""

    settings = get_settings()
    console.print("[bold]synthguard demo — Phase 0–3 walkthrough[/bold]\n")
    plasmid_code = run_screen(settings.sample_dir / "plasmid.fa", explain=False)
    if plasmid_code != 0:
        raise typer.Exit(code=plasmid_code)
    console.print()
    near_code = run_screen(settings.sample_dir / "near-miss.fa", explain=True)
    if near_code != 0:
        raise typer.Exit(code=near_code)
    console.print()
    short_code = run_screen(settings.sample_dir / "too-short.fa", explain=False)
    if short_code != 1:
        raise typer.Exit(code=short_code or 1)
    console.print("too-short exited 1 as required (NOT SCREENABLE, does not clear).")
    console.print()
    orders_ingest(path=settings.split_order_dir)
    console.print()
    orders_analyze(requester="R001")
    console.print()
    eval_cmd()


def repo_root() -> Path:
    return get_settings().repo_root
