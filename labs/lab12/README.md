# LAB 12 — Freight Cost Prediction PoC (Stage 01–05)

## Overview

- **Module:** LAB12 — End-to-End Freight Cost Prediction PoC
- **Current Scope:** Stage 01 (Business Understanding), Stage 02 (Data Acquisition, Schema &
  Versioning), Stage 03 (Data Quality Audit & Dataset Qualification), Stage 03.5
  (Shipment-Level Dataset Contract, Reference Resolution & Qualification Gate Review), Stage 04
  (Evidence-Based Exploratory Data Analysis & Statistical Engineering), and **Stage 05**
  (Temporal & Group-Aware Data Splitting, Cross-Validation Design & Evaluation Contract) — out
  of 14 planned stages. No modeling, preprocessing, feature engineering, or estimator training
  is performed here — Stage 05's output is an **evaluation protocol**, not a model.
- **Audience:** Participants who have completed LAB02–LAB11

This is a production-oriented capstone that combines the statistical/engineering discipline
from the previous 11 labs into a real dataset-qualification exercise. The guiding principle:
**Hypothesis → Statistical Evidence → Comparative Analysis → Engineering Decision → Validation
→ Documentation.**

## Learning Objectives

By the end of Stage 01–03, participants will be able to:

1. Frame a business prediction problem and its prediction-time boundary explicitly.
2. Audit a raw, messy real-world CSV without assuming its filename, encoding, or schema.
3. Distinguish true missing values from sentinel/placeholder text values.
4. Classify a target column's raw values into real, evidence-based categories (not fabricated
   labels) before applying `pd.to_numeric`.
5. Investigate observation granularity (row vs. shipment) before assuming independence.
6. Detect and interpret selection bias in a target-availability subset.
7. Produce a documented, evidence-based dataset qualification decision (GO / CONDITIONAL GO /
   NO-GO) — including the option to say "not yet," which is itself a valid engineering outcome.

## Dataset

