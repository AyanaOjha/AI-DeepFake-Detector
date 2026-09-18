# Forensics Evaluation

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
## Y-02 ELA Evaluation

### Scope

This section records Ayana's Y-02 evaluation of the existing
`backend/app/forensics/ela.py` implementation. Production ELA code was not changed.

ELA measures differences produced by JPEG recompression. The implementation returns
continuous measurements and a heatmap; it does not define a binary authentic/fake
decision. Therefore, a binary false-positive rate is not reported.

### Methodology

The evaluation used ten deterministic, project-generated cases with principal seed
`20260912`. It reused the merged A-03 controls and added single-encoded JPEGs at
different quality levels plus benign resize, blur, and noise processing.

Every case records its seed, source encoding, processing history, SHA-256 checksum,
ELA JPEG quality, highlight threshold, known-edit status, and expected interpretation.

The production `generate_ela` function was run with:

- JPEG comparison quality: `90`
- Highlight threshold: `20`
- Output: PNG heatmap
- Measurements: mean error, 95th-percentile error, maximum error, and highlighted
  pixel ratio

The controlled edited image contains a known rectangular edit at
`x=186..290, y=70..174`. Its heatmap intensity inside that region was compared with
the remaining image.

### Corpus design

| Case | Category | Processing | Known edit |
| --- | --- | --- | --- |
| `png-clean-cover` | PNG control | Lossless synthetic cover | No |
| `png-screenshot` | Screenshot control | Flat regions and sharp interface edges | No |
| `jpeg-original-95` | Single JPEG | One quality-95 encoding | No |
| `jpeg-recompressed-55` | Benign recompression | Quality 95 decoded and saved at quality 55 | No |
| `jpeg-edited-region-88` | Controlled edit | Mirrored region inserted and saved at quality 88 | Yes |
| `jpeg-single-75` | Single JPEG | One quality-75 encoding | No |
| `jpeg-single-50` | Single JPEG | One quality-50 encoding | No |
| `jpeg-resized` | Benign processing | Downscaled and upscaled using bicubic resampling | No |
| `jpeg-blurred` | Benign processing | Gaussian blur radius 1.5 | No |
| `jpeg-noise` | Benign processing | Deterministic Gaussian noise, standard deviation 8 | No |

### Results

| Case | Mean error | P95 error | Maximum error | Highlighted ratio |
| --- | ---: | ---: | ---: | ---: |
| `png-clean-cover` | 20.9751 | 99.0 | 208 | 0.244089 |
| `png-screenshot` | 5.4045 | 27.0 | 123 | 0.076445 |
| `jpeg-original-95` | 21.4560 | 99.0 | 204 | 0.259818 |
| `jpeg-recompressed-55` | 19.9399 | 94.0 | 215 | 0.279714 |
| `jpeg-edited-region-88` | 20.6068 | 98.0 | 205 | 0.269375 |
| `jpeg-single-75` | 21.1046 | 98.0 | 217 | 0.299310 |
| `jpeg-single-50` | 19.6458 | 93.0 | 213 | 0.274193 |
| `jpeg-resized` | 5.9345 | 19.0 | 62 | 0.045104 |
| `jpeg-blurred` | 3.6020 | 10.0 | 32 | 0.001823 |
| `jpeg-noise` | 24.5207 | 98.0 | 200 | 0.325443 |

All nine benign/control cases contained at least some pixels above the configured
highlight threshold.

Four benign cases met or exceeded the controlled edit's highlighted-pixel ratio:

- `jpeg-recompressed-55`
- `jpeg-single-75`
- `jpeg-single-50`
- `jpeg-noise`

Four benign cases met or exceeded the controlled edit's 95th-percentile error:

- `png-clean-cover`
- `jpeg-original-95`
- `jpeg-single-75`
- `jpeg-noise`

### Known-edit localisation

The controlled edited case produced:

| Measurement | Result |
| --- | ---: |
| Known-region mean heatmap intensity | 16.6191 |
| Background mean heatmap intensity | 26.5949 |
| Region-to-background ratio | 0.6249 |

The known edited region was dimmer than the image background in the generated
heatmap. In this controlled case, ELA did not reliably localise the edit.

This is a negative but important result. It must not be altered or omitted merely
because it does not demonstrate successful localisation.

### False-positive conditions

A formal binary false-positive rate is undefined because the production ELA
implementation does not classify images as manipulated or authentic.

However, the controlled measurements demonstrate clear false-positive conditions
for visual interpretation:

- Ordinary single JPEG encoding produced strong residuals.
- Lower JPEG quality produced highlighted ratios greater than the edited case.
- Benign recompression exceeded the edited case's highlighted ratio.
- Added noise produced the largest highlighted ratio in the corpus.
- PNG-to-JPEG comparison highlighted ordinary texture and edges.
- Screenshot edges produced visible ELA response without deceptive editing.

Consequently, a bright ELA region must not be described as proof of manipulation.

### Limitations

- The corpus contains synthetic controls rather than real forensic evidence.
- The ten cases do not estimate population-level accuracy.
- JPEG encoder and Pillow-version differences may slightly change measurements.
- ELA responds to compression, noise, resampling, filtering, edges, and image history.
- Uniform recompression may hide or reduce differences from a real edit.
- A manipulated image may produce a weak heatmap.
- An authentic or benignly processed image may produce a strong heatmap.
- ELA cannot identify who edited an image, why it was edited, or whether an edit is
  malicious.
- Results must be combined with metadata, provenance, content inspection, and other
  forensic signals.

### Reproduction

From the repository root with the Python 3.11 virtual environment active:

```powershell
python evaluation/ela/corpus.py
python evaluation/ela/evaluate.py
python -m pytest backend/tests/test_ela_evaluation.py -q
python -m pytest -q
python -m ruff check backend evaluation scripts
git diff --check
```

Generated images, heatmaps, manifests, and result JSON files are written beneath
`evaluation/ela/generated/` and excluded from Git.