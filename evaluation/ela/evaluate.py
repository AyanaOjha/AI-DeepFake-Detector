"""Evaluate the existing ELA implementation against the Y-02 corpus."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.forensics.ela import generate_ela  # noqa: E402


def heatmap_region_metrics(
    heatmap_path: Path,
    region: list[int] | None,
) -> dict[str, float] | None:
    """Compare a known edited region with the remaining heatmap."""
    if region is None:
        return None

    with Image.open(heatmap_path) as image:
        heatmap = np.asarray(image.convert("RGB"), dtype=np.float64)

    intensity = heatmap.max(axis=2)
    x1, y1, x2, y2 = region

    mask = np.zeros(intensity.shape, dtype=bool)
    mask[y1:y2, x1:x2] = True

    region_mean = float(intensity[mask].mean())
    background_mean = float(intensity[~mask].mean())
    ratio = (
        region_mean / background_mean
        if background_mean > 0
        else float("inf")
    )

    return {
        "known_region_mean_heatmap_intensity": round(region_mean, 4),
        "background_mean_heatmap_intensity": round(background_mean, 4),
        "region_to_background_ratio": (
            round(ratio, 4) if np.isfinite(ratio) else None
        ),
    }


def evaluate_case(
    case: dict[str, Any],
    heatmap_dir: Path,
) -> dict[str, Any]:
    source_path = REPOSITORY_ROOT / case["file"]
    heatmap_path = heatmap_dir / f"{case['id']}.png"

    result = generate_ela(
        source_path,
        heatmap_path,
        jpeg_quality=case["ela_jpeg_quality"],
        highlight_threshold=case["highlight_threshold"],
    )

    return {
        "id": case["id"],
        "file": case["file"],
        "category": case["category"],
        "seed": case["seed"],
        "source_encoding": case["source_encoding"],
        "processing": case["processing"],
        "known_edit": case["known_edit"],
        "known_edit_region_xyxy": case["known_edit_region_xyxy"],
        "expected_interpretation": case["expected_interpretation"],
        "ela_jpeg_quality": result.jpeg_quality,
        "highlight_threshold": case["highlight_threshold"],
        "mean_error": result.mean_error,
        "percentile_95_error": result.percentile_95_error,
        "max_error": result.max_error,
        "highlighted_pixel_ratio": result.highlighted_pixel_ratio,
        "heatmap": heatmap_path.relative_to(REPOSITORY_ROOT).as_posix(),
        "region_metrics": heatmap_region_metrics(
            heatmap_path,
            case["known_edit_region_xyxy"],
        ),
    }


def evaluate_manifest(
    manifest_path: Path,
    results_path: Path,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    heatmap_dir = results_path.parent / "heatmaps"
    heatmap_dir.mkdir(parents=True, exist_ok=True)

    cases = [
        evaluate_case(case, heatmap_dir)
        for case in manifest["cases"]
    ]

    edited_cases = [case for case in cases if case["known_edit"]]
    benign_cases = [case for case in cases if not case["known_edit"]]

    if len(edited_cases) != 1:
        raise ValueError("Y-02 corpus must contain exactly one known edit")

    edited = edited_cases[0]
    edited_ratio = edited["highlighted_pixel_ratio"]
    edited_p95 = edited["percentile_95_error"]

    benign_with_highlighted_pixels = [
        case["id"]
        for case in benign_cases
        if case["highlighted_pixel_ratio"] > 0
    ]
    benign_meeting_edited_ratio = [
        case["id"]
        for case in benign_cases
        if case["highlighted_pixel_ratio"] >= edited_ratio
    ]
    benign_meeting_edited_p95 = [
        case["id"]
        for case in benign_cases
        if case["percentile_95_error"] >= edited_p95
    ]

    strongest_benign_by_ratio = max(
        benign_cases,
        key=lambda case: case["highlighted_pixel_ratio"],
    )
    strongest_benign_by_p95 = max(
        benign_cases,
        key=lambda case: case["percentile_95_error"],
    )

    summary = {
        "total_cases": len(cases),
        "known_edit_case_count": len(edited_cases),
        "benign_case_count": len(benign_cases),
        "binary_false_positive_rate": None,
        "binary_false_positive_rate_reason": (
            "The production ELA implementation returns measurements and "
            "a heatmap but does not define a binary manipulation decision."
        ),
        "benign_cases_with_highlighted_pixels": (
            benign_with_highlighted_pixels
        ),
        "benign_cases_meeting_or_exceeding_edited_highlight_ratio": (
            benign_meeting_edited_ratio
        ),
        "benign_cases_meeting_or_exceeding_edited_p95_error": (
            benign_meeting_edited_p95
        ),
        "strongest_benign_by_highlight_ratio": {
            "id": strongest_benign_by_ratio["id"],
            "value": strongest_benign_by_ratio[
                "highlighted_pixel_ratio"
            ],
        },
        "strongest_benign_by_p95_error": {
            "id": strongest_benign_by_p95["id"],
            "value": strongest_benign_by_p95[
                "percentile_95_error"
            ],
        },
        "known_edit": {
            "id": edited["id"],
            "mean_error": edited["mean_error"],
            "percentile_95_error": edited["percentile_95_error"],
            "max_error": edited["max_error"],
            "highlighted_pixel_ratio": edited_ratio,
            "region_metrics": edited["region_metrics"],
        },
    }

    evaluation = {
        "schema_version": 1,
        "task": "Y-02",
        "production_implementation": "backend/app/forensics/ela.py",
        "production_code_modified": False,
        "manifest": manifest_path.relative_to(
            REPOSITORY_ROOT
        ).as_posix(),
        "interpretation_boundary": manifest[
            "interpretation_boundary"
        ],
        "summary": summary,
        "cases": cases,
    }

    results_path.write_text(
        json.dumps(evaluation, indent=2) + "\n",
        encoding="utf-8",
    )
    return evaluation


def print_results(evaluation: dict[str, Any]) -> None:
    summary = evaluation["summary"]
    known_edit = summary["known_edit"]

    ratio_matches = summary[
        "benign_cases_meeting_or_exceeding_edited_highlight_ratio"
    ]
    p95_matches = summary[
        "benign_cases_meeting_or_exceeding_edited_p95_error"
    ]

    print(f"Total cases: {summary['total_cases']}")
    print(f"Known edit cases: {summary['known_edit_case_count']}")
    print(f"Benign/control cases: {summary['benign_case_count']}")
    print("Binary false-positive rate: not defined")
    print(
        "Benign cases with highlighted pixels: "
        f"{len(summary['benign_cases_with_highlighted_pixels'])}"
    )
    print(
        "Benign cases meeting/exceeding edited highlight ratio: "
        f"{ratio_matches}"
    )
    print(
        "Benign cases meeting/exceeding edited p95 error: "
        f"{p95_matches}"
    )
    print(
        "Known edit highlighted ratio: "
        f"{known_edit['highlighted_pixel_ratio']}"
    )
    print(
        "Known edit region/background metrics: "
        f"{known_edit['region_metrics']}"
    )

    print("\nCase measurements:")
    for case in evaluation["cases"]:
        print(
            f"- {case['id']}: "
            f"mean={case['mean_error']}, "
            f"p95={case['percentile_95_error']}, "
            f"max={case['max_error']}, "
            f"highlighted={case['highlighted_pixel_ratio']}"
        )

def main() -> None:
    generated_dir = (
        REPOSITORY_ROOT / "evaluation" / "ela" / "generated"
    )
    default_manifest = generated_dir / "manifest.json"
    default_results = generated_dir / "results.json"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=default_manifest,
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=default_results,
    )
    args = parser.parse_args()

    evaluation = evaluate_manifest(args.manifest, args.results)
    print_results(evaluation)
    print(f"\nResults: {args.results}")


if __name__ == "__main__":
    main()