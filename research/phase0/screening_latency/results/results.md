# screening_latency results

Repeats per cell: 2. Panel = 3 committed benign refs + 20 decoys.

Decision: Local indexed backend is faster on this grid (indexed 1.5656s vs naive 1.5969s total). BLAST vs DIAMOND vs HMM remains deferred. BLAST RTT: unmeasured.

| query length | order volume | naive ms | indexed ms | speedup |
| --- | --- | --- | --- | --- |
| 50 | 1 | 6.68 | 6.55 | 1.02 |
| 50 | 10 | 65.27 | 65.72 | 0.99 |
| 50 | 25 | 163.71 | 176.26 | 0.93 |
| 100 | 1 | 7.60 | 7.64 | 0.99 |
| 100 | 10 | 76.01 | 77.83 | 0.98 |
| 100 | 25 | 190.12 | 192.47 | 0.99 |
| 200 | 1 | 1.73 | 1.47 | 1.18 |
| 200 | 10 | 16.82 | 16.58 | 1.01 |
| 200 | 25 | 41.94 | 42.11 | 1.00 |
| 400 | 1 | 28.23 | 27.69 | 1.02 |
| 400 | 10 | 283.87 | 273.19 | 1.04 |
| 400 | 25 | 714.95 | 678.05 | 1.05 |
