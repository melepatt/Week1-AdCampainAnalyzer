# Ad Campaign Performance Analyzer — Project Documentation

## Project overview

This project helps a marketer or marketing analyst determine which campaigns and advertising channels are delivering results. The Streamlit application compares Facebook, Instagram, Pinterest, and Twitter using spend, impressions, clicks, conversions, revenue, ROI, ROAS, and supporting efficiency metrics.

The dashboard is designed for exploratory analysis rather than campaign editing or prediction. One shared filter state updates every view so comparisons always refer to the same subset of records.

## Dataset

The bundled `data/sample_campaigns.csv` contains 1,080 deterministic daily records: 12 campaigns across 90 days from January 1 through March 31, 2026. Each platform has three campaigns. The data includes multiple audiences and the Awareness, Traffic, Leads, and Sales goals.

An additional upload-ready test file, `data/test_campaigns_april_september.csv`, contains 1,464 deterministic daily records from April 1 through September 30, 2026. It includes eight campaigns, two per supported platform, eight audiences, and the same four campaign goals. This second dataset was added to test longer date ranges, source transitions, filters, tables, charts, and CSV uploads without changing the bundled default data.

The row grain is one campaign, platform, audience, goal, and day. Required fields are `date`, `campaign_id`, `campaign_name`, `platform`, `audience`, `campaign_goal`, `spend`, `impressions`, `clicks`, `conversions`, and `revenue`. `revenue` is the only attributed-value field; `conversion_value` was removed from the design to make the data contract easier to understand.

Users can replace the sample data for the current session by uploading a CSV. Uploads remain in memory and are not saved.

## Architecture and technology

- Streamlit composes the page, sidebar controls, four tabs, validation messages, and downloads.
- pandas loads, validates, filters, groups, and exports data.
- Plotly creates interactive, unit-labeled charts.
- pytest and Streamlit AppTest verify business rules and the main UI contract.
- Focused modules under `src/` keep business logic independent of the UI.

The processing path is: load CSV → normalize headers → validate and coerce → apply one shared filter selection → aggregate totals → recalculate ratios → render all views.

## Application views

### Overview

Shows total spend in USD, revenue in USD, conversion count, ROI percent, CPA, and ROAS. A weekly combination chart compares spend and conversions, and a horizontal chart compares platform ROI.

### Platform Comparison

Provides a selectable single-unit chart for Spend, Revenue, Clicks, Conversions, CPA, ROAS, or ROI. A summary table and CSV download expose the same aggregated data.

### Campaign Details

Aggregates each campaign and retains stable comma-separated labels when a campaign spans several audiences, goals, platforms, or names. Search is case-insensitive across campaign ID and name. The searched table can be downloaded as CSV.

### Time Series

Explores Spend, Revenue, Clicks, Conversions, CTR, CPA, ROAS, or ROI by day, Monday-start week, or calendar month. An optional channel breakdown creates one labeled trace per platform.

## Global filters and states

The sidebar filters the inclusive date range, channel, audience, and campaign goal. Multiple selections inside a filter use OR logic; categories combine with AND logic. Reset restores the complete source dataset. Selecting no value intentionally returns no rows and displays: “No campaign records match the selected filters. Broaden or reset the filters to continue.”

CSV validation reports all blocking schema and value errors together. Duplicate grains and unusual metric relationships remain usable but generate warnings. Ratios with a zero denominator return `None` and display as `N/A`; non-finite numeric inputs are rejected.

## AI-assisted workflow

AI was used to turn the initial product requirements into a detailed specification, recommend the CSV schema, develop and save GUI mockups, write an implementation plan, and execute the plan using test-driven development. Each feature began with a failing contract test, followed by the smallest implementation needed to pass it. Task-specific commits and an execution ledger preserved traceability.

After the initial build, AI also helped investigate the date-range reset, strengthen validation and filter-state handling, generate and validate the six-month test dataset, merge the feature work locally, rename the project directory, diagnose a stale Streamlit process after the rename, and publish the repository to GitHub.

Major prompts are recorded in `prompt-log.md`. The detailed implementation plan is retained under `docs/superpowers/plans/`.

## Iterations and design decisions

