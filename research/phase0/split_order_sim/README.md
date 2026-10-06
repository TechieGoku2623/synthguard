# split_order_sim

## What is measured

Whether an overlap graph detects five overlapping fragments of one committed benign gene ordered by requester R001, without flagging normal multi-order customers who order unrelated benign fragments.

## Why it decides something

If R001 is detected and control requesters are not, split-order monitoring is in scope for Phase 2. If controls also fire, the overlap threshold is too loose.

## How to run

```bash
uv run python research/phase0/split_order_sim/run.py
```

Parent sequence is a designed benign ORF. No hazardous gene is used or named.
