# Team Workboard

This is the single source of truth for active project work. Update this file before
starting a task and again when its state changes. `TEAM_STATUS.md` records broader
milestones; this file prevents two members from editing the same area at the same time.

Last remote audit: 12 September 2026 by Ayush. Palak's evaluation pipeline was reviewed
and merged through [PR #3](https://github.com/AyushPatra45/AI-DeepFake-Detector/pull/3).
Ayush's retention and resource-limit work was reviewed and merged through
[PR #4](https://github.com/AyushPatra45/AI-DeepFake-Detector/pull/4). No Ayana-authored
branch or commit had been found at the time of Ayush's audit. Palak's evaluator
integration tests were reviewed and merged through
[PR #5](https://github.com/AyushPatra45/AI-DeepFake-Detector/pull/5), and her deepfake
failure and batch-inference tests were reviewed and merged through
[PR #6](https://github.com/AyushPatra45/AI-DeepFake-Detector/pull/6).
Ayush's reproducible synthetic demonstration corpus and repository CI were reviewed
and merged through [PR #8](https://github.com/AyushPatra45/AI-DeepFake-Detector/pull/8).

## Status values

- `READY`: available for a member to claim.
- `CLAIMED`: owner and branch are recorded; implementation has not started.
- `IN_PROGRESS`: code, experiments, tests, or documentation are being produced.
- `BLOCKED`: progress needs a decision, dependency, dataset, or another hand-off.
- `PR_OPEN`: branch is pushed and a pull request is ready for review.
- `MERGED`: reviewed work is present on `main`.

## Active work

| ID | Task | Owner | Status | Branch | Owned files or area | Updated | PR / evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P-03 | Run the baseline on an approved fixed dataset subset | Palak | BLOCKED | Create after dataset approval | Generated private manifests/results and reviewed aggregate results in `docs/MODEL_EVALUATION.md` | 2026-09-11 | Needs an approved dataset subset; no accuracy is claimed |
| Y-01 | Build a controlled clean and LSB-embedded image corpus | Ayana | PR_OPEN | `ayana/stego-validation` | New `evaluation/steganography/`, fixtures, and `docs/FORENSICS_EVALUATION.md` | 2026-09-12 | [PR #9](https://github.com/AyushPatra45/AI-DeepFake-Detector/pull/9) open; 66 local tests and Ruff passed; awaiting CI and Ayush review |
| Y-02 | Evaluate ELA cases and document false positives | Ayana | READY | Suggested after Y-01: `ayana/ela-validation` | Evaluation assets/scripts and `docs/FORENSICS_EVALUATION.md`; coordinate before production ELA edits | 2026-09-05 | Not started |
| Y-03 | Run interface accessibility and usability checks | Ayana | READY | Suggested: `ayana/usability-study` | `frontend/`, new usability notes; coordinate before changing shared API schemas | 2026-09-05 | Not started |

Only one large task per person may be `CLAIMED` or `IN_PROGRESS` at a time.

## Completed and merged work

| Work | Assigned domain | Implemented / committed by | State | Evidence |
| --- | --- | --- | --- | --- |
| Project roadmap and team plan | Shared | Ayush | MERGED | Commit `c85722c` |
| Platform backend foundation | Ayush | Ayush | MERGED | PR #1, commit `49b0b5f` |
| Shared workboard and collision rules | Shared | Ayush | MERGED | Commits `81aa4d0` and `0f34555` |
| Reproducible deepfake baseline evaluation pipeline | Palak | Palak | MERGED | PR #3; commit `9c285c5` and follow-up commits; 30 tests and Ruff passed |
| Evaluator runner and failure-path tests | Palak | Palak, with Ayush review fix | MERGED | PR #5; Palak commit `e65ffbf`; review fix `6357a19`; 55 tests and Ruff passed |
| Deepfake failure and batch-inference tests | Palak | Palak | MERGED | PR #6; commit `61ca8a9`; 11 deepfake, 45 backend and 60 total tests passed; Ruff passed |
| Retention cleanup and configurable analysis limits | Ayush | Ayush | MERGED | PR #4; commit `218db76`; 45 tests, Ruff and diff checks passed |
| Reproducible synthetic demonstration corpus and repository CI | Ayush | Ayush | MERGED | PR #8; merge commit `7bb1c93`; 63 tests, Ruff and GitHub Actions passed |
| ELA, LSB and metadata integration | Ayana domain | Ayush with Codex assistance | MERGED | PR #2, commit `d027194`; Ayana must still review and validate it |
| Dual-stream detector integration | Palak domain | Ayush with Codex assistance | MERGED | PR #2, commit `04119ab`; Palak must still review and validate it |
| Browser forensic workspace | Ayana domain | Ayush with Codex assistance | MERGED | PR #2, commit `49cba6d`; Ayana must still review and validate it |
| Integrated status and follow-up documentation | Shared | Ayush | MERGED | PR #2, commit `eaa5d71` |

Assignment is not authorship. The `Implemented / committed by` column must match the
actual work and Git history.

## Collision-prevention procedure

1. Run `git switch main`, `git pull --ff-only origin main`, and `git fetch --prune`.
2. Read this file and choose one `READY` task assigned to you.
3. Confirm that nobody owns the same files or area in an active row.
4. Change the row to `CLAIMED` and add your intended implementation branch and files.
   Land this coordination-only edit on `main` through the GitHub editor or a tiny claim
   pull request before writing implementation code.
5. Pull the claimed row from `main`, then create the implementation branch recorded in
   the row. Never implement directly on `main`.
6. Change the row to `IN_PROGRESS` in the implementation branch when work begins.
7. Before editing a shared file such as `README.md`, `pyproject.toml`, API schemas, or
   report formats, record it in the row and notify the other owners.
8. Commit in small units and push at least at the end of each work session.
9. When opening a pull request, change the status to `PR_OPEN` and add its link.
10. After merge, move the factual result to the completed table and select the next
    `READY` task.

Do not overwrite another member's branch, force-push shared work, or mark work
`MERGED` before it is present on `origin/main`.

## Daily update format

Add a short entry only when useful; keep the newest entry first.

| Date | Member | Task | Done | Next | Blocker |
| --- | --- | --- | --- | --- | --- |
| 2026-09-12 | Ayush | A-03 | Merged [PR #8](https://github.com/AyushPatra45/AI-DeepFake-Detector/pull/8) with a deterministic six-image ELA/LSB demonstration corpus, manifest checksums, regression tests, documentation and repository CI; 63 local tests, Ruff and GitHub Actions passed | Review Ayana's Y-01 PR and integrate approved P-03 results when available | P-03 still requires formal FaceForensics++ access approval |
| 2026-09-12 | Ayush | A-03 | Claimed the synthetic demonstration corpus and CI task on `codex/ayush-demo-ci` | Implement deterministic media generation, automated forensic checks, documentation, and CI | None |
| 2026-09-12 | Ayush | P-02 review | Reviewed and merged [PR #6](https://github.com/AyushPatra45/AI-DeepFake-Detector/pull/6); verified checkpoint failure, empty input, batching, unreadable image and video frame-association coverage; 60 tests and Ruff passed | Keep P-03 blocked until an approved fixed dataset subset is supplied | Approved dataset subset not supplied |
| 2026-09-12 | Palak | P-02 | Added five deterministic deepfake failure and batch-inference tests and opened [PR #6](https://github.com/AyushPatra45/AI-DeepFake-Detector/pull/6); 11 deepfake, 45 backend and 60 total tests passed; Ruff passed; no production code or data artifacts changed | Ayush reviews and merges P-02; keep P-03 blocked until an approved fixed dataset subset is supplied | P-03 still needs an approved dataset subset; no accuracy is claimed |
| 2026-09-12 | Ayush | P-04 review | Reviewed and merged [PR #5](https://github.com/AyushPatra45/AI-DeepFake-Detector/pull/5); retained A-02 updates and fixed cross-platform absolute-path validation after a new test exposed the issue; 55 tests and Ruff passed | Palak may claim P-02 after updating from `main` | P-03 still needs an approved dataset subset |
| 2026-09-11 | Palak | P-04 | Added 10 evaluator runner and failure-path tests; opened [PR #5](https://github.com/AyushPatra45/AI-DeepFake-Detector/pull/5); 40 total tests and Ruff passed | Ayush reviews and merges P-04 before Palak claims P-02 | P-03 still needs an approved dataset subset |
| 2026-09-11 | Ayush | A-02 | Merged [PR #4](https://github.com/AyushPatra45/AI-DeepFake-Detector/pull/4) with startup/periodic retention cleanup, path-safe deletion, decoded-media limits and operations documentation; 45 tests and Ruff passed | Integrate validated team evaluation outputs when available | Palak's approved dataset run and Ayana's validation results are still pending |
| 2026-09-11 | Ayush | P-01 review | Reviewed and merged PR #3 after 30 tests, Ruff and an independent evaluator smoke test passed | Add direct evaluator failure-path coverage; run real metrics after dataset approval | Approved dataset subset not supplied |
| 2026-09-11 | Palak | P-01 | Pushed the evaluation branch and opened [PR #3](https://github.com/AyushPatra45/AI-DeepFake-Detector/pull/3); 30 tests and Ruff passed | Ayush reviews P-01; run the documented baseline after an approved dataset subset is supplied | Approved dataset subset not supplied; no accuracy is claimed |
| 2026-09-11 | Ayush | A-01 | Merged the workboard into `origin/main` | Palak and Ayana can claim their first validation tasks | None |
| 2026-09-05 | Ayush | A-01 | Audited remote branches and created coordination rules | Open and merge the workboard pull request | None |

## Handoff checklist

- Branch is pushed and visible on GitHub.
- Pull request explains the task ID, changed files, approach, and limitations.
- Tests or experiment commands and their actual results are recorded.
- Generated datasets, uploads, checkpoints, secrets, and large artifacts are not in Git.
- Documentation states what is complete and what remains unvalidated.
- Another teammate can run, review, and explain the work.
