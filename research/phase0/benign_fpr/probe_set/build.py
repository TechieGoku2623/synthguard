"""Build 220 designed benign FASTA records. No hazardous sequences."""

from __future__ import annotations

from pathlib import Path

from synthguard.dna import designed_orf, mutate, random_dna
from synthguard.fasta import FastaRecord, write_fasta
from synthguard.reference import PLASMID_BACKBONE

HERE = Path(__file__).resolve().parent

N_TARGET = 220


def build_records() -> list[FastaRecord]:
    records: list[FastaRecord] = []
    for i in range(50):
        diverged = mutate(PLASMID_BACKBONE, f"plasmid-div-{i}", substitutions=40 + (i % 20))
        records.append(FastaRecord(header=f"plasmid_div_{i:03d}", sequence=diverged))
    for i in range(50):
        records.append(
            FastaRecord(header=f"orf_{i:03d}", sequence=designed_orf(f"orf-probe-{i}", 40 + i % 10))
        )
    for _i, gc in enumerate((0.30, 0.50, 0.70)):
        for j in range(40):
            records.append(
                FastaRecord(
                    header=f"rand_gc{int(gc * 100)}_{j:03d}",
                    sequence=random_dna(f"rand-{gc}-{j}", 160 + j % 40, gc=gc),
                )
            )
    assert len(records) >= N_TARGET
    return records


def main() -> None:
    records = build_records()
    write_fasta(HERE / "benign_queries.fa", records)
    (HERE / "README.md").write_text(
        "# benign_fpr probe set\n\n"
        f"{len(records)} designed benign sequences. No hazardous sequences.\n",
        encoding="utf-8",
    )
    print(f"wrote {len(records)} benign queries")


if __name__ == "__main__":
    main()
