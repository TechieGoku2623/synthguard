"""Write asciinema v2 JSONL recordings from real command output."""

from __future__ import annotations

import json
import time
from collections.abc import Sequence
from pathlib import Path

from typer.testing import CliRunner

from synthguard.cli import app
from synthguard.config import get_settings


def write_cast(
    path: Path, title: str, chunks: Sequence[str], width: int = 120, height: int = 40
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = {
        "version": 2,
        "width": width,
        "height": height,
        "timestamp": int(time.time()),
        "title": title,
        "env": {"SHELL": "/bin/bash", "TERM": "xterm-256color"},
    }
    lines = [json.dumps(header, separators=(",", ":"))]
    elapsed = 0.05
    for chunk in chunks:
        payload = chunk if chunk.endswith("\n") else f"{chunk}\n"
        lines.append(json.dumps([round(elapsed, 6), "o", payload], separators=(",", ":")))
        elapsed += 0.04
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run(args: list[str]) -> str:
    runner = CliRunner()
    result = runner.invoke(app, args)
    header = "$ synthguard " + " ".join(str(item) for item in args)
    body = result.stdout
    if result.exit_code != 0:
        body = f"{body}\n[exit {result.exit_code}]\n"
    return f"{header}\n{body}"


def record_all() -> list[Path]:
    demo_dir = get_settings().repo_root / "demo"
    jobs = (
        (
            "01-screen-and-clear.cast",
            "screen plasmid clear",
            _run(["screen", "--fasta", "data/sample/plasmid.fa"]),
        ),
        (
            "02-unscreenable.cast",
            "too-short is not screenable",
            _run(["screen", "--fasta", "data/sample/too-short.fa"]),
        ),
        (
            "03-split-order-graph.cast",
            "ingest and analyze R001",
            _run(["orders", "ingest", "data/sample/split-orders/"])
            + "\n"
            + _run(["orders", "analyze", "--requester", "R001"]),
        ),
        (
            "04-tradeoff-curve.cast",
            "benign FP/FN tradeoff",
            _run(["eval"]),
        ),
    )
    written: list[Path] = []
    for name, title, text in jobs:
        path = demo_dir / name
        write_cast(path, title, text.splitlines())
        written.append(path)
    return written
