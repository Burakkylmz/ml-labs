"""Tests 17/18 from the Phase B preparation task: normal pytest execution
and normal Notebook execution must have NO path to the Protected Test.

These are static source scans, not behavioral tests -- they verify that
the *dangerous call* (`PreUnlockGate.unlock(...)` with the real
authorization phrase against the real dataset, or any direct
`load_protected_population(...)` with a real token) does not appear
anywhere outside this evaluation package's own definition, and that the
Stage 14 notebook never references the Phase B unlock machinery at all.
"""

from __future__ import annotations

from pathlib import Path

LAB12_ROOT = Path(__file__).resolve().parents[2]
TESTS_ROOT = LAB12_ROOT / "tests"
NOTEBOOK_PATH = LAB12_ROOT / "lab12_stage14_api_deployment.ipynb"
EVALUATION_CLI_MAIN_CALL_MARKER = "cli.main("

DANGEROUS_MARKERS = ("UnlockToken", "unlock_token", "PreUnlockGate", "load_protected_population", "FinalEvaluationRunner", "evaluation.cli", "REQUIRED_AUTHORIZATION_PHRASE")


def _all_test_py_files() -> list[Path]:
    this_dir = Path(__file__).resolve().parent
    return [p for p in TESTS_ROOT.rglob("*.py") if p.resolve().parent != this_dir]


def test_no_test_outside_this_package_references_protected_test_machinery():
    """Stage 13 and Stage 14 (Phase A) test suites must be completely
    unaware that Phase B machinery exists -- they were written before it
    did, and must still pass unmodified (regression safety)."""
    offending: list[str] = []
    for path in _all_test_py_files():
        text = path.read_text(encoding="utf-8")
        for marker in DANGEROUS_MARKERS:
            if marker in text:
                offending.append(f"{path}: contains '{marker}'")
    assert offending == [], f"Phase A/Stage 13 tests must not reference Phase B machinery: {offending}"


def test_this_packages_own_tests_never_call_unlock_against_the_real_dataset():
    """Within this test package itself, `unlock()` may only ever be called
    with synthetic, tmp_path-scoped fixtures (test_gate.py) -- never with
    the real DATASET_PATH/SPLIT_MANIFEST_PATH from `cli.py`."""
    this_dir = Path(__file__).resolve().parent
    for path in this_dir.glob("*.py"):
        if path.name == "test_structural_safety.py":
            continue
        text = path.read_text(encoding="utf-8")
        assert "cli.DATASET_PATH" not in text
        assert "cli.main(" not in text
        assert "runner.run(" not in text or "tmp_path" in text


def test_notebook_never_references_phase_b_unlock_machinery():
    """The Stage 14 (Phase A) notebook, which this preparation task does
    NOT modify, must contain zero references to any Phase B construct."""
    notebook_text = NOTEBOOK_PATH.read_text(encoding="utf-8")
    offending = [marker for marker in DANGEROUS_MARKERS if marker in notebook_text]
    assert offending == [], f"Stage 14 notebook must not reference Phase B machinery: {offending}"


def test_evaluation_package_has_no_import_from_api_or_notebook_entrypoints():
    """The evaluation package must not be imported by api/app.py (FastAPI
    startup) -- Phase B must stay reachable only through its own explicit
    CLI, never through normal API or notebook execution."""
    api_app_text = (LAB12_ROOT / "api" / "app.py").read_text(encoding="utf-8")
    assert "import evaluation" not in api_app_text
    assert "from evaluation" not in api_app_text
    assert "from .evaluation" not in api_app_text
