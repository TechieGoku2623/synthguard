# Phase 0 harnesses

`make research` runs these in order:

1. Rewrite `data/sample/` benign fixtures from committed seeds
2. `benign_fpr/probe_set/build.py` — rebuild 200+ designed benign sequences
3. `benign_fpr/run.py` — FPR across homology thresholds
4. `screening_latency/run.py` — indexed vs naive backend timing
5. `split_order_sim/probe_set/build.py` — R001 fragments vs multi-order controls
6. `split_order_sim/run.py` — reassembly detection
7. `render_docs.py` — write memo, evaluation, data, and README tables

No number in the memo is typed by hand. If a quantity cannot be produced here, the memo says **unmeasured** and names the measurement that would settle it.

Detection only. No harness generates a customer sequence or a sequences-of-concern database.
