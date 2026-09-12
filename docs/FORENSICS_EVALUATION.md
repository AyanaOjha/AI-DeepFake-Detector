# Steganography Forensics Evaluation

## Scope

This document records Ayana's Y-01 evaluation of the existing
`backend/app/forensics/lsb.py` implementation. The evaluation was performed on
12 September 2026 without changing the production LSB analyser.

The evaluation measures controlled behaviour only. LSB statistics and successful
marker extraction do not prove that an image contains malicious steganography,
and a negative result does not prove that an image is clean.

## Methodology

The evaluation uses deterministic, project-generated PNG images. It reuses the
merged A-03 controls from `scripts/create_demo_corpus.py` and expands them with
additional payload sizes, channel layouts, marker-free content, keyed layouts,
and random/noisy clean controls.

The principal seed is `20260912`. Every generated case records:

- Seed
- Payload size
- Channel order
- Bit plane
- Embedding method
- Expected supported result
- Image SHA-256
- Expected payload SHA-256, where applicable

The existing `analyse_lsb` function was run against each image. A supported
extraction counted as correct only when the extracted payload SHA-256 matched
the expected payload SHA-256.

Generated images, manifests, and raw result files are placed under
`evaluation/steganography/generated/`. This directory is excluded from Git
because all its contents can be regenerated.

## Corpus design

All embedding cases use bit plane zero.

| Case | Category | Seed | Payload bytes | Channel order | Embedding method | Expected |
| --- | --- | ---: | ---: | --- | --- | --- |
| `a03-clean-control` | Clean control | 20260912 | 0 | Interleaved RGB | None | No supported payload |
| `a03-supported-control` | Supported control | 20260912 | 23 | Interleaved RGB | `STEGv1` marker and NUL terminator | Exact payload |
| `interleaved-1` | Supported | 20260912 | 1 | Interleaved RGB | `STEGv1` marker and NUL terminator | Exact payload |
| `interleaved-16` | Supported | 20260912 | 16 | Interleaved RGB | `STEGv1` marker and NUL terminator | Exact payload |
| `interleaved-256` | Supported | 20260912 | 256 | Interleaved RGB | `STEGv1` marker and NUL terminator | Exact payload |
| `interleaved-4096` | Supported | 20260912 | 4096 | Interleaved RGB | `STEGv1` marker and NUL terminator | Exact payload |
| `red-channel` | Unsupported channel layout | 20260912 | 64 | Red only | Single-channel `STEGv1` embedding | No supported payload |
| `green-channel` | Unsupported channel layout | 20260912 | 64 | Green only | Single-channel `STEGv1` embedding | No supported payload |
| `blue-channel` | Unsupported channel layout | 20260912 | 64 | Blue only | Single-channel `STEGv1` embedding | No supported payload |
| `markerless` | Unsupported marker | 20260912 | 64 | Interleaved RGB | Bytes without a supported marker | No supported payload |
| `keyed-random-layout` | Unsupported keyed layout | 20261412 | 128 | Shuffled RGB positions | Deterministic shuffled positions and high-entropy bytes | No supported payload |
| `clean-noise-0` | Clean/noisy | 20261012 | 0 | Interleaved RGB inspected | None | No supported payload |
| `clean-noise-1` | Clean/noisy | 20261013 | 0 | Interleaved RGB inspected | None | No supported payload |
| `clean-noise-2` | Clean/noisy | 20261014 | 0 | Interleaved RGB inspected | None | No supported payload |
| `clean-noise-3` | Clean/noisy | 20261015 | 0 | Interleaved RGB inspected | None | No supported payload |
| `clean-noise-4` | Clean/noisy | 20261016 | 0 | Interleaved RGB inspected | None | No supported payload |

The keyed case is an encrypted-like negative control, not an implementation or
validation of real encryption. It uses deterministic pseudo-random payload bytes
and shuffled embedding positions to demonstrate a layout outside the current
analyser's supported sequential extraction model.

## Results

| Metric | Result |
| --- | ---: |
| Total controlled cases | 16 |
| Supported-payload extraction success | 5/5 (100.0%) |
| Exact extracted-payload correctness | 5/5 (100.0%) |
| Clean/noisy image false positives | 0/6 (0.0%) |
| False negatives among supported cases | 0 |
| Incorrect supported payloads | 0 |
| Unsupported cases detected as supported | 0/5 |

All four evaluated payload sizes—1, 16, 256, and 4096 bytes—were extracted
correctly from the interleaved RGB bit-plane-zero layout. The 23-byte merged
A-03 supported control was also extracted correctly.

A `PASS` for an unsupported case means that the analyser did not claim to
support or extract that case. It does not mean that the analyser detected the
presence of hidden data.

## False positives and false negatives

No supported payload was reported for the A-03 clean PNG or the five
deterministic random/noisy PNG images. The measured clean-image false-positive
rate was therefore 0/6.

No false negatives occurred among the five cases that followed the currently
supported interleaved RGB `STEGv1` layout.

These rates apply only to this small deterministic corpus. They must not be
presented as estimates of performance on arbitrary real-world images.

## Unsupported cases

The current analyser did not extract:

- Red-only bit-plane-zero embedding
- Green-only bit-plane-zero embedding
- Blue-only bit-plane-zero embedding
- Interleaved bytes without a supported marker
- Deterministically shuffled keyed positions containing high-entropy bytes

These outcomes match the documented expectations. The analyser is not a general
steganography decoder and does not discover keys, decrypt payloads, or test every
possible channel order and embedding algorithm.

## Security and forensic limitations

- LSB statistics are indicators, not proof of steganography or image authenticity.
- Marker-based extraction can identify only supported layouts and payload formats.
- A negative result does not establish that an image contains no hidden data.
- Encrypted, keyed, compressed, transformed, or adaptively embedded payloads may
  not be recoverable.
- Re-encoding, resizing, cropping, filtering, and colour conversion can modify or
  destroy LSB payloads.
- Random data can resemble statistical irregularities, while deliberately crafted
  payloads may avoid simple indicators.
- Payload previews should be treated as untrusted data and should not be executed.
- The corpus contains only synthetic, licence-safe media and no private data,
  secrets, third-party datasets, or real forensic evidence.
- The reported rates do not demonstrate real-world generalisation.

## Reproduction

Create and activate the repository's Python 3.11 virtual environment before
running these commands from the repository root.

```powershell
python scripts/create_demo_corpus.py
python evaluation/steganography/corpus.py
python evaluation/steganography/evaluate.py
python -m pytest -q
python -m ruff check backend evaluation scripts
git diff --check
```

To run only the Y-01 automated tests:

```powershell
python -m pytest backend/tests/test_steganography_evaluation.py -q
```

The corpus generator writes its complete per-case manifest to:

```text
evaluation/steganography/generated/manifest.json
```

The evaluator writes the detailed measured results to:

```text
evaluation/steganography/generated/results.json
```

Both files are reproducible generated evidence and are excluded from Git along
with the generated PNG files.