from __future__ import annotations

from pathlib import Path

from synthguard.fasta import parse_fasta, read_fasta, write_fasta
from synthguard.schemas import FastaRecord


def test_parse_and_round_trip(tmp_path: Path) -> None:
    text = ">one desc\nacgtNNNN\n\n>two\nTTG\nAA\n"
    records = parse_fasta(text)
    assert records[0].header == "one desc"
    assert records[0].sequence == "ACGTNNNN"
    assert records[1].sequence == "TTGAA"
    path = tmp_path / "x.fa"
    write_fasta(path, records)
    again = read_fasta(path)
    assert again[0].sequence == "ACGTNNNN"
    assert FastaRecord(header="h", sequence="AC").length == 2
