"""Trusted, verified loading of a Stage 13 model bundle.

Security policy (see stage13_serialization_security.md):
1. The bundle path must resolve inside an explicitly allowed root directory
   (no arbitrary user-supplied path, no path traversal).
2. The manifest must be present and must declare the expected model identity.
3. The model artifact's SHA-256 must match the manifest's recorded hash.
4. The manifest's recorded dependency versions must be compatible with the
   current runtime before the pickle/joblib payload is ever deserialized.

Only after all four checks pass is `joblib.load()` invoked. This does not
protect against an attacker who can modify both the model file and the
manifest together (integrity != authenticity -- see the design doc) but it
does reject corruption, accidental tampering, and version mismatches.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import sklearn

from .artifact_store import MANIFEST_FILENAME, MODEL_FILENAME, REQUIRED_BUNDLE_FILES, compute_sha256
from .contracts import ArtifactIntegrityError, ModelCompatibilityError


def _runtime_versions() -> dict[str, str]:
    return {
        "python_version": sys.version.split()[0],
        "sklearn_version": sklearn.__version__,
        "numpy_version": np.__version__,
        "joblib_version": joblib.__version__,
    }


class TrustedBundleLoader:
    """Loads a versioned model bundle only after integrity and identity verification."""

    def __init__(self, allowed_root: Path, expected_model_id: str, expected_trial_id: str):
        self.allowed_root = allowed_root.resolve()
        self.expected_model_id = expected_model_id
        self.expected_trial_id = expected_trial_id

    def _resolve_safe_path(self, bundle_dir: Path) -> Path:
        resolved = bundle_dir.resolve()
        try:
            resolved.relative_to(self.allowed_root)
        except ValueError as exc:
            raise ArtifactIntegrityError(f"Untrusted artifact path: {bundle_dir} is outside the allowed root {self.allowed_root}") from exc
        return resolved

    def load(self, bundle_dir: Path) -> tuple[Any, dict[str, Any]]:
        bundle_dir = self._resolve_safe_path(bundle_dir)

        for filename in REQUIRED_BUNDLE_FILES:
            if not (bundle_dir / filename).exists():
                raise ArtifactIntegrityError(f"Bundle is missing required file: {filename}")

        manifest_path = bundle_dir / MANIFEST_FILENAME
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        if manifest.get("model_id") != self.expected_model_id or manifest.get("trial_id") != self.expected_trial_id:
            raise ArtifactIntegrityError(
                f"Model identity mismatch: manifest declares model_id={manifest.get('model_id')!r}, "
                f"trial_id={manifest.get('trial_id')!r}, expected {self.expected_model_id!r}/{self.expected_trial_id!r}"
            )

        model_path = bundle_dir / MODEL_FILENAME
        actual_sha256 = compute_sha256(model_path)
        expected_sha256 = manifest.get("model_artifact_sha256")
        if actual_sha256 != expected_sha256:
            raise ArtifactIntegrityError(f"SHA-256 mismatch for {model_path}: expected {expected_sha256}, got {actual_sha256}")

        recorded_env = manifest.get("environment", {})
        current_env = _runtime_versions()

        # Python patch releases within the same major.minor series do not change the pickle
        # protocol or object layout relevant to joblib-serialized sklearn pipelines, so only
        # major.minor is compared here. sklearn's version IS compared exactly, since its
        # estimator internals/pickle format can change between minor releases.
        recorded_py = recorded_env.get("python_version")
        if recorded_py and ".".join(recorded_py.split(".")[:2]) != ".".join(current_env["python_version"].split(".")[:2]):
            raise ModelCompatibilityError(
                f"Dependency compatibility failure: bundle was created with python_version={recorded_py}, "
                f"current runtime has python_version={current_env['python_version']} (major.minor mismatch)"
            )
        if recorded_env.get("sklearn_version") and recorded_env["sklearn_version"] != current_env["sklearn_version"]:
            raise ModelCompatibilityError(
                f"Dependency compatibility failure: bundle was created with sklearn_version={recorded_env['sklearn_version']}, "
                f"current runtime has sklearn_version={current_env['sklearn_version']}"
            )

        fitted_pipeline = joblib.load(model_path)
        return fitted_pipeline, manifest
