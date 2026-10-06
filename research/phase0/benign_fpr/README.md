# benign_fpr

## What is measured

False-positive rate of "identity ≥ T against the committed benign reference, treating that panel as a stand-in hit list" on 200+ designed benign sequences (plasmid-like diverged fragments, housekeeping-style ORFs, random DNA at known GC).

## Why it decides something

The default identity threshold for a later sequences-of-concern backend should keep FPR on ordinary lab DNA low. Phase 0 cannot and does not include a hazard database; this is a proxy on benign sequences only.

## How to run

```bash
uv run python research/phase0/benign_fpr/run.py
```

Seed: `synthguard-benign-fpr-v1`. Sequences are designed stand-ins, not live GenBank pulls.
