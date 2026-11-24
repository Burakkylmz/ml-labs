"""End-to-end FinalEvaluationRunner test, entirely on SYNTHETIC data: a
fake dataset CSV, a fake split manifest (with a fake 'Protected_Test'
split that is NOT 2015 data -- just a test fixture row labeled that way),
and a freshly-fit synthetic model bundle. This proves the orchestration
(population loading, baseline fitting, prediction, metrics, acceptance,
report writing) end-to-end without the gate and without ever touching the
real dataset or the real frozen model.

`UnlockToken` is constructed directly here (bypassing `PreUnlockGate`) --
legitimate for white-box testing of `runner.py` in isolation; see
`test_structural_safety.py` for the separate guarantee that this pattern
never reaches the real dataset path in non-test code.
"""

from __future__ import annotations

import json

import pytest

from evaluation.contracts import DevelopmentPopulationIntegrityError
from evaluation.gate import UnlockToken
from evaluation.runner import FinalEvaluationRunner


def test_runner_end_to_end_on_synthetic_data_produces_a_complete_report(tmp_path, synthetic_dataset_csv, synthetic_split_manifest, synthetic_model_bundle):
    bundle_dir, allowed_root = synthetic_model_bundle
    report_path = tmp_path / "synthetic_final_report.json"

    runner = FinalEvaluationRunner(
        dataset_path=synthetic_dataset_csv, split_manifest_path=synthetic_split_manifest,
        model_bundle_dir=bundle_dir, allowed_root=allowed_root, report_path=report_path,
    )
    token = UnlockToken(_nonce="synthetic-test-token")
    report = runner.run(token)

    assert report_path.exists()
    assert json.loads(report_path.read_text(encoding="utf-8")) == report
    assert report["n_protected_eligible"] == 1  # only SHIP-G is Protected_Test in the fixture
    assert "MAE" in report["model"]["metrics"]
    assert "MAE" in report["b1_global_mean"]["metrics"]
    assert "MAE" in report["b4_hierarchical_median"]["metrics"]
    assert report["acceptance"]["classification"] in {"ACCEPTED", "CONDITIONAL", "FAILED"}
    assert not token.is_valid()  # consumed after use


def test_runner_rejects_a_consumed_token(tmp_path, synthetic_dataset_csv, synthetic_split_manifest, synthetic_model_bundle):
    bundle_dir, allowed_root = synthetic_model_bundle
    runner = FinalEvaluationRunner(
        dataset_path=synthetic_dataset_csv, split_manifest_path=synthetic_split_manifest,
        model_bundle_dir=bundle_dir, allowed_root=allowed_root, report_path=tmp_path / "report.json",
    )
    token = UnlockToken(_nonce="already-used")
    token.consume()
    try:
        runner.run(token)
        assert False, "expected PermissionError for a consumed token"
    except PermissionError:
        pass


def test_runner_integrity_check_passes_when_expected_mean_matches(tmp_path, synthetic_dataset_csv, synthetic_split_manifest, synthetic_model_bundle):
    """D-174: the dev-population integrity check is generic -- it is exercised
    here against the SYNTHETIC fixture's own true mean (11540.1 USD: SHIP-A/B/E/F/H),
    not the real Stage 11 constant, proving the check logic itself (not the
    real-world number) works before it ever gates the real run."""
    bundle_dir, allowed_root = synthetic_model_bundle
    runner = FinalEvaluationRunner(
        dataset_path=synthetic_dataset_csv, split_manifest_path=synthetic_split_manifest,
        model_bundle_dir=bundle_dir, allowed_root=allowed_root, report_path=tmp_path / "report.json",
        expected_development_b1_mean_usd=11540.1,
    )
    token = UnlockToken(_nonce="integrity-pass")
    report = runner.run(token)
    assert report["b1_global_mean"]["metrics"]["MAE"] is not None  # ran to completion


def test_runner_integrity_check_rejects_wrong_expected_mean(tmp_path, synthetic_dataset_csv, synthetic_split_manifest, synthetic_model_bundle):
    """A mismatched expected mean must abort BEFORE the protected population
    is ever loaded -- fail-closed, pre-2015-read."""
    bundle_dir, allowed_root = synthetic_model_bundle
    runner = FinalEvaluationRunner(
        dataset_path=synthetic_dataset_csv, split_manifest_path=synthetic_split_manifest,
        model_bundle_dir=bundle_dir, allowed_root=allowed_root, report_path=tmp_path / "report.json",
        expected_development_b1_mean_usd=999999.0,
    )
    token = UnlockToken(_nonce="integrity-fail")
    with pytest.raises(DevelopmentPopulationIntegrityError):
        runner.run(token)
    assert token.is_valid()  # never consumed -- protected population was never reached
    assert not (tmp_path / "report.json").exists()


def test_runner_rejects_a_plain_non_token_object(tmp_path, synthetic_dataset_csv, synthetic_split_manifest, synthetic_model_bundle):
    bundle_dir, allowed_root = synthetic_model_bundle
    runner = FinalEvaluationRunner(
        dataset_path=synthetic_dataset_csv, split_manifest_path=synthetic_split_manifest,
        model_bundle_dir=bundle_dir, allowed_root=allowed_root, report_path=tmp_path / "report.json",
    )
    try:
        runner.run("not-a-token")
        assert False, "expected PermissionError for a non-UnlockToken object"
    except PermissionError:
        pass
