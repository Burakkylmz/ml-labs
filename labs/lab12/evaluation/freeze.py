"""Evaluation-code fingerprinting and the Phase B freeze manifest (v2).

The Phase A freeze manifest (`stage14_pretest_freeze_manifest.json`) froze
the API/model state *before any evaluation code existed*. It does not, and
cannot, cover the evaluation code, protocol, baselines, metrics, or
acceptance criteria built in this task. This module builds a v2 manifest
that supersedes it for Phase B purposes while leaving the v1 file
untouched on disk (see `write_freeze_manifest_v2`).
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import sklearn

EVALUATION_PACKAGE_FILES = (
    "__init__.py", "contracts.py", "population.py", "baselines.py",
    "metrics.py", "acceptance.py", "freeze.py", "gate.py", "runner.py", "cli.py",
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_evaluation_code_fingerprint(package_dir: Path) -> str:
    """SHA-256 over every evaluation module's relative path + contents,
    concatenated in a fixed (sorted) order -- changing any file, adding
    one, or removing one changes this fingerprint."""
    digest = hashlib.sha256()
    for filename in sorted(EVALUATION_PACKAGE_FILES):
        file_path = package_dir / filename
        digest.update(filename.encode("utf-8"))
        digest.update(file_path.read_bytes())
    return digest.hexdigest()


def compute_doc_fingerprint(doc_paths: list[Path]) -> str:
    """SHA-256 over one or more protocol/acceptance documents, in the
    given order -- used for the evaluation-protocol and acceptance-criteria
    fingerprints."""
    digest = hashlib.sha256()
    for doc_path in doc_paths:
        digest.update(doc_path.read_bytes())
    return digest.hexdigest()


def canonical_runtime() -> dict[str, str]:
    """Mirrors inference/model_loader.py's own compatibility policy
    (major.minor Python, exact sklearn) -- not imported from there to avoid
    coupling a private helper, but intentionally the same two checks."""
    return {
        "python_version": sys.version.split()[0],
        "python_major_minor": ".".join(sys.version.split()[0].split(".")[:2]),
        "sklearn_version": sklearn.__version__,
        "numpy_version": np.__version__,
        "joblib_version": joblib.__version__,
        "platform": platform.platform(),
    }


def build_freeze_manifest(
    *,
    manifest_version: str,
    supersedes: str,
    superseding_reason: str,
    evaluation_package_dir: Path,
    protocol_doc_paths: list[Path],
    acceptance_doc_paths: list[Path],
    model_manifest: dict[str, Any],
    model_artifact_sha256: str,
) -> dict[str, Any]:
    return {
        "manifest_version": manifest_version,
        "supersedes": supersedes,
        "superseding_reason": superseding_reason,
        "model_bundle": {
            "model_id": model_manifest["model_id"],
            "trial_id": model_manifest["trial_id"],
            "artifact_version": model_manifest["artifact_version"],
            "model_artifact_sha256": model_artifact_sha256,
            "feature_schema_version": model_manifest["feature_schema_version"],
            "preprocessing_contract_version": model_manifest["preprocessing_contract_version"],
            "feature_schema_fingerprint": _sha256_bytes(json.dumps(model_manifest["feature_schema_inline"], sort_keys=True).encode("utf-8")),
        },
        "evaluation_code_fingerprint": compute_evaluation_code_fingerprint(evaluation_package_dir),
        "evaluation_protocol_fingerprint": compute_doc_fingerprint(protocol_doc_paths),
        "acceptance_criteria_fingerprint": compute_doc_fingerprint(acceptance_doc_paths),
        "dataset_sha256": model_manifest["dataset_sha256"],
        "stage05_protocol_fingerprint": model_manifest["stage05_protocol_fingerprint"],
        "canonical_runtime": canonical_runtime(),
        "protected_test_policy": {
            "accessed_during_preparation": False,
            "statement": "No row of the 2015 Protected Test was read, parsed, filtered, aggregated, or scored while building this manifest or the evaluation code it fingerprints.",
        },
    }


def write_freeze_manifest_v2(path: Path, manifest: dict[str, Any]) -> None:
    """Writes the v2 manifest to its OWN path. Never touches the Phase A
    (v1) manifest file -- that file is preserved for audit purposes
    (master prompt Section 7: 'do not silently overwrite earlier evidence')."""
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def verify_freeze_manifest(manifest: dict[str, Any], evaluation_package_dir: Path, protocol_doc_paths: list[Path], acceptance_doc_paths: list[Path]) -> list[str]:
    """Returns a list of mismatch descriptions (empty = fully verified)."""
    mismatches: list[str] = []
    current_code_fp = compute_evaluation_code_fingerprint(evaluation_package_dir)
    if current_code_fp != manifest["evaluation_code_fingerprint"]:
        mismatches.append(f"evaluation_code_fingerprint mismatch: manifest={manifest['evaluation_code_fingerprint']}, current={current_code_fp}")

    current_protocol_fp = compute_doc_fingerprint(protocol_doc_paths)
    if current_protocol_fp != manifest["evaluation_protocol_fingerprint"]:
        mismatches.append(f"evaluation_protocol_fingerprint mismatch: manifest={manifest['evaluation_protocol_fingerprint']}, current={current_protocol_fp}")

    current_acceptance_fp = compute_doc_fingerprint(acceptance_doc_paths)
    if current_acceptance_fp != manifest["acceptance_criteria_fingerprint"]:
        mismatches.append(f"acceptance_criteria_fingerprint mismatch: manifest={manifest['acceptance_criteria_fingerprint']}, current={current_acceptance_fp}")

    current_runtime = canonical_runtime()
    frozen_runtime = manifest["canonical_runtime"]
    if current_runtime["python_major_minor"] != frozen_runtime["python_major_minor"]:
        mismatches.append(f"python_major_minor mismatch: manifest={frozen_runtime['python_major_minor']}, current={current_runtime['python_major_minor']}")
    if current_runtime["sklearn_version"] != frozen_runtime["sklearn_version"]:
        mismatches.append(f"sklearn_version mismatch: manifest={frozen_runtime['sklearn_version']}, current={current_runtime['sklearn_version']}")

    return mismatches
