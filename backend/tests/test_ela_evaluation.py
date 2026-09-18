"""Deterministic tests for the Y-02 ELA evaluation."""

from pathlib import Path

from evaluation.ela import corpus, evaluate


def generate_test_corpus(
    tmp_path: Path,
    monkeypatch,
    directory_name: str = "generated",
) -> tuple[Path, dict]:
    repository_root = tmp_path / "repository"
    repository_root.mkdir(exist_ok=True)

    monkeypatch.setattr(corpus, "REPOSITORY_ROOT", repository_root)
    monkeypatch.setattr(evaluate, "REPOSITORY_ROOT", repository_root)

    output_dir = (
        repository_root / "evaluation" / "ela" / directory_name
    )
    manifest = corpus.generate_ela_corpus(output_dir)
    return output_dir, manifest


def test_ela_manifest_records_controlled_case_details(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _, manifest = generate_test_corpus(tmp_path, monkeypatch)

    assert manifest["task"] == "Y-02"
    assert manifest["generator_seed"] == 20260912
    assert manifest["production_code_modified"] is False
    assert manifest["case_count"] == 10

    required_fields = {
        "id",
        "file",
        "category",
        "seed",
        "source_encoding",
        "processing",
        "known_edit",
        "known_edit_region_xyxy",
        "ela_jpeg_quality",
        "highlight_threshold",
        "expected_interpretation",
        "image_sha256",
    }

    for case in manifest["cases"]:
        assert required_fields <= case.keys()
        assert isinstance(case["seed"], int)
        assert case["ela_jpeg_quality"] == 90
        assert case["highlight_threshold"] == 20
        assert len(case["image_sha256"]) == 64

    categories = {case["category"] for case in manifest["cases"]}
    assert {
        "png-control",
        "screenshot-control",
        "single-jpeg-control",
        "benign-recompression",
        "benign-processing",
        "controlled-edit",
    } <= categories

    edited_cases = [
        case for case in manifest["cases"] if case["known_edit"]
    ]
    assert len(edited_cases) == 1
    assert edited_cases[0]["known_edit_region_xyxy"] == [
        186,
        70,
        291,
        175,
    ]


def test_ela_corpus_generation_is_reproducible(
    tmp_path: Path,
    monkeypatch,
) -> None:
    first_dir, first = generate_test_corpus(
        tmp_path,
        monkeypatch,
        "first",
    )
    second_dir = (
        tmp_path / "repository" / "evaluation" / "ela" / "second"
    )
    second = corpus.generate_ela_corpus(second_dir)

    first_hashes = {
        case["id"]: case["image_sha256"] for case in first["cases"]
    }
    second_hashes = {
        case["id"]: case["image_sha256"] for case in second["cases"]
    }

    assert first_dir != second_dir
    assert first_hashes == second_hashes


def test_existing_ela_reports_benign_false_positive_conditions(
    tmp_path: Path,
    monkeypatch,
) -> None:
    output_dir, _ = generate_test_corpus(tmp_path, monkeypatch)
    results_path = output_dir / "results.json"

    results = evaluate.evaluate_manifest(
        output_dir / "manifest.json",
        results_path,
    )
    summary = results["summary"]

    assert summary["total_cases"] == 10
    assert summary["known_edit_case_count"] == 1
    assert summary["benign_case_count"] == 9
    assert summary["binary_false_positive_rate"] is None

    assert len(summary["benign_cases_with_highlighted_pixels"]) == 9
    assert (
        summary[
            "benign_cases_meeting_or_exceeding_edited_highlight_ratio"
        ]
    )
    assert (
        summary[
            "benign_cases_meeting_or_exceeding_edited_p95_error"
        ]
    )

    known_edit = summary["known_edit"]
    region_metrics = known_edit["region_metrics"]
    assert region_metrics is not None
    assert region_metrics["region_to_background_ratio"] is not None
    assert region_metrics["region_to_background_ratio"] < 1.0

    assert results_path.exists()
    for case in results["cases"]:
        heatmap_path = (
            tmp_path / "repository" / case["heatmap"]
        )
        assert heatmap_path.exists()