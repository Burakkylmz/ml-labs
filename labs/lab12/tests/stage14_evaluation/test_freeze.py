from pathlib import Path

from evaluation import freeze

EVALUATION_PACKAGE_DIR = Path(__file__).resolve().parents[2] / "evaluation"
PROTOCOL_DOC = Path(__file__).resolve().parents[2] / "docs" / "stage14_final_evaluation_protocol.md"
ACCEPTANCE_DOC = Path(__file__).resolve().parents[2] / "docs" / "stage14_metric_baseline_contract.md"


def test_evaluation_code_fingerprint_is_deterministic():
    fp1 = freeze.compute_evaluation_code_fingerprint(EVALUATION_PACKAGE_DIR)
    fp2 = freeze.compute_evaluation_code_fingerprint(EVALUATION_PACKAGE_DIR)
    assert fp1 == fp2
    assert len(fp1) == 64  # sha256 hex digest


def test_evaluation_code_fingerprint_changes_when_a_file_changes(tmp_path):
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    for filename in freeze.EVALUATION_PACKAGE_FILES:
        (pkg / filename).write_text(f"# {filename}\n", encoding="utf-8")

    original = freeze.compute_evaluation_code_fingerprint(pkg)
    (pkg / "contracts.py").write_text("# contracts.py\nX = 1\n", encoding="utf-8")
    changed = freeze.compute_evaluation_code_fingerprint(pkg)
    assert original != changed


def test_doc_fingerprint_matches_real_protocol_docs():
    fp = freeze.compute_doc_fingerprint([PROTOCOL_DOC])
    assert len(fp) == 64


def test_canonical_runtime_reports_major_minor_and_exact_sklearn():
    runtime = freeze.canonical_runtime()
    assert "python_major_minor" in runtime
    assert "sklearn_version" in runtime
    assert runtime["python_version"].startswith(runtime["python_major_minor"])


def test_verify_freeze_manifest_detects_code_fingerprint_mismatch(tmp_path):
    manifest = {
        "evaluation_code_fingerprint": "0" * 64,  # deliberately wrong
        "evaluation_protocol_fingerprint": freeze.compute_doc_fingerprint([PROTOCOL_DOC]),
        "acceptance_criteria_fingerprint": freeze.compute_doc_fingerprint([ACCEPTANCE_DOC]),
        "canonical_runtime": freeze.canonical_runtime(),
    }
    mismatches = freeze.verify_freeze_manifest(manifest, EVALUATION_PACKAGE_DIR, [PROTOCOL_DOC], [ACCEPTANCE_DOC])
    assert any("evaluation_code_fingerprint" in m for m in mismatches)


def test_verify_freeze_manifest_passes_when_everything_matches():
    manifest = {
        "evaluation_code_fingerprint": freeze.compute_evaluation_code_fingerprint(EVALUATION_PACKAGE_DIR),
        "evaluation_protocol_fingerprint": freeze.compute_doc_fingerprint([PROTOCOL_DOC]),
        "acceptance_criteria_fingerprint": freeze.compute_doc_fingerprint([ACCEPTANCE_DOC]),
        "canonical_runtime": freeze.canonical_runtime(),
    }
    mismatches = freeze.verify_freeze_manifest(manifest, EVALUATION_PACKAGE_DIR, [PROTOCOL_DOC], [ACCEPTANCE_DOC])
    assert mismatches == []
