"""Run every Phase 0 harness and regenerate the memo and evaluation tables."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from synthguard.config import get_settings
from synthguard.samples import write_sample_tree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HARNESSES = (
    HERE / "benign_fpr" / "probe_set" / "build.py",
    HERE / "benign_fpr" / "run.py",
    HERE / "screening_latency" / "run.py",
    HERE / "split_order_sim" / "probe_set" / "build.py",
    HERE / "split_order_sim" / "run.py",
    HERE / "render_docs.py",
)


def main() -> None:
    write_sample_tree(get_settings().sample_dir)
    for script in HARNESSES:
        print(f"\n=== {script.relative_to(ROOT)} ===\n")
        subprocess.run([sys.executable, str(script)], check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
