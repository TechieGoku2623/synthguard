# screening_latency

## What is measured

Wall time of the local Python k-mer-prefilter homology backend versus a naive all-pairs identity scan, at several query lengths and order volumes. Queries are synthetic benign DNA.

## Why it decides something

BLAST vs DIAMOND vs HMM is deferred. Phase 0 only decides whether the local backend is fast enough for demo-scale volumes, and whether the k-mer prefilter beats naive scan.

## How to run

```bash
uv run python research/phase0/screening_latency/run.py
```

API / BLAST RTT: unmeasured (not invoked).
