"""Generate the deterministic Y-02 ELA evaluation corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageFilter

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts.create_demo_corpus import (  # noqa: E402
    DEFAULT_SEED,
    generate_corpus,
)

ELA_JPEG_QUALITY = 90
ELA_HIGHLIGHT_THRESHOLD = 20


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_jpeg(image: Image.Image, path: Path, quality: int) -> None:
    image.convert("RGB").save(
        path,
        format="JPEG",
        quality=quality,
        subsampling=0,
        optimize=False,
        progressive=False,
    )


def generate_ela_corpus(
    output_dir: Path,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    """Create deterministic ELA controls without modifying production code."""
    output_dir.mkdir(parents=True, exist_ok=True)
    image_dir = output_dir / "images"
    image_dir.mkdir(exist_ok=True)

    controls_dir = REPOSITORY_ROOT / "demo" / "generated"
    generate_corpus(controls_dir, seed=seed)

    with Image.open(controls_dir / "clean-cover.png") as source:
        cover = source.convert("RGB")

    cases: list[dict[str, Any]] = []

    def record(
        case_id: str,
        path: Path,
        *,
        category: str,
        case_seed: int,
        source_encoding: str,
        processing: str,
        known_edit: bool,
        edit_region: list[int] | None,
        expected_interpretation: str,
    ) -> None:
        cases.append(
            {
                "id": case_id,
                "file": path.relative_to(REPOSITORY_ROOT).as_posix(),
                "category": category,
                "seed": case_seed,
                "source_encoding": source_encoding,
                "processing": processing,
                "known_edit": known_edit,
                "known_edit_region_xyxy": edit_region,
                "ela_jpeg_quality": ELA_JPEG_QUALITY,
                "highlight_threshold": ELA_HIGHLIGHT_THRESHOLD,
                "expected_interpretation": expected_interpretation,
                "image_sha256": sha256_file(path),
            }
        )

    record(
        "png-clean-cover",
        controls_dir / "clean-cover.png",
        category="png-control",
        case_seed=seed,
        source_encoding="PNG",
        processing="Synthetic cover saved losslessly",
        known_edit=False,
        edit_region=None,
        expected_interpretation=(
            "PNG-to-JPEG comparison may highlight texture and edges; "
            "this is not evidence of manipulation"
        ),
    )
    record(
        "png-screenshot",
        controls_dir / "screenshot-style.png",
        category="screenshot-control",
        case_seed=seed,
        source_encoding="PNG",
        processing="Synthetic interface-style image with flat regions and sharp edges",
        known_edit=False,
        edit_region=None,
        expected_interpretation=(
            "Ordinary interface edges may produce visible ELA response"
        ),
    )
    record(
        "jpeg-original-95",
        controls_dir / "original-quality-95.jpg",
        category="single-jpeg-control",
        case_seed=seed,
        source_encoding="JPEG quality 95",
        processing="Single JPEG encoding",
        known_edit=False,
        edit_region=None,
        expected_interpretation="Reference single-encoding JPEG case",
    )
    record(
        "jpeg-recompressed-55",
        controls_dir / "recompressed-quality-55.jpg",
        category="benign-recompression",
        case_seed=seed,
        source_encoding="JPEG quality 95 then quality 55",
        processing="Decoded and recompressed without a content edit",
        known_edit=False,
        edit_region=None,
        expected_interpretation=(
            "Recompression can create strong ELA response without manipulation"
        ),
    )
    record(
        "jpeg-edited-region-88",
        controls_dir / "edited-region-quality-88.jpg",
        category="controlled-edit",
        case_seed=seed,
        source_encoding="JPEG quality 95 then edited and saved at quality 88",
        processing="Mirrored rectangular region inserted before final encoding",
        known_edit=True,
        edit_region=[186, 70, 291, 175],
        expected_interpretation=(
            "Compare the known edit region with the background; "
            "localisation is not guaranteed"
        ),
    )

    for quality in (75, 50):
        path = image_dir / f"single-quality-{quality}.jpg"
        save_jpeg(cover, path, quality)
        record(
            f"jpeg-single-{quality}",
            path,
            category="single-jpeg-control",
            case_seed=seed,
            source_encoding=f"JPEG quality {quality}",
            processing="Single JPEG encoding",
            known_edit=False,
            edit_region=None,
            expected_interpretation=(
                "Lower JPEG quality alone may increase ELA response"
            ),
        )

    resized_path = image_dir / "resized-quality-90.jpg"
    reduced = cover.resize((160, 120), Image.Resampling.BICUBIC)
    resized = reduced.resize(cover.size, Image.Resampling.BICUBIC)
    save_jpeg(resized, resized_path, 90)
    record(
        "jpeg-resized",
        resized_path,
        category="benign-processing",
        case_seed=seed,
        source_encoding="PNG then resized and saved as JPEG quality 90",
        processing="Downscaled and upscaled with bicubic resampling",
        known_edit=False,
        edit_region=None,
        expected_interpretation=(
            "Resampling may produce edge response without deceptive editing"
        ),
    )

    blurred_path = image_dir / "blurred-quality-90.jpg"
    blurred = cover.filter(ImageFilter.GaussianBlur(radius=1.5))
    save_jpeg(blurred, blurred_path, 90)
    record(
        "jpeg-blurred",
        blurred_path,
        category="benign-processing",
        case_seed=seed,
        source_encoding="PNG then saved as JPEG quality 90",
        processing="Gaussian blur radius 1.5 before encoding",
        known_edit=False,
        edit_region=None,
        expected_interpretation=(
            "Filtering changes compression residuals without implying manipulation"
        ),
    )

    noise_seed = seed + 301
    rng = np.random.default_rng(noise_seed)
    cover_array = np.asarray(cover, dtype=np.int16)
    noise = rng.normal(0.0, 8.0, size=cover_array.shape)
    noisy_array = np.clip(cover_array + noise, 0, 255).astype(np.uint8)
    noisy_path = image_dir / "noise-quality-90.jpg"
    save_jpeg(Image.fromarray(noisy_array), noisy_path, 90)
    record(
        "jpeg-noise",
        noisy_path,
        category="benign-processing",
        case_seed=noise_seed,
        source_encoding="PNG with deterministic noise, then JPEG quality 90",
        processing="Zero-mean Gaussian noise with standard deviation 8",
        known_edit=False,
        edit_region=None,
        expected_interpretation=(
            "Noise may create widespread ELA response without a local edit"
        ),
    )

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "task": "Y-02",
        "generator_seed": seed,
        "production_code_modified": False,
        "ela_configuration": {
            "jpeg_quality": ELA_JPEG_QUALITY,
            "highlight_threshold": ELA_HIGHLIGHT_THRESHOLD,
        },
        "interpretation_boundary": (
            "ELA measurements compare recompression residuals and are not "
            "binary proof of manipulation or authenticity"
        ),
        "case_count": len(cases),
        "cases": cases,
    }

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPOSITORY_ROOT / "evaluation" / "ela" / "generated",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    manifest = generate_ela_corpus(args.output_dir, args.seed)
    print(f"Generated {manifest['case_count']} deterministic Y-02 ELA cases")
    print(f"Manifest: {args.output_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()