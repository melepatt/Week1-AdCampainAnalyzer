# Bug and Iteration Log

## 2026-10-10 — Simplified attributed-value schema

- **Observation:** The early schema allowed `conversion_value` as a possible fallback for `revenue`.
- **Cause:** Advertising exports use inconsistent names for attributed value, but supporting both made the class contract harder to explain and validate.
- **Change:** Removed `conversion_value`; `revenue` is now required.
- **Verification:** Loader and validation tests require `revenue`, missing-column tests report it, and the README lists only the final 11-column schema.

## 2026-10-10 — Generated workflow files were staged

- **Symptom:** Temporary `.superpowers/brainstorm/` runtime files appeared in the Git staging area.
- **Cause:** Tool-generated state was created before a repository ignore rule existed.
- **Change:** Unstaged the generated files without deleting them and added `.superpowers/` and `.worktrees/` to the root `.gitignore`.
- **Verification:** Application commits contain no runtime-state files, and `git status` does not surface them.

## 2026-10-10 — Plan commit rejected trailing whitespace

- **Symptom:** `git diff --cached --check` reported trailing whitespace in Markdown command lines.
- **Cause:** Hard line-break spaces remained in the approved plan document.
- **Change:** Applied a mechanical trailing-whitespace cleanup before committing.
- **Verification:** The plan commit succeeded, and subsequent `git diff --check` runs were clean.

## 2026-10-10 — Streamlit could not bind inside the managed sandbox

- **Symptom:** The live smoke command failed with `PermissionError: [Errno 1] Operation not permitted` in Tornado's socket bind.
- **Cause:** A minimal Python `socket.bind` reproduced the same error, proving that the managed sandbox denies local TCP binds independently of the application.
- **Change:** Ran the unchanged Streamlit command outside the socket-restricted sandbox for the smoke check.
- **Verification:** Streamlit printed its local URL and `http://localhost:8501/_stcore/health` returned `ok`; the server then stopped cleanly.

## 2026-10-10 — Deprecated Streamlit width argument in live log

- **Symptom:** Live visual QA logged that `use_container_width` will be removed after December 31, 2025.
- **Cause:** The first UI implementation used Streamlit's older responsive-width argument.
- **Change:** Added a failing source-contract regression test, then replaced every occurrence with `width="stretch"`.
- **Verification:** All application tests passed and the regression test confirms the deprecated argument is absent.

## 2026-10-10 — Browser automation could not attach an upload file

- **Symptom:** The live Upload CSV control rendered, but the QA browser extension refused to attach the local sample CSV.
- **Cause:** The installed Chrome extension does not have its optional “Allow access to file URLs” permission enabled.
- **Change:** No application change was appropriate. File-style ingestion remains covered through `BytesIO`, bundled-file loading, schema validation tests, and the visibly confirmed upload control.
- **Verification:** Loader and validation tests pass for valid and invalid in-memory CSV inputs. This limitation applies only to the QA browser extension's file chooser.

## Implementation iterations

- Split UI orchestration from data, validation, metric, filter, chart, formatting, and export modules.
- Chose deterministic sample generation so results and screenshots remain reproducible.
- Made empty categorical selections produce the documented empty state.
- Added duplicate normalized-header detection to prevent ambiguous uploaded columns.
- Recalculated ratios only after every platform, campaign, and time grouping.
- Added chart-contract tests for USD, count, percent, and multiplier units.
