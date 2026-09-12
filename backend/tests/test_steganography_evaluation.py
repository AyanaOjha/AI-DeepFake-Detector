"""Deterministic tests for the Y-01 steganography evaluation."""

from pathlib import Path

from evaluation.steganography import corpus, evaluate


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
        repository_root
        / "evaluation"
        / "steganography"
        / directory_name
    )
    manifest = corpus.generate_y01_corpus(output_dir)
    return output_dir, manifest


def test_manifest_records_every_control_parameter(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _, manifest = generate_test_corpus(tmp_path, monkeypatch)

    assert manifest["task"] == "Y-01"
    assert manifest["generator_seed"] == 20260912
    assert manifest["production_code_modified"] is False
    assert manifest["case_count"] == 16

    required_fields = {
        "id",
        "file",
        "category",
        "seed",
        "payload_size",
        "payload_sha256",
        "channel_order",
        "bit_plane",
        "embedding_method",
        "expected_supported_payload",
        "expected_result",
        "image_sha256",
    }

    for case in manifest["cases"]:
        assert required_fields <= case.keys()
        assert isinstance(case["seed"], int)
        assert case["payload_size"] >= 0
        assert case["bit_plane"] == 0
        assert len(case["image_sha256"]) == 64

    supported_sizes = sorted(
        case["payload_size"]
        for case in manifest["cases"]
        if case["expected_supported_payload"]
    )
    assert supported_sizes == [1, 16, 23, 256, 4096]

    channel_orders = {
        case["channel_order"] for case in manifest["cases"]
    }
    assert {
        "interleaved-rgb",
        "red",
        "green",
        "blue",
        "keyed-shuffled-rgb",
    } <= channel_orders


def test_corpus_generation_is_reproducible(
    tmp_path: Path,
    monkeypatch,
) -> None:
    first_dir, first = generate_test_corpus(
        tmp_path,
        monkeypatch,
        "first",
    )
    second_dir = (
        tmp_path
        / "repository"
        / "evaluation"
        / "steganography"
        / "second"
    )
    second = corpus.generate_y01_corpus(second_dir)

    first_hashes = {
        case["id"]: case["image_sha256"] for case in first["cases"]
    }
    second_hashes = {
        case["id"]: case["image_sha256"] for case in second["cases"]
    }

    assert first_dir != second_dir
    assert first_hashes == second_hashes


def test_existing_lsb_analyser_against_controlled_corpus(
    tmp_path: Path,
    monkeypatch,
) -> None:
    output_dir, _ = generate_test_corpus(tmp_path, monkeypatch)
    results = evaluate.evaluate_manifest(output_dir / "manifest.json")
    summary = results["summary"]

    assert summary["total_cases"] == 16
    assert summary["supported_case_count"] == 5
    assert summary["supported_payloads_detected"] == 5
    assert summary["supported_extraction_success_rate_percent"] == 100.0
    assert summary["correct_payload_count"] == 5
    assert summary["payload_correctness_rate_percent"] == 100.0
    assert summary["clean_case_count"] == 6
    assert summary["clean_false_positive_count"] == 0
    assert summary["clean_false_positive_rate_percent"] == 0.0
    assert summary["false_negative_count"] == 0
    assert summary["incorrect_payload_count"] == 0
    assert summary["unsupported_case_count"] == 5
    assert summary["unsupported_detection_count"] == 0

    assert all(
        case["outcome"] == "PASS" for case in results["cases"]
    )