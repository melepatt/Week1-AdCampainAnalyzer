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
- **Cause:** Button and dataframe calls used Streamlit's older responsive-width argument. Plotly uses a different signature in the pinned Streamlit 1.50 release.
- **Change:** Added a failing source-contract regression test, migrated buttons and dataframes to `width="stretch"`, and retained `use_container_width=True` only for Plotly calls where it remains the supported 1.50 parameter.
- **Verification:** All application tests pass and the regression test confirms all four Plotly calls use the pinned version's supported signature.

## 2026-10-10 — Browser automation could not attach an upload file

- **Symptom:** The live Upload CSV control rendered, but the QA browser extension refused to attach the local sample CSV.
- **Cause:** The installed Chrome extension does not have its optional “Allow access to file URLs” permission enabled.
- **Change:** No application change was appropriate. File-style ingestion remains covered through `BytesIO`, bundled-file loading, schema validation tests, and the visibly confirmed upload control.
- **Verification:** Loader and validation tests pass for valid and invalid in-memory CSV inputs. This limitation applies only to the QA browser extension's file chooser.

## 2026-10-10 — Final review found source-transition and validation edge cases

- **Symptom:** A CSV with dates or categories disjoint from the sample could inherit incompatible filter state. Extremely large integer counts could also overflow during `int64` conversion, missing columns could hide other detectable errors, and zero-denominator ratios appeared as blank table cells.
- **Cause:** Filter state had no source identity, count validation did not enforce the `int64` upper bound, validation returned immediately for missing columns, and table preparation only renamed headers.
- **Change:** Added content-derived upload identity and source-aware filter reconciliation; added exact decimal parsing and integer-range validation for counts; continued checking every present column when others are missing; and prepared ratio tables/downloads with explicit `N/A` values.
- **Verification:** Added RED–GREEN regressions covering source resets, intentional empty selections, exact decimal and scientific-notation overflow, aggregated error reporting, and `N/A` table values. All tests pass.

## 2026-10-10 — Plotly and layout controls require different width arguments

- **Observation:** Streamlit 1.50 uses `width="stretch"` for buttons and dataframes, but its pinned Plotly API still requires `use_container_width=True`; sending `width` to Plotly is treated as a deprecated arbitrary keyword.
- **Change:** Kept the current `width` argument for supported layout controls and restored the version-correct Plotly argument.
- **Verification:** A source-contract test asserts all four Plotly calls use the Streamlit 1.50 signature, and application tests pass.

## 2026-10-10 — Date range returned to the full sample period

- **Symptom:** Clicking a new start date caused the Date range control to jump back to January 1 through March 31 before an end date could be selected.
- **Cause:** Streamlit represents an in-progress range as a one-date tuple. Filter-state reconciliation treated any tuple other than a completed two-date range as invalid and restored the defaults.
- **Change:** Preserved valid one-date tuples for the current source and treated that intermediate value as a one-day range until the user selects the end date.
- **Verification:** Two RED–GREEN regressions confirm both pure filter-state reconciliation and the Streamlit AppTest interaction retain the newly selected first date. The full suite passes.

## Implementation iterations

- Split UI orchestration from data, validation, metric, filter, chart, formatting, and export modules.
- Chose deterministic sample generation so results and screenshots remain reproducible.
- Made empty categorical selections produce the documented empty state.
- Added duplicate normalized-header detection to prevent ambiguous uploaded columns.
- Recalculated ratios only after every platform, campaign, and time grouping.
- Added chart-contract tests for USD, count, percent, and multiplier units.
