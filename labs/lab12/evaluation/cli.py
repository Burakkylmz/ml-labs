"""The explicit, separate command for the Phase B unlock. Normal execution
(pytest, the Stage 14 notebook, the FastAPI service) NEVER imports or
calls into this module's `main()` -- it is reached only by deliberately
running:

    uv run python -m evaluation.cli unlock --confirm-phrase "I AUTHORIZE 2015 PROTECTED TEST EVALUATION"

**This command is not invoked anywhere in this preparation task.** It
exists so that, when the user gives separate, explicit authorization, a
single, auditable, non-accidental entrypoint is ready -- not so that this
task can run it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .contracts import AlreadyEvaluatedError, EvaluationError, EXPECTED_B1_DEVELOPMENT_MEAN_USD
from .gate import PreUnlockGate
from .runner import FinalEvaluationRunner

LAB12_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = LAB12_ROOT.parent.parent / "data" / "freight_cost" / "SCMS_Delivery_History_Dataset_20150929.csv"
SPLIT_MANIFEST_PATH = LAB12_ROOT / "artifacts" / "stage05_split_manifest.csv"
MODEL_BUNDLE_DIR = LAB12_ROOT / "artifacts" / "stage13_model_bundle" / "v1"
ALLOWED_ROOT = LAB12_ROOT / "artifacts" / "stage13_model_bundle"
FREEZE_MANIFEST_PATH = LAB12_ROOT / "artifacts" / "stage14_evaluation_freeze_manifest_v3.json"
PROTOCOL_DOC_PATHS = [LAB12_ROOT / "docs" / "stage14_final_evaluation_protocol.md"]
ACCEPTANCE_DOC_PATHS = [LAB12_ROOT / "docs" / "stage14_metric_baseline_contract.md"]
MODEL_BUNDLE_MANIFEST_PATH = MODEL_BUNDLE_DIR / "manifest.json"
AUDIT_LOG_PATH = LAB12_ROOT / "artifacts" / "stage14_evaluation_audit_log.json"
COMPLETED_REPORT_PATH = LAB12_ROOT / "artifacts" / "stage14_final_evaluation_report.json"


def _build_gate() -> PreUnlockGate:
    return PreUnlockGate(
        evaluation_package_dir=Path(__file__).resolve().parent,
        freeze_manifest_v2_path=FREEZE_MANIFEST_PATH,
        protocol_doc_paths=PROTOCOL_DOC_PATHS,
        acceptance_doc_paths=ACCEPTANCE_DOC_PATHS,
        model_bundle_manifest_path=MODEL_BUNDLE_MANIFEST_PATH,
        audit_log_path=AUDIT_LOG_PATH,
        completed_report_path=COMPLETED_REPORT_PATH,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m evaluation.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    unlock_parser = subparsers.add_parser("unlock", help="Run the one-time 2015 Protected Test final evaluation. DO NOT run without separate, explicit user authorization.")
    unlock_parser.add_argument("--confirm-phrase", required=True, help='Must be exactly "I AUTHORIZE 2015 PROTECTED TEST EVALUATION"')
    unlock_parser.add_argument("--allow-rerun", action="store_true", help="Permit re-running when a completed report already exists.")

    args = parser.parse_args(argv)

    if args.command == "unlock":
        gate = _build_gate()
        try:
            token = gate.unlock(authorization_phrase=args.confirm_phrase, allow_rerun=args.allow_rerun)
        except AlreadyEvaluatedError as exc:
            print(f"REFUSED (already evaluated): {exc}", file=sys.stderr)
            return 2
        except EvaluationError as exc:
            print(f"REFUSED (gate check failed): {exc}", file=sys.stderr)
            return 1

        runner = FinalEvaluationRunner(
            dataset_path=DATASET_PATH, split_manifest_path=SPLIT_MANIFEST_PATH,
            model_bundle_dir=MODEL_BUNDLE_DIR, allowed_root=ALLOWED_ROOT,
            report_path=COMPLETED_REPORT_PATH,
            expected_development_b1_mean_usd=EXPECTED_B1_DEVELOPMENT_MEAN_USD,
        )
        report = runner.run(token)
        print(f"Final evaluation complete. Acceptance: {report['acceptance']['classification']}")
        print(f"Report written to: {COMPLETED_REPORT_PATH}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
