import json
from pathlib import Path

import pytest

from evaluation import freeze
from evaluation.contracts import (
    AlreadyEvaluatedError,
    EXPECTED_DATASET_SHA256,
    EXPECTED_MODEL_ARTIFACT_SHA256,
    EXPECTED_MODEL_ID,
    EXPECTED_STAGE05_PROTOCOL_FINGERPRINT,
    EXPECTED_TRIAL_ID,
    GateError,
)
from evaluation.gate import REQUIRED_AUTHORIZATION_PHRASE, PreUnlockGate, UnlockToken

LAB12_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_PACKAGE_DIR = LAB12_ROOT / "evaluation"
PROTOCOL_DOC = LAB12_ROOT / "docs" / "stage14_final_evaluation_protocol.md"
ACCEPTANCE_DOC = LAB12_ROOT / "docs" / "stage14_metric_baseline_contract.md"
REAL_MODEL_BUNDLE_MANIFEST = LAB12_ROOT / "artifacts" / "stage13_model_bundle" / "v1" / "manifest.json"


def _valid_manifest() -> dict:
    return {
        "model_bundle": {"model_id": EXPECTED_MODEL_ID, "trial_id": EXPECTED_TRIAL_ID, "model_artifact_sha256": EXPECTED_MODEL_ARTIFACT_SHA256},
        "evaluation_code_fingerprint": freeze.compute_evaluation_code_fingerprint(EVALUATION_PACKAGE_DIR),
        "evaluation_protocol_fingerprint": freeze.compute_doc_fingerprint([PROTOCOL_DOC]),
        "acceptance_criteria_fingerprint": freeze.compute_doc_fingerprint([ACCEPTANCE_DOC]),
        "dataset_sha256": EXPECTED_DATASET_SHA256,
        "stage05_protocol_fingerprint": EXPECTED_STAGE05_PROTOCOL_FINGERPRINT,
        "canonical_runtime": freeze.canonical_runtime(),
    }


def _build_gate(tmp_path, manifest: dict | None = None, completed_report_exists: bool = False) -> PreUnlockGate:
    manifest_path = tmp_path / "freeze_manifest_v2.json"
    manifest_path.write_text(json.dumps(manifest if manifest is not None else _valid_manifest()), encoding="utf-8")
    completed_report_path = tmp_path / "report.json"
    if completed_report_exists:
        completed_report_path.write_text("{}", encoding="utf-8")
    return PreUnlockGate(
        evaluation_package_dir=EVALUATION_PACKAGE_DIR,
        freeze_manifest_v2_path=manifest_path,
        protocol_doc_paths=[PROTOCOL_DOC],
        acceptance_doc_paths=[ACCEPTANCE_DOC],
        model_bundle_manifest_path=REAL_MODEL_BUNDLE_MANIFEST,
        audit_log_path=tmp_path / "audit_log.json",
        completed_report_path=completed_report_path,
    )


def test_happy_path_unlock_succeeds_with_everything_correct(tmp_path):
    gate = _build_gate(tmp_path)
    token = gate.unlock(authorization_phrase=REQUIRED_AUTHORIZATION_PHRASE)
    assert isinstance(token, UnlockToken)
    assert token.is_valid()
    audit = json.loads((tmp_path / "audit_log.json").read_text(encoding="utf-8"))
    assert audit[-1]["event"] == "unlock_token_issued"


def test_missing_explicit_authorization_rejected(tmp_path):
    gate = _build_gate(tmp_path)
    with pytest.raises(GateError):
        gate.unlock(authorization_phrase="close enough but not exact")


def test_missing_freeze_manifest_rejected(tmp_path):
    gate = _build_gate(tmp_path)
    gate.freeze_manifest_v2_path.unlink()
    with pytest.raises(GateError):
        gate.unlock(authorization_phrase=REQUIRED_AUTHORIZATION_PHRASE)


def test_wrong_model_artifact_hash_rejected(tmp_path):
    manifest = _valid_manifest()
    manifest["model_bundle"]["model_artifact_sha256"] = "0" * 64
    gate = _build_gate(tmp_path, manifest=manifest)
    with pytest.raises(GateError):
        gate.unlock(authorization_phrase=REQUIRED_AUTHORIZATION_PHRASE)


def test_wrong_dataset_fingerprint_rejected(tmp_path):
    manifest = _valid_manifest()
    manifest["dataset_sha256"] = "deadbeef" * 8
    gate = _build_gate(tmp_path, manifest=manifest)
    with pytest.raises(GateError):
        gate.unlock(authorization_phrase=REQUIRED_AUTHORIZATION_PHRASE)


def test_wrong_stage05_fingerprint_rejected(tmp_path):
    manifest = _valid_manifest()
    manifest["stage05_protocol_fingerprint"] = "deadbeef" * 8
    gate = _build_gate(tmp_path, manifest=manifest)
    with pytest.raises(GateError):
        gate.unlock(authorization_phrase=REQUIRED_AUTHORIZATION_PHRASE)


def test_evaluation_code_fingerprint_mismatch_rejected(tmp_path):
    manifest = _valid_manifest()
    manifest["evaluation_code_fingerprint"] = "0" * 64
    gate = _build_gate(tmp_path, manifest=manifest)
    with pytest.raises(GateError):
        gate.unlock(authorization_phrase=REQUIRED_AUTHORIZATION_PHRASE)


def test_existing_completed_evaluation_prevents_silent_rerun(tmp_path):
    gate = _build_gate(tmp_path, completed_report_exists=True)
    with pytest.raises(AlreadyEvaluatedError):
        gate.unlock(authorization_phrase=REQUIRED_AUTHORIZATION_PHRASE)


def test_existing_completed_evaluation_allows_explicit_rerun_override(tmp_path):
    gate = _build_gate(tmp_path, completed_report_exists=True)
    token = gate.unlock(authorization_phrase=REQUIRED_AUTHORIZATION_PHRASE, allow_rerun=True)
    assert token.is_valid()


def test_canonical_runtime_mismatch_rejected(tmp_path):
    manifest = _valid_manifest()
    manifest["canonical_runtime"]["python_major_minor"] = "2.7"
    gate = _build_gate(tmp_path, manifest=manifest)
    with pytest.raises(GateError):
        gate.unlock(authorization_phrase=REQUIRED_AUTHORIZATION_PHRASE)


def test_unlock_token_is_single_use():
    token = UnlockToken(_nonce="test")
    assert token.is_valid()
    token.consume()
    assert not token.is_valid()