1. The initial schema considered accepting `conversion_value` as a fallback. It was removed after review so the app requires the clearer `revenue` field.
2. The GUI was designed as a single wide page with a persistent filter sidebar and four tabs, then translated into Streamlit-native controls for accessibility.
3. Business calculations were separated from `app.py` so the formulas and edge cases could be tested without a browser.
4. Empty categorical selections were defined as “show no records,” preventing an ambiguous implicit select-all behavior.
5. Weekly aggregation was explicitly set to Monday-start periods so Sunday is not lost at month boundaries.
6. Filter state was tied to a content-derived source identity so uploading a different CSV resets incompatible dates and categories while preserving deliberate empty selections.
7. Count validation was changed to exact decimal parsing before `int64` conversion so scientific notation and values above the supported integer boundary are handled without floating-point precision loss.
8. Streamlit's one-date intermediate value is preserved while a user selects a date range, preventing the start date from jumping back to the source minimum.
9. A separate six-month CSV was generated instead of replacing the bundled sample, keeping demonstrations reproducible while providing a broader upload test.
10. The completed feature branch was fast-forwarded into local `main`, the isolated worktree was removed, and the project directory was renamed to `Week1-AdCampainAnalyzer`.
11. The GitHub repository was created as a public repository and the complete local history was pushed to its `main` branch.

## Bugs and resolutions

Only observed issues are listed in `bug-and-iteration-log.md`. During release work, Markdown trailing whitespace blocked a commit check and was normalized. A local Streamlit server initially could not bind a port inside the managed sandbox; a minimal socket reproduction identified the restriction, and the unchanged app passed its health check outside that socket sandbox.

Final review also found and resolved source-transition, integer-boundary, missing-column aggregation, ratio-display, and Streamlit width-API issues. The date-range control required a targeted fix because an in-progress selection contains only one date. After the directory rename, the already-running Streamlit process still referenced the removed worktree; an upload-triggered rerun therefore produced `[Errno 2] No such file or directory`. Restarting Streamlit from `Week1-AdCampainAnalyzer` resolved the environmental error without an application-code change.

## Testing and validation evidence

- 76 automated tests cover sample generation, CSV loading, duplicate normalized headers, type coercion, validation errors and warnings, exact integer-boundary handling, finite values, aggregate formulas, zero denominators, formatting, data-source filter resets, in-progress date-range selection, shared filters, campaign/platform/time aggregation, weekly boundaries, chart labels and units, deterministic exports, four-tab rendering, the shared empty state, and the pinned Streamlit width APIs.
- The full suite passed on Python 3.12 with pytest 8.3.5.
- `python -m compileall app.py src scripts tests` completed successfully.
- `git diff --check` reported no whitespace errors.
- Streamlit started in headless mode and `/_stcore/health` returned `ok`.
- The default sample-data UI, four tabs, filter groups, key KPI labels, and empty-filter state were exercised through Streamlit AppTest and live visual QA. The upload mode and file input were visibly verified; browser automation could not attach a file because the installed Chrome extension does not have local-file URL access, so valid and invalid uploaded-file processing was verified at the loader and validation layers with in-memory file objects.
- The six-month CSV was loaded through the same application loader and validator: all 1,464 rows were accepted, the date range was April 1 through September 30, 2026, all four platforms had 366 rows, and validation returned no errors or warnings.
- After the directory rename, Streamlit was restarted from the new location, its `/_stcore/health` endpoint returned `ok`, and live visual QA confirmed the dashboard rendered normally.
- After publication, local `main` and GitHub `origin/main` were verified at the same commit.

## Learnings and observations

- Marketing ratios must be recomputed from totals; averaging row-level rates gives misleading results.
- A clear data contract saves more time than silently guessing what an uploaded column means.
- Treating warnings differently from blocking errors lets analysts continue while still seeing data-quality concerns.
- Unit labels belong in metric cards, table headers, axes, legends, and hover text—not only in documentation.
- Deterministic sample data makes screenshots, demonstrations, and tests reproducible.
- Long-running development servers should be restarted after a project directory or worktree is renamed because their working directory and script path do not update automatically.
- A second deterministic dataset is useful for validating uploads and longer reporting periods without making the default product demonstration harder to reproduce.

## Project links

- GitHub repository: <https://github.com/melepatt/Week1-AdCampainAnalyzer>
- Project directory on GitHub: <https://github.com/melepatt/Week1-AdCampainAnalyzer/tree/main/Week1-AdCampainAnalyzer>
- AI prompt log: [docs/prompt-log.md](prompt-log.md)
- Saved mockups: `docs/mockups/`
