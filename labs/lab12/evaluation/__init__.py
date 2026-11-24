"""Stage 14 Phase B PREPARATION -- final evaluation infrastructure.

**This package implements the machinery for the 2015 Protected Test final
evaluation. It does NOT execute it.** No module here is imported by
`api/app.py`, by any pytest collection outside `tests/stage14_evaluation/`,
or by the Stage 14 notebook's normal cells -- the only way to reach the
Protected Test is `evaluation.cli`'s explicit `unlock` subcommand, which
this preparation task does not invoke (see `gate.py`, `cli.py`).

Responsibilities (one small module each, no shared base classes beyond
what the problem needs):

- `contracts.py`   -- frozen constants, exceptions, metric/baseline specs.
- `population.py`  -- development (2006-2013) and protected (2015)
                       population loaders. The protected loader is only
                       ever called from `runner.py`'s unlock-gated path.
- `baselines.py`    -- B1 (Global Mean), B4 (Hierarchical Median),
                       fit/predict, recovered from Stage 08/11.
- `metrics.py`      -- MAE/RMSE/WAPE/Bias/Median AE/P90/P95/high-cost
                       metrics, recovered from Stage 08/11.
- `acceptance.py`   -- technical (not business-SLA) acceptance classification.
- `freeze.py`       -- evaluation-code fingerprint + freeze manifest v2.
- `gate.py`         -- PreUnlockGate: every check that must pass before
                       any 2015 row is read.
- `runner.py`       -- FinalEvaluationRunner: the actual Phase B logic,
                       reachable only through `gate.py`.
- `cli.py`          -- the explicit, separate unlock command.
"""