**SCMS Delivery History Dataset — 20150929** (`data/freight_cost/
SCMS_Delivery_History_Dataset_20150929.csv`), 10324 rows × 33 columns. Source: USAID/SCMS
Delivery History family; Kaggle reference:
[apoorvwatsky/supply-chain-shipment-pricing-data](https://www.kaggle.com/datasets/apoorvwatsky/supply-chain-shipment-pricing-data).
No separate data dictionary file ships with the data — a provisional one is built in the
notebook from the schema itself. File encoding is **latin-1** (UTF-8 fails on a real byte in
the `Country` column, e.g. `Côte d'Ivoire`), auto-detected rather than assumed.

## Business Problem

**Freight Cost Prediction** — estimate a future shipment's freight cost (USD) from information
available before the shipment, for Pre-Shipment Cost Estimation. See
[`docs/business_problem.md`](docs/business_problem.md) for the full framing, prediction-time
feature-availability table, and open questions.

## Key Real Findings (not assumed, measured in the notebook)

- **Target structure:** `Freight Cost (USD)` splits into exactly 4 real categories summing to
  10324 rows: Numeric Positive (6198), Freight Included in Commodity Cost (1442), Reference to
  Another Shipment (2445), Invoiced Separately (239). Zero `Unrecognized` values.
- **Observation granularity:** Rows are line items; `ASN/DN #` identifies the physical shipment
  (7030 unique groups). Crucially, **no multi-row ASN/DN group has more than 1 numeric Freight
  Cost row** — Freight Cost is a shipment-level total, recorded once, with sibling rows
  explicitly referencing it (`"See ASN/DN-xxxx (ID#:yyyy)"`).
- **Selection bias:** Numeric-target coverage ranges from ~21% (Vendor INCO Term = DDP) to ~89%
  (FCA) at the **row level** — explained by INCOTERM semantics (DDP bundles freight into the
  commodity price), not random missingness. *(Stage 03.5 re-measured this at the shipment
  level: the gap narrows — DDP rises to ~49.2% — but does not disappear; see below.)*
- **Temporal feasibility:** `Scheduled Delivery Date` parses at 100%, spans 2006–2015, and is
  consistent within each shipment group — a viable, group-aware chronological-split candidate
  for a future stage, with 2015 flagged as a likely partial year.
- **Weight vs. Freight Cost:** weak linear correlation (0.23) but strong log-log correlation
  (0.73) on valid paired records — real signal, but Weight's prediction-time availability
  (planned vs. measured) could not be verified from this dataset.

## Dataset Qualification Decision

**CONDITIONAL GO** (Stage 01-03), **re-reviewed and still CONDITIONAL GO after Stage 03.5** —
see below. Full Stage 01-03 rationale, the 8-dimension assessment (Q1–Q8), and the original 5
conditions are in [`docs/dataset_qualification.md`](docs/dataset_qualification.md). The
engineering decisions (D-001–D-012, including the Stage 03.5 updates) are in
[`docs/engineering_decisions.md`](docs/engineering_decisions.md).

## Stage 03.5 — Shipment-Level Dataset Contract & Qualification Gate Review

A focused follow-up notebook (`lab12_stage03_5_shipment_contract.ipynb`) reconciled every
Stage 01-03 statistic against the raw CSV (all matched exactly) and resolved the three open
decisions left pending after Stage 03:

- **Reference Resolution:** Every one of the 2445 `"See ASN/DN-xxxx (ID#:yyyy)"` reference rows
  was parsed and structurally resolved — **100% resolution rate**, 0 missing anchors, 0
  cross-shipment references. (2340 resolve to a numeric anchor, 105 resolve to a valid
  non-numeric `"Invoiced Separately"` anchor — not an error.)
- **Row-level vs. shipment-level coverage:** The Stage 03 row-level coverage (60.03%)
  understated true data availability — recomputed at the correct observation unit (shipment),
  coverage is **88.17%** (6198 of 7030 shipments have at least one numeric Freight Cost row).
- **D-005 (modeling unit) — now Accepted:** Shipment-Level Modeling, based on concrete evidence
  (0 shipments with >1 numeric anchor; `Shipment Mode`/`Vendor INCO Term` are 100%
  single-valued within every shipment).
- **D-006 (Weight) — Partially Resolved:** correlation re-verified (0.23 linear / 0.73
  log-log); availability remains `Unknown` — Weight is excluded from the default feature set.
- **D-007 (temporal split) — downgraded from Accepted to Conditional:** 10 of 7030 shipments
  have an internally inconsistent `Scheduled Delivery Date`, and 2015's monthly row counts
  confirm a genuine partial year (collapsing after September).
- **Selection bias — reconciled at the shipment level:** the INCOTERM gap narrows but persists
  (e.g. DDP: 21.0% row-level → 49.2% shipment-level, still well below EXW/FCA's ~93%).

Full detail: [`docs/shipment_data_contract.md`](docs/shipment_data_contract.md) and
[`docs/qualification_gate_resolution.md`](docs/qualification_gate_resolution.md).

## Running with Docker

From the project root:

```powershell
docker compose up --build -d
```

Check logs for the JupyterLab access URL and token:

```powershell
docker compose logs ml-lab
```

## Opening the Notebooks

Open `http://localhost:8888`, then navigate to `labs/lab12/
lab12_stage01_03_dataset_qualification.ipynb` (Stage 01-03), `labs/lab12/
lab12_stage03_5_shipment_contract.ipynb` (Stage 03.5), `labs/lab12/
lab12_stage04_evidence_based_eda.ipynb` (Stage 04), or `labs/lab12/
lab12_stage05_temporal_group_splitting.ipynb` (Stage 05) — each later notebook reconciles
against the previous stage's real artifacts, so earlier notebooks should be run first.

## Generated Artifacts

Written to `labs/lab12/artifacts/` (gitignored — not committed):

- **Stage 01-03:** `dataset_profile.json`, `data_quality_report.csv`,
  `target_coverage_report.csv`, `target_value_categories.csv`, `feature_availability_audit.csv`,
  `shipment_granularity_report.json`, `qualification_summary.json`.
- **Stage 03.5:** `stage03_5_dataset_reconciliation.json`, `shipment_group_profile.csv`,
  `reference_resolution_summary.csv`, `target_coverage_by_granularity.csv`,
  `incoterm_coverage_reconciliation.csv`, `shipment_field_consistency.csv`,
  `aggregation_semantics_audit.csv`, `stage03_5_qualification_gate.json`.
- **Stage 04:** `stage04_eda_protocol.json`, `stage04_population_profile.json`,
  `stage04_target_statistics.json`, `stage04_numeric_associations.csv`,
  `stage04_categorical_segments.csv`, `stage04_outlier_diagnostics.csv`,
  `stage04_temporal_diagnostics.csv`, `stage04_feature_eligibility.csv`,
  `stage04_preprocessing_hypotheses.csv`, `stage04_statistical_evidence.csv`,
  `stage04_qualification_gate.json` (none contain any Protected Future target value — asserted
  in the notebook).
- **Stage 05:** `stage05_split_metadata.json`, `stage05_split_manifest.csv`,
  `stage05_training_population_profile.json`, `stage05_cv_fold_manifest.csv`,
  `stage05_cv_fold_summary.csv`, `stage05_group_integrity_report.json`,
  `stage05_temporal_integrity_report.json`, `stage05_leakage_audit.json`,
  `stage05_evaluation_contract.json`, `stage05_protocol_fingerprint.json` (none contain any
  Validation/Protected-Test target value — asserted via explicit string-absence checks).

None contain PII — the raw CSV has none (`ASN/DN #` is an internal operational identifier, not
personal data). The original CSV is never modified.

## Documentation

- [`docs/business_problem.md`](docs/business_problem.md) — Stage 01 deliverable.
- [`docs/dataset_qualification.md`](docs/dataset_qualification.md) — Stage 03 final
  GO/CONDITIONAL GO/NO-GO decision.
- [`docs/engineering_decisions.md`](docs/engineering_decisions.md) — D-001 through D-032
  decision registry, including the Stage 03.5, Stage 04, and Stage 05 updates and still-open
  items.
- [`docs/stage04_eda_findings.md`](docs/stage04_eda_findings.md) — Stage 04 full findings
  report (18 sections).
- [`docs/stage06_preprocessing_experiment_plan.md`](docs/stage06_preprocessing_experiment_plan.md)
  — technical requirements for Stage 06, with no preprocessing pipeline chosen yet.
- [`docs/stage05_split_strategy.md`](docs/stage05_split_strategy.md),
  [`docs/stage05_evaluation_contract.md`](docs/stage05_evaluation_contract.md),
  [`docs/stage05_leakage_risk_register.md`](docs/stage05_leakage_risk_register.md) — Stage 05
  split design, evaluation contract, and 13-risk leakage register.
- [`docs/shipment_data_contract.md`](docs/shipment_data_contract.md) — Stage 03.5 canonical
  shipment-level dataset contract.
- [`docs/qualification_gate_resolution.md`](docs/qualification_gate_resolution.md) — Stage
  03.5's review of the 5 original CONDITIONAL GO conditions.

## Limitations

- Target semantics (realized vs. quoted cost) cannot be fully verified from this dataset.
- Weight (Kilograms) prediction-time availability remains an open question (D-006, Partially
  Resolved) — excluded from the default feature set as a safe policy.
- Line Item Quantity/Value aggregation across differing product types remains `Pending` (D-010).
- Numeric-target subset is not representative of the full population — confirmed at both
  row-level and shipment-level (INCO-Term-driven selection bias, narrower but persistent at the
  shipment level).
- 2015 is a confirmed partial year (row counts collapse after September); 10 of 7030 shipments
  have an internally inconsistent `Scheduled Delivery Date` (D-007, downgraded to Conditional).

## Stage 04 — Evidence-Based EDA & Statistical Engineering

A third notebook (`lab12_stage04_evidence_based_eda.ipynb`) performs a leakage-safe
exploratory analysis under a fixed **EDA Isolation Protocol**: a cutoff date (2013-12-31,
chosen before looking at the target distribution) splits shipments into an EDA-eligible
historical population and a Protected Future population that is **never** used in any
target-dependent analysis (asserted explicitly in the notebook).

- **Target distribution** (Population C, n=4987): strongly right-skewed and heavy-tailed
  (skewness≈5.36, excess kurtosis≈53.9); mean (~10456 USD) is ~1.8x the median (~5820 USD).
- **Weight (Kilograms):** confirmed nonlinear/monotonic signal (Pearson r≈0.14, Spearman
  ρ≈0.73) — still diagnostic-only per D-006; prediction-time availability remains unverified.
- **Line Item Quantity/Value (shipment sums):** moderate-to-strong Spearman correlations
  (ρ≈0.64 / ρ≈0.70) — prediction-time available, but the cross-product-type summation rule
  (D-010) is still Pending.
- **Selection bias:** the INCOTERM-driven gap found in Stage 03.5 is **reconfirmed within the
  historical population alone** — a stronger, independent piece of evidence.
- **Temporal stability:** median Freight Cost rose ~2.7x from 2006 to 2013, and numeric-target
  coverage rose from ~82.7% to ~96.0% over the same period — a real historical trend, not
  claimed as a guaranteed future trend.
- **No preprocessing was chosen.** Instead, a 5-experiment matrix (EXP-01–EXP-05) proposes
  testable comparisons for Stage 06 (target transformation, scaling, Weight inclusion,
  categorical encoding, outlier treatment), each planned on the same CV folds across at least
  one linear and one tree-based model.

Full detail: [`docs/stage04_eda_findings.md`](docs/stage04_eda_findings.md) and
[`docs/stage06_preprocessing_experiment_plan.md`](docs/stage06_preprocessing_experiment_plan.md).

## Stage 05 — Temporal & Group-Aware Data Splitting

A fourth notebook (`lab12_stage05_temporal_group_splitting.ipynb`) freezes the evaluation
protocol that Stage 06–14 must not arbitrarily change. Split membership is assigned **purely
from the temporal field (never from the target)**, and Stage 04's EDA cutoff is preserved
exactly as the Training boundary (`assert`-verified in the notebook).

| Split | Range | Shipments | Numeric-Eligible |
|---|---|---:|---:|
| Training | < 2014-01-01 | 5551 | 4987 |
| Validation | 2014-01-01 – 2014-12-31 | 910 | 819 (not inspected in Stage 05) |
| Protected Test | ≥ 2015-01-01 (real max: 2015-12-31) | 569 | 392 (not inspected in Stage 05) |

- **Group isolation:** 0 `ASN/DN #` overlap across splits, 0 overlap in any CV fold, and 0
  cross-shipment cost-anchor dependency (Stage 03.5's reference resolution reconfirmed) — no
  connected-component grouping layer was needed.
- **Cross-validation:** Expanding-window, 4 folds (validation years 2010–2013), entirely
  inside the Training period, group- and calendar-aware, `gap_days=0` by default.
- **Label availability:** no real freight-settlement timestamp exists in this dataset;
  `Scheduled Delivery Date` is used only as a chronological proxy. D-007 remains **Conditional**
  — it was explicitly **not** upgraded to Accepted.
- **7 invariants** (no group overlap, correct chronological ordering, 0 contract violations,
  EDA-cutoff/Train-boundary match, etc.) all verified PASS in the notebook.
- **Reproducibility:** a deterministic protocol fingerprint (dataset hash + boundaries + fold
  boundaries + grouping/gap policy, excluding any runtime timestamp) was confirmed stable
  across recomputation.
- **No target value for Validation or Protected Test was read anywhere in this notebook** —
  verified by an explicit string-absence check on every artifact written.

Full detail: [`docs/stage05_split_strategy.md`](docs/stage05_split_strategy.md),
[`docs/stage05_evaluation_contract.md`](docs/stage05_evaluation_contract.md), and
[`docs/stage05_leakage_risk_register.md`](docs/stage05_leakage_risk_register.md) (13 tracked
risks).

## Stage 06 — Evidence-Based Data Preprocessing & Controlled Experiments

A fifth notebook (`lab12_stage06_evidence_based_preprocessing.ipynb`) re-verifies Stage 05's
frozen protocol fingerprint, then runs 5 one-factor-at-a-time controlled experiments
(EXP-01…EXP-05) across Stage 05's frozen 4-fold Expanding-Window CV, using two fixed
"probe" estimators (Ridge `alpha=10.0`, RandomForestRegressor `n_estimators=80`). All
preprocessing is fit on fold-training data only; 2014/2015 targets are never read.

| Experiment | Dimension | Decision |
|---|---|---|
| EXP-01 | Missing Value Handling | Inconclusive / Deferred (0% real missing in main features) |
| EXP-02 | Categorical Encoding | **Accepted:** OneHot + rare-category grouping; Ordinal rejected |
| EXP-03 | Feature Scaling | Model-Dependent: irrelevant for RF, MinMaxScaler acceptable for Ridge |
| EXP-04 | Outlier Treatment | Mixed: quantile capping helps Ridge, inconclusive for RF |
| EXP-05 | Target Transformation | Model-Dependent: **rejected for Ridge** (retransformation bias), acceptable for RF |

- **Headline finding:** applying `log`/`log1p` to the target and inverse-transforming back
  to USD causes Ridge's pooled MAE to jump from **8,001.52 USD to 59,303.40 USD** (~7.4x
  worse) — a dramatic, measured instance of the retransformation bias risk discussed in Stage 06. Random Forest, by contrast, improves marginally under
  the same transform.
- **124 total CV fits** across all experiments; validated first as a plain Python script
  (66.7s) to isolate pipeline-logic correctness from Jupyter-kernel execution overhead,
  then executed end-to-end on a clean kernel both locally and inside Docker (0 errors, 0
  warnings in both).
- **Leakage audit:** all 91,056 out-of-fold prediction rows verified (programmatically) to
  belong only to the Training split; reproducibility verified by refitting the reference
  pipeline twice and confirming identical predictions.
- 4 Advanced Challenges: Weight_KG missingness sensitivity (D-006), rare-category threshold
  sensitivity, scaling–estimator interaction, and log-target tail (P90+) error behavior.

Full detail: [`docs/stage06_preprocessing_evidence.md`](docs/stage06_preprocessing_evidence.md),
[`docs/stage06_experiment_results.md`](docs/stage06_experiment_results.md), and
[`docs/stage06_preprocessing_contract.md`](docs/stage06_preprocessing_contract.md) (candidate
policies for Stage 07 — not a finalized production pipeline).

## Stage 07 — Evidence-Based Feature Engineering, Selection & Ablation Studies

A sixth notebook (`lab12_stage07_feature_engineering_selection.ipynb`) re-verifies Stage
05's frozen protocol fingerprint, engineers 14 candidate shipment-level features (Groups
A–F), and runs Filter/Embedded/limited-Wrapper feature selection plus add-one/drop-one
feature-group ablation — all on Stage 05's frozen 4-fold CV, using the same fixed Ridge/
Random Forest probe estimators from Stage 06.

| Feature Group | Decision |
|---|---|
| A — Shipment Composition (line-item/item/molecule counts) | **Accepted** — consistent small positive contribution for both estimators |
| B — Shipment Value (mean/max/dispersion) | Model-dependent — helps Ridge slightly, redundant/harmful for Random Forest |
| C — Product Diversity | **Rejected** — every shipment has exactly 1 Product Group (zero variance, empirically confirmed) |
| D — Transport/Contract extensions (Managed By, Fulfill Via, First Line Designation) | Inconclusive — small, ambiguous effect |
| E — Calendar (month/quarter) | Conditional/sensitivity-only (D-007); slightly hurts both estimators |
| F — Weight | Sensitivity-only (D-006 unchanged) — despite a striking −542 USD pooled-MAE improvement for Random Forest |

- **Correlated-feature lesson:** the Value group shows *high* permutation importance
  (RF: 1159, Ridge: 1841) yet *removing* it from the combined set actually **improves**
  Random Forest (−95.64 USD) — a textbook case of correlated features sharing importance
  that ablation, not permutation importance alone, correctly resolves.
- **Feature selection:** No Selection (full ~57-column encoded F4 space) outperformed
  Filter (SelectKBest/MI), Embedded (Lasso SelectFromModel), and limited Wrapper (RFE,
  n=8) in this setup — more encoded features consistently helped Random Forest here.
- **136 total CV fits**; validated first as a plain Python script (37.4s) to separate
  pipeline-logic correctness from Jupyter-kernel execution overhead — the slowdown seen
  in Stage 06 was traced this time to matplotlib's interactive `TkAgg` backend blocking
  on `plt.show()` during plain-script runs (fixed with `Agg`); the official clean-kernel
  executions (local and Docker) both completed in ~43s with 0 errors.
- **Recommended feature sets for Stage 08–09:** Candidate A (Minimal Core, 6 features —
  Recommended), Candidate B (Extended Eligible, 15 features — Acceptable), Candidate C
  (Filter-reduced, ~10 encoded features — Conditional), Candidate D (Weight-included,
  sensitivity-only — never compared as production-ready). **No final production feature
  set was chosen** — that remains Stage 08–09's job.

Full detail: [`docs/stage07_feature_engineering_design.md`](docs/stage07_feature_engineering_design.md),
[`docs/stage07_feature_selection_evidence.md`](docs/stage07_feature_selection_evidence.md),
[`docs/stage07_ablation_study.md`](docs/stage07_ablation_study.md), and
[`docs/stage07_feature_contract.md`](docs/stage07_feature_contract.md).

## Stage 08 — Statistical & Business Baseline Development

A seventh notebook (`lab12_stage08_statistical_business_baselines.ipynb`) builds 5
baselines (B0 Global Median, B1 Global Mean, B2 Shipment Mode Median, B3 INCOTERM
Median, B4 Hierarchical Segment Median) on Stage 05's frozen 4-fold CV — the reference
levels Stage 09's ML models must beat.

| Baseline | Pooled MAE (USD) | Note |
|---|---:|---|
| B0 — Global Median | 9,226.37 | Theoretically MAE-optimal on training, but not on this CV |
| B1 — Global Mean | 9,106.34 | **Beat B0** — a temporal-shift-sensitive finding, not a general rule |
| B2 — Shipment Mode Median | 8,791.55 | Best single-segment baseline, 0 fallback |
| B3 — INCOTERM Median | 9,145.64 | Only marginal gain over B0 |
| B4 — Hierarchical (Mode+INCOTERM) | **8,694.56** | Best overall — small but consistent gain over B2 |

- **Statistical Reference Baseline: B1.** **Business Reference Baseline: B4.** No
  business-approved SLA exists — a 5% MAE-improvement threshold is used only as a
  *provisional* engineering reference point for Stage 09.
- **Critical tail-risk finding:** all 5 baselines show a **100% underprediction rate**
  on high-cost (fold-training P90+) shipments — a structural property of constant/
  median-based predictors on a right-skewed target, not a fixable bug.
- Hierarchical fallback (`combined segment → Shipment Mode → INCOTERM → global median`)
  validated with 8 synthetic unit fixtures (known/unknown/low-support/missing/single-
  observation segments) plus real fold diagnostics — 0 NaN/infinite predictions, 0
  crashes; fallback triggered on 4.1% of B4's predictions.
- 28 total baseline fits (20 planned + 8 reproducibility reruns); validated as a plain
  script (3.2s) before clean-kernel execution — both local and Docker completed in
  under 9 seconds with 0 errors.

Full detail: [`docs/stage08_baseline_design.md`](docs/stage08_baseline_design.md),
[`docs/stage08_baseline_evaluation.md`](docs/stage08_baseline_evaluation.md),
[`docs/stage08_baseline_acceptance.md`](docs/stage08_baseline_acceptance.md), and
[`docs/stage09_benchmark_contract.md`](docs/stage09_benchmark_contract.md) (Stage 09
handoff — Stage 06/07 Ridge/RF probe results are contextual reference only, not
directly comparable due to different feature/preprocessing policies).

## Stage 09 — Model Training, Comparative Benchmarking & Model Shortlisting

An eighth notebook (`lab12_stage09_model_training_benchmarking.ipynb`) trains 6 models
across 3 families — Ridge/ElasticNet (Regularized Linear), Random Forest/ExtraTrees
(Bagging), XGBoost/LightGBM (Gradient Boosting) — on Stage 05's frozen 4-fold CV, with
fixed (not tuned) hyperparameters, and benchmarks them against Stage 08's B4/B1
baselines.

| Model | Pooled MAE (USD) | Improvement vs B4 |
|---|---:|---:|
| M05 — XGBoost | **5,808.51** (best) | **33.2%** |
| M04 — ExtraTrees | 5,880.35 | 32.4% |
| M03 — Random Forest | 6,151.90 | 29.2% |
| M06 — LightGBM | 6,236.25 | 28.3% |
| M02 — ElasticNet | 7,993.60 | 8.1% |
| M01 — Ridge | 8,029.16 | 7.7% |

- **All 6 models beat both B4 (8,694.56 USD) and B1 (9,106.34 USD)**, with tree-based/
  boosting models showing a far larger gain than linear models.
- **Tail-risk finding:** all 6 models reduce the high-cost-shipment underprediction rate
  below Stage 08's baseline 100% (range: 83.1%–92.5%) — a real but only *partial*
  improvement, not a fix.
- ElasticNet produced **zero** negative raw predictions vs Ridge's 96 (2.95% of OOF) —
  a concrete, measured safety advantage from the L1 penalty.
- Five mandatory pre-execution gates (dataset integrity, evaluation-protocol integrity,
  feature contract, baseline contract re-verified from real Stage 08 artifacts, and
  XGBoost/LightGBM dependency compatibility) all passed before any training began.
- **Model shortlist for Stage 10: M05 (XGBoost) and M04 (ExtraTrees)** — one candidate
  per family, each independently meeting the improvement/stability/prediction-validity
  bar; Ridge was downgraded to *Inconclusive* (negative-prediction risk), others to
  *Conditional Candidate* (redundant with a stronger same-family peer, or unstable).
- 44 total fits (24 primary + 12 secondary + 8 reproducibility reruns); both local and
  Docker clean-kernel executions completed in under 17 seconds with 0 errors.

Full detail: [`docs/stage09_model_experiment_design.md`](docs/stage09_model_experiment_design.md),
[`docs/stage09_comparative_benchmark_results.md`](docs/stage09_comparative_benchmark_results.md),
[`docs/stage09_generalization_diagnostics.md`](docs/stage09_generalization_diagnostics.md),
[`docs/stage09_model_shortlist.md`](docs/stage09_model_shortlist.md), and
[`docs/stage10_optimization_contract.md`](docs/stage10_optimization_contract.md) (a
contract only — no search was executed).

## Stage 10 — Hyperparameter Optimization, Controlled Search & Model Selection

A ninth notebook (`lab12_stage10_hyperparameter_optimization.ipynb`) runs a bounded,
pre-registered hyperparameter search (16 trials/model, including the Stage 09
reference as trial T000) for the two shortlisted models — M04 (ExtraTrees) and M05
(XGBoost) — on Stage 05's frozen CV, totaling 128 CV fits.

| Model | Reference MAE | Best Trial MAE | Improvement vs Reference | Decision |
|---|---:|---:|---:|---|
| M04 — ExtraTrees | 5,880.35 | **5,686.34** (M04-T003) | **+3.30%** (4/4 folds consistent) | Preferred Tuned Candidate |
| M05 — XGBoost | 5,818.29 | 5,818.29 (= reference) | +0.00% | Retain Stage 09 Reference (Tuning Benefit Inconclusive) |

- **Honest, non-forced outcome:** none of XGBoost's 15 sampled configurations beat its
  Stage 09 reference — the reference itself was retained rather than manufacturing an
  improvement.
- **Root-caused a real cross-session/cross-environment discrepancy** rather than
  dismissing it: a controlled `n_jobs=1/2/4` experiment confirmed XGBoost's `hist`
  tree_method has thread-count-dependent floating-point non-determinism (not a config
  or leakage bug) — ExtraTrees reproduced at 0.000% discrepancy under the same test,
  isolating the cause to XGBoost specifically. Docker and local executions even
  selected a marginally different "best" XGBoost trial (~0.10% apart), which itself
  reinforces rather than contradicts the "Inconclusive" finding.
- **Caught and fixed a subtler bug in the selection logic itself**: comparing a
  separately-recomputed reference value against the main search loop's own T000 trial
  (two independent XGBoost fits of the identical config) could introduce spurious
  non-zero deltas from floating-point noise alone. Fixed by anchoring all improvement
  comparisons to T000's value from the same trial loop.
- Both local and Docker clean-kernel executions completed with 0 errors; the fix was
  re-verified against both environments.
- **Provisional Stage 11 candidates**: Primary = M04 tuned (M04-T003), Alternative =
  M05 reference (M05-T000) — explicitly **not** a final production model choice.

Full detail: [`docs/stage10_optimization_design.md`](docs/stage10_optimization_design.md),
[`docs/stage10_search_space_rationale.md`](docs/stage10_search_space_rationale.md),
[`docs/stage10_optimization_results.md`](docs/stage10_optimization_results.md),
[`docs/stage10_model_selection.md`](docs/stage10_model_selection.md), and
[`docs/stage11_external_validation_contract.md`](docs/stage11_external_validation_contract.md)
(a contract only — 2014 data was never read in this notebook).

## Stage 11 — External Validation, Generalization Diagnostics & Model Acceptance

A tenth notebook (`lab12_stage11_external_validation.ipynb`) scores the two frozen
Stage 10 candidates on the **2014 external validation population** — the first time
this period's targets are used anywhere in the project. Both candidates were fully
refit from scratch on the entire eligible development population (2006–2013,
N=4,987), not reused from Stage 10's fold-level fits, and scored exactly once.

| Model | External MAE (2014) | Improvement vs B4 | Dev-CV MAE | Generalization Gap |
|---|---:|---:|---:|---:|
| **M04-T003 — ExtraTrees (Primary)** | **6,485.63** | **+33.6%** | 5,686.34 | +799.29 (+14.1%) |
| M05-T000 — XGBoost (Alternative) | 6,591.33 | +32.5% | 5,818.29 | +773.04 (+13.3%) |
| B4 — Hierarchical Median | 9,770.79 | — | — | — |
| B1 — Global Mean | 11,111.03 | — | — | — |

- **Development-CV ranking held on genuinely unseen data**: M04-T003 remains the
  best model; both ML candidates beat both baselines by a wide margin.
- **Nuanced, honestly-reported disagreement**: M05-T000 wins on more individual
  shipments (51.3% vs 48.7%) but loses on aggregate MAE — a handful of large
  disagreements (up to ~$21,490 on one shipment) pull its MAE up. Win-rate and MAE
  are reported together, not substituted for each other.
- **Stage 08-10's high-cost underprediction finding independently replicated**:
  baselines still underpredict 100% of high-cost shipments on 2014; both ML models
  reduce this to 89.9% — confirmed on data never used for that original finding.
- **Quantified a real cross-environment reproducibility risk**: local vs Docker
  execution of the identical frozen configuration shows ExtraTrees reproduces to
  ~1e-11 USD (floating-point only), while XGBoost's aggregate MAE differs by only
  ~0.10% but **individual shipment predictions can differ by up to $9,338** —
  documented as a real model risk, not resolved by retuning, with no environment
  cherry-picked.
- **No production-readiness or SLA claim made**: no business-approved monetary
  tolerance exists for this project; Stage 08's 5% criterion remains a provisional
  engineering target only.
- **2015 Protected Test was never opened**: no target parsing, aggregation, or
  analysis was performed on it anywhere in this notebook.
- **Decision: Accepted for Stage 12 (Primary: M04-T003)**, with M05-T000 retained
  as a secondary comparison candidate rather than discarded.

Full detail: [`docs/stage11_validation_design.md`](docs/stage11_validation_design.md),
[`docs/stage11_external_validation_results.md`](docs/stage11_external_validation_results.md),
[`docs/stage11_generalization_diagnostics.md`](docs/stage11_generalization_diagnostics.md),
[`docs/stage11_model_risk_assessment.md`](docs/stage11_model_risk_assessment.md),
[`docs/stage11_model_acceptance.md`](docs/stage11_model_acceptance.md), and
[`docs/stage12_explainability_uncertainty_contract.md`](docs/stage12_explainability_uncertainty_contract.md)
(a contract only — Stage 12 implementation has not begun).

## Stage 12 — Model Explainability, Prediction Uncertainty & Time-Aware Conformal Calibration

An eleventh notebook (`lab12_stage12_explainability_uncertainty.ipynb`) explains the
frozen Stage 11 point predictor (M04-T003, refit-identity-verified to 0.000000 USD
vs Stage 11's own 2014 predictions) and runs a **development-only** conformal
interval research protocol — without changing the accepted model in any way.

**Global/Local Explainability (Approved for Stage 13 Prototype):**
- Permutation Importance (development population) and Grouped SHAP agree strongly
  (Spearman rank correlation = 0.943); top features are `Line_Item_Qty_Sum` and
  `Line_Item_Value_Sum`.
- SHAP additivity verified exactly (max diff ~1.9e-10 USD, both ExtraTrees and the
  secondary XGBoost comparison).
- **Caught and fixed a real sign-flip bug during development**: the first
  implementation negated sklearn's `permutation_importance` output, which already
  returns correctly-signed values — this produced an entirely fabricated
  "all-negative importance" result that was verified against a synthetic
  signal/noise fixture and corrected before being reported.
- Explanation stability across 3 independent background samples: perfectly stable
  (rank range = 0); however, `tree_path_dependent` vs `interventional` SHAP
  perturbation assumptions produce a real, material difference (~$1,231) for
  `Line_Item_Qty_Sum` — documented as a genuine, unresolved attribution-method
  sensitivity, not an error.
- 5 deterministic local case studies (typical, high/low predicted, 2014 high-error,
  2014 model-disagreement) explained via SHAP waterfall.

**Time-Aware Conformal Calibration (Production Interval Not Approved):**
- A `SplitConformalCalibrator` (absolute-residual split conformal, 10 unit tests)
  was run across Stage 05's 4 frozen outer folds using a nested chronological
  design (e.g., outer validation year 2010 ← calibration year 2009 ← inner training
  2006–2008) — never touching 2014 or 2015.
- A calibration-leakage demonstration confirmed the textbook risk empirically: using
  a model's own training residuals for calibration produced a P90 residual 16.9%
  narrower than the honest, held-out version.
- **Systematic undercoverage at both tested levels**: 80% nominal → 73.0% empirical
  (gap −7.0%); 90% nominal → 83.1% empirical (gap −6.9%), consistent across all 4
  folds.
- **High-cost shipments show severe interval undercoverage**: only 43.6% empirical
  coverage at the 90% nominal level (vs. 83.1% overall) — an independent,
  interval-level confirmation of Stage 11's 89.9% point-level underprediction
  finding.
- Decision: **Production Interval Not Approved** — intervals remain Research Only /
  Disabled by Default; this does not change Stage 11's acceptance of the point
  predictor itself.

**Explicit distinction preserved throughout:** the frozen full-development point
predictor (Object A) and the development-only research calibration replicas
(Object B) are never the same fitted estimator, and this notebook never claims
otherwise.

Full detail: [`docs/stage12_explainability_design.md`](docs/stage12_explainability_design.md),
[`docs/stage12_global_local_explanations.md`](docs/stage12_global_local_explanations.md),
[`docs/stage12_explanation_reliability.md`](docs/stage12_explanation_reliability.md),
[`docs/stage12_uncertainty_calibration_design.md`](docs/stage12_uncertainty_calibration_design.md),
[`docs/stage12_interval_evaluation.md`](docs/stage12_interval_evaluation.md),
[`docs/stage12_model_risk_decisions.md`](docs/stage12_model_risk_decisions.md), and
[`docs/stage13_model_inference_contract.md`](docs/stage13_model_inference_contract.md)
(a contract only — Stage 13 implementation has not begun).

## Stage 13 — Model Persistence, Inference Pipeline, Artifact Governance, Security & Reproducibility

A twelfth notebook (`lab12_stage13_model_persistence_inference.ipynb`) packages the
Stage 11-accepted, Stage 12-explained frozen ExtraTrees model (M04-T003) as a
versioned, checksummed, trusted-loading inference component — built on a real,
tested, reusable Python package (`labs/lab12/inference/`), not reimplemented inside
the notebook.

- **Full-development refit identity**: refit from scratch on the full eligible
  population (n=4,987) and verified against Stage 11's own 2014 predictions —
  **0.000000 USD** difference (n=819).
- **Versioned model bundle** (`artifacts/stage13_model_bundle/v1/`): a single fitted
  `Pipeline` (preprocessing + ExtraTrees) plus manifest, feature schema,
  preprocessing schema, model config, environment, and reference predictions — SHA-256
  checksummed, immutable once written.
- **Trusted, security-checked loading**: `joblib.load()` is never called directly —
  `TrustedBundleLoader` verifies the artifact path, manifest, model identity,
  SHA-256, and dependency compatibility first. 6/6 security failure-mode tests
  (corrupted file, wrong model/trial ID, untrusted path, missing manifest,
  dependency mismatch) correctly rejected; 3 additional tamper patterns detected in
  Advanced Challenge 1.
- **Real dependency-compatibility finding, caught and fixed during Docker
  validation**: local runs Python 3.11.15, this project's Docker image runs Python
  3.11.18. The original exact-match check correctly rejected this (fail-closed,
  working as designed) — the policy was then deliberately refined to compare
  `python_version` by major.minor only (patch releases don't affect pickle
  compatibility) while keeping `sklearn_version` an exact-match requirement. After
  the fix, the *same* bundle (identical SHA-256, not refit) loaded in both
  environments with predictions agreeing to 7.28e-12 USD.
- **Self-caught floating-point tolerance bug**: two notebook assertions originally
  used strict `==` to compare ExtraTrees predictions; under `n_jobs=2`,
  thread-order-dependent summation can introduce ~1e-11 USD noise even for a
  deterministic estimator. Both were corrected to the same 1e-6 USD tolerance used
  everywhere else in the notebook.
- **Honest risk-flag finding**: `PREDICTION_OUTSIDE_REFERENCE_RANGE` almost never
  fires for this model in practice — tree ensembles cannot extrapolate beyond
  training-leaf values, so even an absurd input (qty=1,000,000, value=50,000,000)
  produced a prediction well inside the training-observed range. Documented, not
  hidden; the flag's logic was separately verified correct.
- **Single/batch inference parity**: 0.00000000 USD difference across every tested
  batch size; optional, bounded SHAP explanation (10/10 additivity checks passed,
  max diff 5.09e-11 USD); uncertainty permanently `disabled` — `request_interval=True`
  only adds an `INTERVAL_NOT_APPROVED` flag, never fabricated bounds.
- **46 pytest unit/component tests** (`labs/lab12/tests/stage13/`, synthetic
  fixtures) plus the notebook's own 17 real-artifact integration tests — both
  layers passed in full, locally and in Docker.
- **Stage 14 readiness: CONDITIONAL GO** — the point predictor and explainability
  are Approved for Prototype; uncertainty/interval remains Research Only/Disabled by
  Default; no production-readiness or business-SLA claim is made.

Full detail: [`docs/stage13_artifact_design.md`](docs/stage13_artifact_design.md),
[`docs/stage13_serialization_security.md`](docs/stage13_serialization_security.md),
[`docs/stage13_feature_inference_contract.md`](docs/stage13_feature_inference_contract.md),
[`docs/stage13_inference_architecture.md`](docs/stage13_inference_architecture.md),
[`docs/stage13_explainability_risk_policy.md`](docs/stage13_explainability_risk_policy.md),
[`docs/stage13_validation_results.md`](docs/stage13_validation_results.md), and
[`docs/stage14_api_deployment_contract.md`](docs/stage14_api_deployment_contract.md).

## Stage 14 (Phase A Only) — REST API, Docker Reuse & Automated Testing

**Phase A complete; Phase B (2015 Protected Test) NOT started — awaiting
explicit user approval.** A thirteenth notebook
(`lab12_stage14_api_deployment.ipynb`) wraps the Stage 13
`FreightCostPredictor` in a FastAPI service (`labs/lab12/api/`:
`config.py`, `schemas.py`, `errors.py`, `app.py`) without reimplementing
any of its validation, risk-flag, or explainability logic.

- **No new Docker service**: the existing `ml-lab` container is reused
  (`compose.yaml` gained a port mapping for the API; `CMD` is still
  `jupyter lab`). Decision and rationale: D-157.
- **Fail-closed startup/readiness**: the bundle loads exactly once at
  service startup and is verified with a canary prediction; `/predict*`
  returns 503 until that succeeds, `/health` and `/ready` are
  deliberately separate.
- **42 new automated tests** (`labs/lab12/tests/stage14/`, 8 contract-based
  files + 1 real-`uvicorn`-subprocess Docker/live-server file) plus all
  48 Stage 13 regression tests — **90/90 passed, local AND Docker**
  (Python 3.11.15 / 3.11.18), bundle SHA-256 unchanged throughout.
- **Real finding (D-162)**: the same ExtraTrees `n_jobs=2`
  floating-point noise from Stage 13's D-154 reappeared at the API layer
  (~1e-13 USD) and was handled with the same project-wide 1e-6 USD
  tolerance policy — not a regression, a documented re-occurrence.
- **Real finding (D-163)**: API latency is dominated by a fixed
  per-call overhead, essentially flat from batch size 1 to 100;
  `explain=true` adds a measurable per-row cost, numerically justifying
  the existing `max_batch_explanations=10` limit.
- **Security**: no endpoint, query parameter, or environment variable
  can override the bundle path (`api/config.py` is a hardcoded constant);
  verified by dedicated tests.
- **Protected Test**: not opened, read, or referenced anywhere in Phase
  A. A Pre-Test Freeze Manifest (`artifacts/stage14_pretest_freeze_manifest.json`)
  records the frozen state (bundle hash, test results, cross-environment
  parity) as the checkpoint Phase B would build on, without triggering it.
- **Phase B readiness: CONDITIONAL GO** (see
  [`docs/stage14_phase_a_final_report.md`](docs/stage14_phase_a_final_report.md)
  for the full mandated report and explicit stop) — gated on the same
  open risks as Stage 11/12/13 (no business SLA, high-cost
  underprediction, D-006/D-007), plus the absence of
  authentication/rate-limiting (out of scope for this prototype).

Full detail: [`docs/stage14_api_implementation.md`](docs/stage14_api_implementation.md),
[`docs/stage14_security_review.md`](docs/stage14_security_review.md),
[`docs/stage14_test_results.md`](docs/stage14_test_results.md),
[`docs/stage14_performance_benchmark.md`](docs/stage14_performance_benchmark.md),
[`docs/stage14_pretest_freeze_manifest.md`](docs/stage14_pretest_freeze_manifest.md), and
[`docs/stage14_phase_a_final_report.md`](docs/stage14_phase_a_final_report.md).

## Stage 14 (Phase B Preparation Only) — Final Evaluation Infrastructure

**Infrastructure built and tested; the 2015 Protected Test itself was
NOT opened, read, or scored.** A new `labs/lab12/evaluation/` package
(10 modules: `contracts`, `population`, `baselines`, `metrics`,
`acceptance`, `freeze`, `gate`, `runner`, `cli`, `__init__`) implements
the full final-evaluation pipeline, reusing `inference.predictor.FreightCostPredictor`
without modification.

- **Structurally, not just conventionally, gated**: `load_protected_population()`
  requires an `UnlockToken` that only `PreUnlockGate.unlock()` can
  produce, after 9 categories of checks (explicit authorization phrase,
  frozen model identity, live bundle integrity, dataset/Stage 05
  fingerprints, frozen evaluation code+protocol+acceptance-criteria
  fingerprints, canonical runtime, no silent rerun, audit-log
  writability) — verified by `tests/stage14_evaluation/test_structural_safety.py`
  that neither pytest nor the Stage 14 notebook can reach it.
- **55 new tests, all synthetic/development-only** — **145/145 tests
  pass, local AND Docker** (Stage 13's 48 + Phase A's 42 + these 55),
  bundle SHA-256 unchanged throughout.
- **Frozen methodology, recovered from Stage 05/08/11, not reinvented**:
  B1 (Global Mean) and B4 (Hierarchical Median, Shipment_Mode+INCO_Term,
  min_support=10) baselines; MAE/RMSE/WAPE/Bias/Median/P90/P95/high-cost
  metrics; the high-cost threshold itself reused unchanged from Stage 11
  (23,897.32 USD, frozen before 2014 was ever read) rather than
  recomputed from the period being scored.
- **Technical acceptance thresholds are explicitly provisional, not a
  business SLA** — `classify_acceptance()` never returns a
  `business_approved`/`sla` field, by design and by test.
- **Freeze Manifest v2** (`artifacts/stage14_evaluation_freeze_manifest_v2.json`)
  supersedes, but does not overwrite, Phase A's v1 manifest — v1 did not
  and could not cover evaluation-code/protocol/acceptance fingerprints
  that didn't exist yet.
- **Validation limitation (D-169)**: raw dataset access was blocked
  during preparation. Baseline fitting against the real development
  population was deferred to the separately authorized unlock run;
  preparation-stage validation used only synthetic fixtures.
- **The explicit unlock CLI (`evaluation/cli.py`) was implemented but
  never invoked** — `PreUnlockGate.unlock()` was never called with the
  real authorization phrase against the real dataset in this task.
- **Phase B readiness (at preparation time): CONDITIONAL GO** (infrastructure-level; see
  [`docs/stage14_phase_b_readiness_assessment.md`](docs/stage14_phase_b_readiness_assessment.md)).

Full detail: [`docs/stage14_final_evaluation_protocol.md`](docs/stage14_final_evaluation_protocol.md),
[`docs/stage14_metric_baseline_contract.md`](docs/stage14_metric_baseline_contract.md),
[`docs/stage14_protected_test_authorization_procedure.md`](docs/stage14_protected_test_authorization_procedure.md),
[`docs/stage14_evaluation_validation_results.md`](docs/stage14_evaluation_validation_results.md),
[`docs/stage14_final_pretest_freeze.md`](docs/stage14_final_pretest_freeze.md),
[`docs/stage14_phase_b_readiness_assessment.md`](docs/stage14_phase_b_readiness_assessment.md), and
[`docs/stage14_pre_unlock_audit_report.md`](docs/stage14_pre_unlock_audit_report.md) (D-173/D-174/D-175 audit findings).

## Stage 14 — Final Evaluation (2015 Protected Test, COMPLETE, One-Time)

**With the user's explicit, separate authorization, the 2015 Protected
Test was evaluated exactly once** (`python -m evaluation.cli unlock`).
All pre-unlock gates passed, including the development-population B1
integrity check (D-174) against the frozen Stage 11 reference
(`10456.218411870865` USD) — matched exactly, *before* any 2015 row was
read.

- **n_protected_eligible = 392** (of 569 Protected_Test shipments).
- **M04-T003: MAE = 8540.83 USD**, beating B4 (12233.66 USD) by
  **30.2%** (threshold: ≥10%) — **ACCEPTED**.
- Validity rate 100%, 0 negative predictions, high-cost underprediction
  80.49% (vs. both baselines' 100% on the same period — the D-173
  relative criterion).
- **Real, unfavorable finding, reported as observed**: the Dev-CV→2014
  generalization gap (+14.1%) accelerated to 2014→2015 (+31.7%) — but
  B1 and B4 degraded by similar relative margins over the same
  transition, suggesting a shared distribution shift rather than a
  model-specific failure (not independently confirmed in this report).
- Model bundle SHA-256 unchanged before/after; no retraining, no
  retuning, no threshold changes after seeing results, no rerun
  (`AlreadyEvaluatedError` guard now active).
- **This result is a technical PoC acceptance, not a business-approved
  SLA or production-deployment approval.**

Full report: [`docs/stage14_final_evaluation_report.md`](docs/stage14_final_evaluation_report.md)
(16-section final report: integrity, gates, audit trail, full metrics,
Model Card, remaining limitations).

## Next Steps

LAB12's planned 14-stage scope is now complete. Remaining open items,
unresolved by this evaluation and not expected to be: D-006 (Weight),
D-007 (label timestamp), D-010 (Quantity/Value aggregation), the lack
of a business-approved improvement SLA, the lack of
authentication/rate-limiting on the API, and the unconfirmed
distribution-shift hypothesis for the 2014→2015 gap acceleration. The
uncertainty/interval output remains Research Only / Disabled by
Default.
