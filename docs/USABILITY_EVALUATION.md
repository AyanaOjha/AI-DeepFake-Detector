# Interface Accessibility and Usability Evaluation

## Status

Y-03 is in progress. This document separates the initial accessibility audit from
the five-person usability study. No participant results are recorded until the
study is actually conducted.

## Scope

The evaluation covers:

- Media upload and progress
- Result interpretation
- Visual evidence and video timeline
- Case history and report download
- Keyboard operation
- Responsive presentation
- Accessible names, states and announcements

Only project-generated synthetic media is used. No participant names, private media
or other personal information is collected.

## Baseline accessibility audit

Audit date: 2026-09-19

Environment:

- Local application at `http://127.0.0.1:8000/`
- Chromium-based browser
- Keyboard-only checks
- Source review of `frontend/index.html`, `frontend/app.js` and
  `frontend/styles.css`

| Check | Result | Evidence |
| --- | --- | --- |
| Main navigation is keyboard operable | Pass | Both application views can be opened without a mouse |
| File chooser is keyboard operable | Pass | Enter opens the native file picker |
| Result tabs support arrow-key navigation | Fail | Right Arrow on Overview does not select Visual evidence |
| New results receive keyboard focus | Fail | Results scroll into view but the result heading is not focused |
| Upload area has visible keyboard focus | Fail | The transparent file input has no corresponding focus style |
| Collapsed navigation retains accessible names | Fail | Responsive CSS hides the only non-`aria-hidden` button text |
| Status meaning is conveyed only by colour | Pass | Risk and module states also contain visible text |
| Evidence images have alternative text | Pass | Artifact descriptions populate image alternative text |

The unusual characters displayed by some PowerShell output are not counted as a
browser defect because the browser renders the symbols correctly.

## Planned corrections

- Add accessible state information to application navigation.
- Add complete tab and tab-panel relationships.
- Implement Left Arrow, Right Arrow, Home and End behavior for tabs.
- Add visible focus treatment to the upload area and interactive controls.
- Move focus to the result heading when analysis finishes.
- Preserve navigation accessible names in collapsed layouts.
- Announce engine status changes.

## Five-person usability study

Participants will be identified only as P1 through P5.

Each participant will be asked to:

1. Upload the supplied synthetic image and start analysis.
2. Explain the result or why a probability is unavailable.
3. Open Visual evidence and describe what it does and does not prove.
4. Open Case history and return to the analysed case.
5. Download a JSON or PDF report.

### Post-task questionnaire

After completing the five tasks, ask each participant:

1. Rate the ease of uploading and starting analysis from 1 (very difficult) to
   5 (very easy).
2. Rate the clarity of the result summary from 1 (very unclear) to 5 (very clear).
3. Rate the clarity of the visual-evidence limitations from 1 to 5.
4. What was the most confusing part?
5. What single change would most improve the interface?

Record only the answers and participant identifier. Do not record names or other
personal information.

| Participant | Upload | Interpret result | Visual evidence | History | Report | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Pending | Pending | Pending | Pending | Pending | |
| P2 | Pending | Pending | Pending | Pending | Pending | |
| P3 | Pending | Pending | Pending | Pending | Pending | |
| P4 | Pending | Pending | Pending | Pending | Pending | |
| P5 | Pending | Pending | Pending | Pending | Pending | |

## Limitations

The audit is not an accessibility conformance certification. The five-person study
is a small formative study and must not be presented as population-level evidence.