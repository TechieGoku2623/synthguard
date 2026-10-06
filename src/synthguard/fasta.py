"""Minimal FASTA reader/writer. Detection only; no sequence design helpers."""

from __future__ import annotations

from pathlib import Path

from synthguard.schemas import FastaRecord


def parse_fasta(text: str) -> list[FastaRecord]:
    records: list[FastaRecord] = []
    header: str | None = None
    chunks: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                records.append(FastaRecord(header=header, sequence="".join(chunks).upper()))
            header = line[1:].strip() or "unnamed"
            chunks = []
        else:
            chunks.append("".join(ch for ch in line.upper() if ch in {"A", "C", "G", "T", "N"}))
    if header is not None:
        records.append(FastaRecord(header=header, sequence="".join(chunks).upper()))
    return records


def read_fasta(path: Path) -> list[FastaRecord]:
    return parse_fasta(path.read_text(encoding="utf-8"))


def write_fasta(path: Path, records: list[FastaRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for record in records:
        lines.append(f">{record.header}")
        seq = record.sequence
        for i in range(0, len(seq), 80):
            lines.append(seq[i : i + 80])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
