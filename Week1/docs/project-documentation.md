# Ad Campaign Performance Analyzer — Project Documentation

## Project overview

This project helps a marketer or marketing student determine which campaigns and advertising channels are delivering results. The Streamlit application compares Facebook, Instagram, Pinterest, and Twitter using spend, impressions, clicks, conversions, revenue, ROI, ROAS, and supporting efficiency metrics.

The dashboard is designed for exploratory analysis rather than campaign editing or prediction. One shared filter state updates every view so comparisons always refer to the same subset of records.

## Dataset

The bundled `data/sample_campaigns.csv` contains 1,080 deterministic daily records: 12 campaigns across 90 days from January 1 through March 31, 2026. Each platform has three campaigns. The data includes multiple audiences and the Awareness, Traffic, Leads, and Sales goals.

The row grain is one campaign, platform, audience, goal, and day. Required fields are `date`, `campaign_id`, `campaign_name`, `platform`, `audience`, `campaign_goal`, `spend`, `impressions`, `clicks`, `conversions`, and `revenue`. `revenue` is the only attributed-value field; `conversion_value` was removed from the design to make the class data contract easier to understand.

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

AI was used to turn the assignment into a detailed specification, recommend the CSV schema, develop and save GUI mockups, write an implementation plan, and execute the plan using test-driven development. Each feature began with a failing contract test, followed by the smallest implementation needed to pass it. Task-specific commits and an execution ledger preserved traceability.

Major prompts are recorded in `prompt-log.md`. The detailed implementation plan is retained under `docs/superpowers/plans/`.

## Iterations and design decisions

1. The initial schema considered accepting `conversion_value` as a fallback. It was removed after review so the app requires the clearer `revenue` field.
2. The GUI was designed as a single wide page with a persistent filter sidebar and four tabs, then translated into Streamlit-native controls for accessibility.
3. Business calculations were separated from `app.py` so the formulas and edge cases could be tested without a browser.
4. Empty categorical selections were defined as “show no records,” preventing an ambiguous implicit select-all behavior.
5. Weekly aggregation was explicitly set to Monday-start periods so Sunday is not lost at month boundaries.

## Bugs and resolutions

Only observed issues are listed in `bug-and-iteration-log.md`. During release work, Markdown trailing whitespace blocked a commit check and was normalized. A local Streamlit server initially could not bind a port inside the managed sandbox; a minimal socket reproduction identified the restriction, and the unchanged app passed its health check outside that socket sandbox. Neither issue required a business-logic workaround.

## Testing and validation evidence

- 73 automated tests cover sample generation, CSV loading, duplicate normalized headers, type coercion, validation errors and warnings, integer overflow, finite values, aggregate formulas, zero denominators, formatting, data-source filter resets, shared filters, campaign/platform/time aggregation, weekly boundaries, chart labels and units, deterministic exports, four-tab rendering, the shared empty state, and the pinned Streamlit width APIs.
- The full suite passed on Python 3.12 with pytest 8.3.5.
- `python -m compileall app.py src scripts tests` completed successfully.
- `git diff --check` reported no whitespace errors.
- Streamlit started in headless mode and `/_stcore/health` returned `ok`.
- The default sample-data UI, four tabs, filter groups, key KPI labels, and empty-filter state were exercised through Streamlit AppTest and live visual QA. The upload mode and file input were visibly verified; browser automation could not attach a file because the installed Chrome extension does not have local-file URL access, so valid and invalid uploaded-file processing was verified at the loader and validation layers with in-memory file objects.

## Learnings and observations

- Marketing ratios must be recomputed from totals; averaging row-level rates gives misleading results.
- A clear data contract saves more time than silently guessing what an uploaded column means.
- Treating warnings differently from blocking errors lets analysts continue while still seeing data-quality concerns.
- Unit labels belong in metric cards, table headers, axes, legends, and hover text—not only in documentation.
- Deterministic sample data makes screenshots, demonstrations, and tests reproducible.

## Submission links

- GitHub repository: **Not published yet**
- Deployed application: **Not published yet**
- Saved mockups: `docs/mockups/`
- Video walkthrough: **Not recorded yet**
