"""PreUnlockGate -- every check that must pass before a single row of the
2015 Protected Test is read. Fail-closed: any failed check raises
`GateError` (or `AlreadyEvaluatedError`) and no `UnlockToken` is produced.

This module is imported by tests and by `cli.py`. **Nothing in this
preparation task calls `PreUnlockGate.unlock()` with a real authorization
phrase against the real dataset** -- tests exercise it with synthetic
fixtures and temporary paths only (see `tests/stage14_evaluation/test_gate.py`).
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .contracts import (
    AlreadyEvaluatedError,
    EXPECTED_DATASET_SHA256,
    EXPECTED_MODEL_ARTIFACT_SHA256,
    EXPECTED_MODEL_ID,
    EXPECTED_STAGE05_PROTOCOL_FINGERPRINT,
    EXPECTED_TRIAL_ID,
    GateError,
)
from .freeze import canonical_runtime, verify_freeze_manifest

REQUIRED_AUTHORIZATION_PHRASE = "I AUTHORIZE 2015 PROTECTED TEST EVALUATION"


@dataclass
class UnlockToken:
    """Produced only by `PreUnlockGate.unlock()`. `population.load_protected_population`
    refuses to run without a valid, unconsumed instance of this class."""

    _nonce: str
    _consumed: bool = field(default=False)

    def is_valid(self) -> bool:
        return not self._consumed

    def consume(self) -> None:
        self._consumed = True


class PreUnlockGate:
    def __init__(
        self,
        *,
        evaluation_package_dir: Path,
        freeze_manifest_v2_path: Path,
        protocol_doc_paths: list[Path],
        acceptance_doc_paths: list[Path],
        model_bundle_manifest_path: Path,
        audit_log_path: Path,
        completed_report_path: Path,
    ):
        self.evaluation_package_dir = evaluation_package_dir
        self.freeze_manifest_v2_path = freeze_manifest_v2_path
        self.protocol_doc_paths = protocol_doc_paths
        self.acceptance_doc_paths = acceptance_doc_paths
        self.model_bundle_manifest_path = model_bundle_manifest_path
        self.audit_log_path = audit_log_path
        self.completed_report_path = completed_report_path

    def _append_audit(self, event: dict[str, Any]) -> None:
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        existing: list[dict[str, Any]] = []
        if self.audit_log_path.exists():
            existing = json.loads(self.audit_log_path.read_text(encoding="utf-8"))
        existing.append({**event, "timestamp_unix": time.time()})
        self.audit_log_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    def run_checks(self, *, authorization_phrase: str, allow_rerun: bool = False) -> list[str]:
        """Returns the list of passed check descriptions, or raises GateError /
        AlreadyEvaluatedError on the first category of failure (all checks in a
        category are still evaluated and reported together)."""
        passed: list[str] = []
        errors: list[str] = []

        if authorization_phrase != REQUIRED_AUTHORIZATION_PHRASE:
            errors.append("explicit authorization phrase does not match the required exact text")
        else:
            passed.append("explicit_authorization")

        if self.completed_report_path.exists() and not allow_rerun:
            raise AlreadyEvaluatedError(
                f"A completed evaluation report already exists at {self.completed_report_path} -- "
                "pass allow_rerun=True (and a fresh, separate confirmation) to intentionally re-run."
            )
        passed.append("no_silent_rerun")

        if not self.freeze_manifest_v2_path.exists():
            errors.append(f"freeze manifest v2 not found at {self.freeze_manifest_v2_path}")
        else:
            manifest = json.loads(self.freeze_manifest_v2_path.read_text(encoding="utf-8"))

            if manifest["model_bundle"]["model_id"] != EXPECTED_MODEL_ID or manifest["model_bundle"]["trial_id"] != EXPECTED_TRIAL_ID:
                errors.append("frozen model identity in manifest does not match EXPECTED_MODEL_ID/EXPECTED_TRIAL_ID")
            elif manifest["model_bundle"]["model_artifact_sha256"] != EXPECTED_MODEL_ARTIFACT_SHA256:
                errors.append("frozen model artifact SHA-256 in manifest does not match EXPECTED_MODEL_ARTIFACT_SHA256")
            else:
                passed.append("frozen_model_identity")

            if self.model_bundle_manifest_path.exists():
                live_model_manifest = json.loads(self.model_bundle_manifest_path.read_text(encoding="utf-8"))
                if live_model_manifest.get("model_artifact_sha256") != EXPECTED_MODEL_ARTIFACT_SHA256:
                    errors.append("live model bundle manifest.json SHA-256 does not match EXPECTED_MODEL_ARTIFACT_SHA256 -- bundle may have changed")
                else:
                    passed.append("live_model_bundle_unchanged")
            else:
                errors.append(f"live model bundle manifest not found at {self.model_bundle_manifest_path}")

            if manifest.get("dataset_sha256") != EXPECTED_DATASET_SHA256:
                errors.append("dataset_sha256 in manifest does not match EXPECTED_DATASET_SHA256")
            else:
                passed.append("dataset_fingerprint")

            if manifest.get("stage05_protocol_fingerprint") != EXPECTED_STAGE05_PROTOCOL_FINGERPRINT:
                errors.append("stage05_protocol_fingerprint in manifest does not match EXPECTED_STAGE05_PROTOCOL_FINGERPRINT")
            else:
                passed.append("stage05_protocol_fingerprint")

            code_and_doc_mismatches = verify_freeze_manifest(manifest, self.evaluation_package_dir, self.protocol_doc_paths, self.acceptance_doc_paths)
            if code_and_doc_mismatches:
                errors.extend(code_and_doc_mismatches)
            else:
                passed.append("frozen_evaluation_code_and_protocol")

            frozen_runtime = manifest.get("canonical_runtime", {})
            current_runtime = canonical_runtime()
            if frozen_runtime.get("python_major_minor") != current_runtime["python_major_minor"]:
                errors.append(f"canonical runtime mismatch: frozen python={frozen_runtime.get('python_major_minor')}, current={current_runtime['python_major_minor']}")
            elif frozen_runtime.get("sklearn_version") != current_runtime["sklearn_version"]:
                errors.append(f"canonical runtime mismatch: frozen sklearn={frozen_runtime.get('sklearn_version')}, current={current_runtime['sklearn_version']}")
            else:
                passed.append("canonical_runtime")

        try:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            marker = self.audit_log_path.parent / f".audit_write_check_{os.getpid()}"
            marker.write_text("ok", encoding="utf-8")
            marker.unlink()
            passed.append("audit_log_writable")
        except OSError as exc:
            errors.append(f"audit log directory is not writable: {exc}")

        if errors:
            self._append_audit({"event": "pre_unlock_checks_failed", "errors": errors, "passed": passed})
            raise GateError("Pre-unlock checks FAILED: " + "; ".join(errors))

        self._append_audit({"event": "pre_unlock_checks_passed", "passed": passed})
        return passed

    def unlock(self, *, authorization_phrase: str, allow_rerun: bool = False) -> UnlockToken:
        """Raises GateError/AlreadyEvaluatedError on any failed check. Only
        returns an UnlockToken when EVERY check in run_checks() passed."""
        self.run_checks(authorization_phrase=authorization_phrase, allow_rerun=allow_rerun)
        token = UnlockToken(_nonce=str(uuid.uuid4()))
        self._append_audit({"event": "unlock_token_issued", "token_nonce": token._nonce})
        return token
