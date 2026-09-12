"""Generate the deterministic Y-01 steganography evaluation corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts.create_demo_corpus import (  # noqa: E402
    DEFAULT_PAYLOAD,
    DEFAULT_SEED,
    MARKER,
    generate_corpus,
)

CHANNEL_INDEX = {"red": 0, "green": 1, "blue": 2}


def payload_for_size(size: int) -> bytes:
    """Create deterministic printable payload bytes."""
    pattern = b"AYANA-Y01-"
    return (pattern * ((size // len(pattern)) + 1))[:size]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def embed_payload(
    image: Image.Image,
    payload: bytes,
    channel_order: str = "interleaved-rgb",
    include_marker: bool = True,
) -> Image.Image:
    """Embed bytes into bit plane zero using a controlled layout."""
    array = np.array(image.convert("RGB"), dtype=np.uint8)
    flat = array.reshape(-1)

    message = (MARKER if include_marker else b"") + payload + b"\0"
    bits = np.unpackbits(np.frombuffer(message, dtype=np.uint8))

    if channel_order == "interleaved-rgb":
        positions = np.arange(flat.size)
    elif channel_order in CHANNEL_INDEX:
        channel = CHANNEL_INDEX[channel_order]
        positions = np.arange(channel, flat.size, 3)
    else:
        raise ValueError(f"Unsupported channel order: {channel_order}")

    if bits.size > positions.size:
        raise ValueError("Payload exceeds image capacity")

    selected = positions[: bits.size]
    flat[selected] = (flat[selected] & 0xFE) | bits
    return Image.fromarray(array)


def embed_keyed_layout(
    image: Image.Image,
    payload: bytes,
    seed: int,
) -> Image.Image:
    """Embed marker and payload at deterministic shuffled positions.

    This represents an unsupported keyed layout, not real encryption.
    """
    array = np.array(image.convert("RGB"), dtype=np.uint8)
    flat = array.reshape(-1)
    message = MARKER + payload + b"\0"
    bits = np.unpackbits(np.frombuffer(message, dtype=np.uint8))

    rng = np.random.default_rng(seed)
    positions = rng.permutation(flat.size)[: bits.size]
    flat[positions] = (flat[positions] & 0xFE) | bits
    return Image.fromarray(array)


def generate_y01_corpus(output_dir: Path, seed: int = DEFAULT_SEED) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    image_dir = output_dir / "images"
    image_dir.mkdir(exist_ok=True)

    # Reuse the merged A-03 controls instead of duplicating their implementation.
    controls_dir = REPOSITORY_ROOT / "demo" / "generated"
    generate_corpus(controls_dir, payload=DEFAULT_PAYLOAD, seed=seed)
    cover = Image.open(controls_dir / "clean-cover.png").convert("RGB")

    cases: list[dict] = []

    def record(
        case_id: str,
        path: Path,
        category: str,
        payload: bytes | None,
        channel_order: str,
        embedding_method: str,
        expected_supported: bool,
        case_seed: int,
    ) -> None:
        cases.append(
            {
                "id": case_id,
                "file": path.relative_to(REPOSITORY_ROOT).as_posix(),
                "category": category,
                "seed": case_seed,
                "payload_size": len(payload) if payload is not None else 0,
                "payload_sha256": (
                    sha256_bytes(payload) if payload is not None else None
                ),
                "channel_order": channel_order,
                "bit_plane": 0,
                "embedding_method": embedding_method,
                "expected_supported_payload": expected_supported,
                "expected_result": (
                    "exact_payload"
                    if expected_supported
                    else "no_supported_payload"
                ),
                "image_sha256": sha256_file(path),
            }
        )

    clean_control = controls_dir / "clean-cover.png"
    record(
        "a03-clean-control",
        clean_control,
        "clean",
        None,
        "interleaved-rgb",
        "none",
        False,
        seed,
    )

    supported_control = controls_dir / "lsb-marker-payload.png"
    record(
        "a03-supported-control",
        supported_control,
        "supported",
        DEFAULT_PAYLOAD,
        "interleaved-rgb",
        "STEGv1 marker with NUL terminator",
        True,
        seed,
    )

    for size in (1, 16, 256, 4096):
        payload = payload_for_size(size)
        path = image_dir / f"interleaved-{size}.png"
        embed_payload(cover, payload).save(path)
        record(
            f"interleaved-{size}",
            path,
            "supported",
            payload,
            "interleaved-rgb",
            "STEGv1 marker with NUL terminator",
            True,
            seed,
        )

    for channel in ("red", "green", "blue"):
        payload = payload_for_size(64)
        path = image_dir / f"{channel}-channel.png"
        embed_payload(cover, payload, channel_order=channel).save(path)
        record(
            f"{channel}-channel",
            path,
            "unsupported-channel-layout",
            payload,
            channel,
            "single-channel STEGv1 bit-plane-zero embedding",
            False,
            seed,
        )

    markerless_payload = payload_for_size(64)
    markerless_path = image_dir / "markerless.png"
    embed_payload(
        cover,
        markerless_payload,
        include_marker=False,
    ).save(markerless_path)
    record(
        "markerless",
        markerless_path,
        "unsupported-marker",
        markerless_payload,
        "interleaved-rgb",
        "bit-plane-zero bytes without supported marker",
        False,
        seed,
    )

    keyed_seed = seed + 500
    keyed_payload = np.random.default_rng(keyed_seed).bytes(128)
    keyed_path = image_dir / "keyed-random-layout.png"
    embed_keyed_layout(cover, keyed_payload, keyed_seed).save(keyed_path)
    record(
        "keyed-random-layout",
        keyed_path,
        "unsupported-keyed-layout",
        keyed_payload,
        "keyed-shuffled-rgb",
        "deterministic shuffled positions; encrypted-like bytes",
        False,
        keyed_seed,
    )

    for offset in range(5):
        noise_seed = seed + 100 + offset
        rng = np.random.default_rng(noise_seed)
        noise = rng.integers(0, 256, size=(240, 320, 3), dtype=np.uint8)
        path = image_dir / f"clean-noise-{offset}.png"
        Image.fromarray(noise).save(path)
        record(
            f"clean-noise-{offset}",
            path,
            "clean-noise",
            None,
            "interleaved-rgb",
            "none",
            False,
            noise_seed,
        )

    manifest = {
        "schema_version": 1,
        "task": "Y-01",
        "generator_seed": seed,
        "production_code_modified": False,
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
        default=REPOSITORY_ROOT
        / "evaluation"
        / "steganography"
        / "generated",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    manifest = generate_y01_corpus(args.output_dir, args.seed)
    print(f"Generated {manifest['case_count']} deterministic Y-01 cases")
    print(f"Manifest: {args.output_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()