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

## Next Steps

Stage 06 (Evidence-Based Data Preprocessing) may begin now that the split/CV protocol is
frozen and versioned — this lab deliberately stops here and does not begin Stage 06.
