# Team Implementation Status

Status date: 18 September 2026

## Authorship note

The Palak-owned and Ayana-owned modules below were implemented in the shared project
branch with Codex assistance because their work had not started. They are marked
"implemented for review," not falsely attributed as code personally written by those
members. Palak and Ayana must review, run, explain, and validate their modules before
claiming them as completed individual contributions.

## Current status

| Area | Assigned owner | Implementation state | Validation state |
| --- | --- | --- | --- |
| API, upload security, hashing, jobs and reports | Ayush | Complete and merged | Automated and live tested |
| Video sampling and timestamp tracking | Ayush | Complete and merged | Automated tested |
| Dual-stream deepfake architecture | Palak | Implemented for review | Forward pass and checkpoint compatibility verified |
| Calibrated checkpoint inference | Palak | Implemented for review | Real CPU inference smoke test passed |
| SRM, FFT and Grad-CAM artifacts | Palak | Implemented for review | All generated and loaded in browser |
| ELA analysis | Ayana | Implemented for review | Automated tests passed; controlled Y-02 evaluation documented limitations |
| LSB indicators and supported extraction | Ayana | Complete and merged | Ayana's 16-case deterministic Y-01 evaluation and GitHub CI passed |
| Image/video metadata | Ayana | Implemented for review | Basic image and integrated API tests passed |
| Browser results workspace | Ayana | Implemented for review | Desktop/mobile and end-to-end browser tested |
| Retention cleanup and configurable media limits | Ayush | Complete and merged | Startup/periodic cleanup and limit tests passed |
| Evaluator runner and failure handling | Palak | Complete and merged | Batching, outputs, invalid input, read-error and no-face tests passed |
| Deepfake runtime edge and batch paths | Palak | Complete and merged | Empty input, malformed checkpoint, unreadable image, batching and frame association tested |
| Synthetic ELA/LSB demonstration corpus and repository CI | Ayush | Complete and merged | Reproducibility, checksums, extraction controls, heatmaps and GitHub Actions verified |
| Cross-dataset scientific evaluation | Palak | Not started | Required before final review |
| Deterministic stego validation | Ayana | Complete and merged | Five supported extractions, six clean controls and five unsupported layouts evaluated |
| Controlled ELA validation | Ayana | Complete and merged | Ten cases reproduced; benign highlight conditions and failed edit localisation documented |
| Interface accessibility and user study | Ayana | Not started | Required before final review |

## Palak: required next work

1. Read and explain `backend/app/deepfake/` and the reference architecture.
2. Reproduce baseline metrics on an approved, identity-disjoint dataset subset.
3. Evaluate at least one manipulation family or dataset excluded from training.
4. Measure JPEG, resize, blur, and noise robustness using fixed test manifests.
5. Compare mean, top-k, and softmax-weighted video aggregation.
6. Write the model methodology, metrics table, confusion matrix, and limitations.
7. Add multiple-face and truncated-checkpoint cases if dataset runs expose gaps.

Palak's module is not scientifically complete until these results are reproducible.
Loading a published checkpoint is implementation evidence, not a new accuracy claim.

## Ayana: progress and required next work

Completed in PR #9: a deterministic clean/LSB corpus with recorded payload size,
channel order, bit plane, embedding method and checksums; supported extraction and
unsupported keyed/channel layouts were measured and documented with explicit limits.

1. Pull merged `main`, read and explain `backend/app/forensics/` and `frontend/`.
2. Y-02 is complete: ten controlled ELA cases and false-positive conditions are
   documented in `docs/FORENSICS_EVALUATION.md`.
3. Claim Y-03 after pulling updated `main`.
4. Run a five-person usability test covering upload, result interpretation, visual
   evidence, history, and report download.
5. Improve accessibility and wording from the observed user errors.

## Ayush: integration status

Completed: the combined engines/UI integration, deployment-oriented retention,
cleanup, configurable media limits, reproducible demonstration corpus, and repository
CI are merged.

1. Add a background worker only if concurrent long-video jobs become a requirement.
2. Integrate Palak's evaluation outputs and Ayana's user-study results when supplied.

## Verified evidence

- Published checkpoint SHA-256:
  `c5c2002b5ef6c7ee0c542d7d203e16386dc641b685859d8a58ac883b52c8e4c9`.
- Checkpoint calibration loaded: threshold `0.01`, temperature `1.4788347482681274`.
- Automated suite: 66 tests passing after PR #9 steganography evaluation integration.
- Y-01 controlled evaluation: 5/5 supported payloads extracted exactly, 0/6 supported-
  payload false positives on clean controls, and 0/5 unsupported layouts falsely
  reported as supported; these figures are not real-world generalisation claims.
- Y-02 controlled evaluation: ten cases, including nine benign controls; the known
  edited region was dimmer than the background in its heatmap. No binary ELA
  false-positive rate is claimed because ELA does not issue a binary decision.
- Browser workflow: upload, processing, completed result, case history, five visual
  artifacts, and report links verified without console errors.
- Responsive check: no horizontal document overflow at a 390-pixel viewport.

## Review wording

Use this accurate statement:

> The integrated functional prototype is implemented. The platform, deepfake inference,
> ELA, LSB analysis, metadata, visual evidence, video sampling, history, and reports are
> operational. Dataset-scale generalisation experiments and extended user validation
> are the next phase; therefore, we report model risk indicators rather than claiming
> universal or conclusive detection.
