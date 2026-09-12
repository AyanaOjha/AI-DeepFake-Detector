"""Evaluate the existing LSB analyser against the Y-01 corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.forensics.lsb import analyse_lsb  # noqa: E402


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def percentage(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    image_path = REPOSITORY_ROOT / case["file"]
    analysis = analyse_lsb(image_path)

    detected = bool(analysis.findings["supported_payload_detected"])
    extracted = analysis.extracted_payload
    extracted_hash = sha256_bytes(extracted) if extracted is not None else None

    expected_supported = bool(case["expected_supported_payload"])
    expected_hash = case["payload_sha256"]

    payload_correct = (
        expected_supported
        and detected
        and extracted_hash == expected_hash
    )

    if expected_supported:
        if not detected:
            outcome = "FALSE_NEGATIVE"
        elif not payload_correct:
            outcome = "INCORRECT_PAYLOAD"
        else:
            outcome = "PASS"
    elif detected:
        outcome = "UNEXPECTED_DETECTION"
    else:
        outcome = "PASS"

    return {
        "id": case["id"],
        "file": case["file"],
        "category": case["category"],
        "seed": case["seed"],
        "payload_size": case["payload_size"],
        "channel_order": case["channel_order"],
        "bit_plane": case["bit_plane"],
        "embedding_method": case["embedding_method"],
        "expected_supported_payload": expected_supported,
        "actual_supported_payload": detected,
        "expected_payload_sha256": expected_hash,
        "extracted_payload_sha256": extracted_hash,
        "extracted_size": (
            len(extracted) if extracted is not None else 0
        ),
        "payload_correct": payload_correct if expected_supported else None,
        "extraction_method": analysis.findings["extraction_method"],
        "outcome": outcome,
    }


def evaluate_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cases = [evaluate_case(case) for case in manifest["cases"]]

    supported = [
        case for case in cases if case["expected_supported_payload"]
    ]
    clean = [
        case
        for case in cases
        if case["category"] in {"clean", "clean-noise"}
    ]
    unsupported = [
        case
        for case in cases
        if case["category"].startswith("unsupported-")
    ]

    supported_detected = sum(
        case["actual_supported_payload"] for case in supported
    )
    correct_payloads = sum(
        case["payload_correct"] is True for case in supported
    )
    clean_false_positives = sum(
        case["actual_supported_payload"] for case in clean
    )
    false_negatives = sum(
        case["outcome"] == "FALSE_NEGATIVE" for case in supported
    )
    incorrect_payloads = sum(
        case["outcome"] == "INCORRECT_PAYLOAD" for case in supported
    )
    unsupported_detections = sum(
        case["actual_supported_payload"] for case in unsupported
    )

    summary = {
        "total_cases": len(cases),
        "supported_case_count": len(supported),
        "supported_payloads_detected": supported_detected,
        "supported_extraction_success_rate_percent": percentage(
            supported_detected,
            len(supported),
        ),
        "correct_payload_count": correct_payloads,
        "payload_correctness_rate_percent": percentage(
            correct_payloads,
            len(supported),
        ),
        "clean_case_count": len(clean),
        "clean_false_positive_count": clean_false_positives,
        "clean_false_positive_rate_percent": percentage(
            clean_false_positives,
            len(clean),
        ),
        "false_negative_count": false_negatives,
        "incorrect_payload_count": incorrect_payloads,
        "unsupported_case_count": len(unsupported),
        "unsupported_detection_count": unsupported_detections,
    }

    return {
        "schema_version": 1,
        "task": "Y-01",
        "production_implementation": "backend/app/forensics/lsb.py",
        "production_code_modified": False,
        "manifest": manifest_path.relative_to(REPOSITORY_ROOT).as_posix(),
        "summary": summary,
        "cases": cases,
    }


def print_results(results: dict[str, Any]) -> None:
    summary = results["summary"]

    print(f"Total cases: {summary['total_cases']}")
    print(
        "Supported extraction success: "
        f"{summary['supported_payloads_detected']}/"
        f"{summary['supported_case_count']} "
        f"({summary['supported_extraction_success_rate_percent']}%)"
    )
    print(
        "Exact payload correctness: "
        f"{summary['correct_payload_count']}/"
        f"{summary['supported_case_count']} "
        f"({summary['payload_correctness_rate_percent']}%)"
    )
    print(
        "Clean-image false positives: "
        f"{summary['clean_false_positive_count']}/"
        f"{summary['clean_case_count']} "
        f"({summary['clean_false_positive_rate_percent']}%)"
    )
    print(f"False negatives: {summary['false_negative_count']}")
    print(
        "Unsupported-layout detections: "
        f"{summary['unsupported_detection_count']}/"
        f"{summary['unsupported_case_count']}"
    )

    print("\nCase results:")
    for case in results["cases"]:
        print(
            f"- {case['id']}: {case['outcome']} "
            f"(payload={case['payload_size']} bytes, "
            f"channels={case['channel_order']}, "
            f"bit-plane={case['bit_plane']})"
        )


def main() -> None:
    default_manifest = (
        REPOSITORY_ROOT
        / "evaluation"
        / "steganography"
        / "generated"
        / "manifest.json"
    )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=default_manifest,
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=default_manifest.parent / "results.json",
    )
    args = parser.parse_args()

    results = evaluate_manifest(args.manifest)
    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.results.write_text(
        json.dumps(results, indent=2) + "\n",
        encoding="utf-8",
    )

    print_results(results)
    print(f"\nResults: {args.results}")


if __name__ == "__main__":
    main()