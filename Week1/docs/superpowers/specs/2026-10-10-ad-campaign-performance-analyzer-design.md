# Ad Campaign Performance Analyzer Design Specification

Date: October 10, 2026  
Status: Implemented and verified
Primary audience: Marketing students and non-technical marketers

## 1. Purpose

Build a class-ready analytics dashboard that helps a marketer identify which advertising campaigns and platforms are delivering results. The application will compare spend, traffic, conversions, revenue, and return across Facebook, Instagram, Pinterest, and Twitter.

The finished submission must include:

1. A working Streamlit dashboard that supports bundled sample data and uploaded CSV files.
2. A GitHub-ready codebase with setup and usage instructions.
3. Project documentation covering the overview, dataset, AI prompts, iterations, bugs, and lessons learned.
4. A script for a walkthrough video lasting no more than five minutes.

## 2. Success Criteria

The project succeeds when:

- A user can open the app and immediately explore a valid sample dataset.
- A user can upload a conforming campaign CSV and receive either a working dashboard or actionable validation errors.
- One set of date, platform, audience, and campaign-goal filters updates all four views consistently.
- Metrics display explicit units and use mathematically correct aggregate formulas.
- Empty filter results produce a clear message rather than misleading zeros or blank charts.
- Automated tests cover data validation, filtering, metric calculations, and important edge cases.
- The repository includes the assets required for the class documentation and video demonstration.

## 3. Scope

### In scope

- Local or hosted single-user Streamlit application
- CSV ingestion and validation
- Bundled sample dataset
- Four synchronized analytical views
- Static descriptive analytics
- Download of the filtered campaign-level table as CSV
- Unit and integration-oriented tests for business logic
- Documentation and demo-support materials

### Out of scope

- User accounts or authentication
- Database storage
- Live advertising-platform APIs
- Campaign editing or ad buying
- Predictive modeling, attribution modeling, or optimization recommendations
- Currency conversion or mixed-currency files
- Multi-user collaboration

## 4. Recommended Technology

- Python 3.11 or later
- Streamlit for the application UI
- pandas for loading, normalization, filtering, aggregation, and export
- Plotly Express or Plotly Graph Objects for interactive charts
- pytest for automated tests
- Streamlit Community Cloud or Replit for deployment

All monetary values are assumed to be US dollars. The app will label monetary values with `$` or `USD`.

## 5. Application Architecture

The application will use a single Streamlit page with four tabs and a persistent sidebar. Business logic will remain outside `app.py` so it can be tested without launching Streamlit.

```text
Bundled sample CSV or uploaded CSV
              ↓
         Load CSV data
              ↓
 Normalize names and primitive types
              ↓
 Validate schema and business rules
              ↓
 Apply one shared global filter state
              ↓
 Compute totals, ratios, and view aggregates
              ↓
 Overview │ Platform Comparison │ Campaign Details │ Time Series
```

Recommended project structure:

```text
Week1/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── sample_campaigns.csv
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── validation.py
│   ├── metrics.py
│   ├── filters.py
│   ├── charts.py
│   └── formatting.py
├── tests/
│   ├── conftest.py
│   ├── test_data_loader.py
│   ├── test_validation.py
│   ├── test_metrics.py
│   └── test_filters.py
└── docs/
    ├── project-documentation.md
    ├── prompt-log.md
    ├── bug-and-iteration-log.md
    ├── video-demo-script.md
    ├── mockups/
    └── superpowers/specs/
```

## 6. Data Contract

### Row grain

Each row represents one campaign's performance on one platform, for one audience and campaign goal, on one calendar day.

### Required columns

| Column | Type | Meaning |
|---|---|---|
| `date` | Date | Reporting date in `YYYY-MM-DD` format |
| `campaign_id` | Text | Stable campaign identifier |
| `campaign_name` | Text | Human-readable campaign name |
| `platform` | Category | Facebook, Instagram, Pinterest, or Twitter |
| `audience` | Text | Audience or targeting segment |
| `campaign_goal` | Text | Objective such as Awareness, Traffic, Leads, or Sales |
| `spend` | Decimal | Advertising spend in USD |
| `impressions` | Integer | Number of delivered impressions |
| `clicks` | Integer | Number of clicks |
| `conversions` | Integer | Number of attributed conversions |
| `revenue` | Decimal | Attributed revenue in USD |

Canonical header order:

```csv
date,campaign_id,campaign_name,platform,audience,campaign_goal,spend,impressions,clicks,conversions,revenue
```

### Normalization

- Trim leading and trailing whitespace from headers and text fields.
- Convert headers to lowercase snake case.
- Parse `date` to pandas datetime.
- Convert numeric columns with strict failure reporting.
- Normalize platform capitalization to the four canonical labels.
- Preserve campaign names, audience labels, and campaign-goal labels after trimming.
- Keep campaign IDs as strings, including leading zeroes.

### Blocking validation errors

The app must reject a dataset when it contains:

- One or more missing required columns
- An empty dataset
- Unparseable or blank dates
- Blank campaign IDs or campaign names
- Unsupported platforms
- Non-numeric values in required metric columns
- Negative spend, impressions, clicks, conversions, or revenue
- Fractional impressions, clicks, or conversions

Each validation message must identify the affected column and, when practical, the number or indices of invalid rows.

### Non-blocking warnings

The app may continue after showing warnings for:

- Duplicate records at the declared row grain
- Clicks greater than impressions
- Conversions greater than clicks
- Zero spend paired with positive revenue
- Campaign IDs mapped to multiple campaign names

Duplicate-grain records remain separate because silently combining them could conceal an export problem. Normal aggregation will still include every retained row.

## 7. Data Sources

The header provides two mutually exclusive choices:

1. **Sample data:** load `data/sample_campaigns.csv`.
2. **Upload CSV:** accept one `.csv` file and replace the sample dataset for the current session.

The sample dataset will contain 90 days of daily data for 12 campaigns, with three campaigns represented on each of the four platforms. It will include multiple audiences and all four representative goals: Awareness, Traffic, Leads, and Sales. Values will be deterministic so tests and screenshots remain reproducible.

Uploaded data is processed in memory and is not persisted.

## 8. Metric Definitions

Metrics are calculated from filtered aggregate totals. Row-level rates and ratios must never be averaged.

| Metric | Formula | Unit |
|---|---|---|
| Spend | `sum(spend)` | USD |
| Revenue | `sum(revenue)` | USD |
| Impressions | `sum(impressions)` | Count |
| Clicks | `sum(clicks)` | Count |
| Conversions | `sum(conversions)` | Count |
| CTR | `clicks / impressions * 100` | Percent |
| CPC | `spend / clicks` | USD per click |
| Conversion rate | `conversions / clicks * 100` | Percent |
| CPA | `spend / conversions` | USD per conversion |
| ROAS | `revenue / spend` | Multiplier |
| ROI | `(revenue - spend) / spend * 100` | Percent |

When a denominator is zero, the result is `None` and the interface displays `N/A`. Infinite values must never appear.

## 9. Global Filters

The sidebar contains:

- Inclusive start and end dates
- Platform multiselect
- Audience multiselect
- Campaign-goal multiselect
- Reset-filters button
- Active-filter summary

Initial state selects the full date range and every available categorical value.

Filter logic:

- Conditions between filter categories use AND logic.
- Multiple values inside one categorical filter use OR logic.
- Filter options are derived from the validated source dataset.
- The app computes one filtered DataFrame and passes it to all views.
- Reset restores the full source dataset.

If no rows match, the app displays:

> No campaign records match the selected filters. Broaden or reset the filters to continue.

In this state, the app does not display zero-valued KPI cards, empty charts, or an empty detail table.

## 10. View Specifications

### 10.1 Overview

Purpose: provide a fast answer to "How are the selected campaigns performing overall?"

Components:

- KPI cards for total spend, revenue, conversions, and ROI
- Supporting values for CPA and ROAS
- Weekly spend-versus-conversions combination chart
- ROI-by-platform horizontal bar chart
- Source and row-count indicator

Chart requirements:

- Spend uses USD labels.
- Conversions use count labels.
- The dual-measure trend uses clearly separated axes and legend labels.
- Hover information includes date period, spend, and conversions.

### 10.2 Platform Comparison

Purpose: compare the four advertising channels using volume and efficiency metrics.

Components:

- Platform summary table or compact cards containing spend, clicks, conversions, revenue, CPA, ROAS, and ROI
- Metric selector and horizontal bar chart for Spend, Revenue, Clicks, Conversions, CPA, ROAS, or ROI; only one unit is plotted at a time
- Horizontal comparison chart for ROI
- Downloadable platform summary CSV

Platforms with no matching rows after filtering are omitted from charts and identified in a short caption.

### 10.3 Campaign Details

Purpose: allow inspection of individual campaigns.

Components:

- Case-insensitive search by campaign ID or campaign name
- Campaign-level aggregate table
- Columns for campaign ID, campaign name, platform, audience, goal, spend, impressions, clicks, conversions, revenue, CTR, CPC, conversion rate, CPA, ROAS, and ROI
- Sortable columns through Streamlit's data table behavior
- Download button for the currently filtered and searched table

If one campaign appears across multiple audience or goal values, the displayed campaign-level row uses comma-separated category labels while numeric fields aggregate across all matching records.

### 10.4 Time Series

Purpose: explore changes in performance over time.

Components:

- Metric selector for Spend, Revenue, Clicks, Conversions, CTR, CPA, ROAS, and ROI
- Aggregation selector for Daily, Weekly, or Monthly
- Interactive Plotly line chart
- Optional platform breakdown toggle, off by default

Additive metrics are summed by period. Ratio metrics are recalculated from each period's aggregate totals. Weekly periods begin on Monday. Monthly periods use calendar months.

## 11. UI and Accessibility

The implementation will follow the approved mockups in `docs/mockups/` while using Streamlit-native controls where practical.

Requirements:

- Wide Streamlit layout
- Persistent sidebar for global controls
- Four clearly labeled tabs
- Responsive chart sizing
- High-contrast text and chart colors
- Color paired with labels so meaning does not depend on color alone
- Visible metric units in cards, axes, legends, tables, and tooltips
- Concise help text for ROI, ROAS, CTR, CPA, and CPC
- Keyboard-accessible native controls
- No custom CSS that hides focus states or breaks Streamlit behavior

## 12. Error and Status Handling

### File-level failures

- Unreadable CSV: show a concise error and how to correct it.
- Empty CSV: state that at least one data row is required.
- Invalid schema or values: show all detected blocking errors in one validation result.

### Warnings

Warnings appear in a collapsible validation section above the dashboard. The dashboard remains usable when only warnings exist.

### Empty filtered state

Display the shared empty-state message and a reset button. Stop rendering all four analytical views for that rerun.

### Unexpected failures

Show a user-facing error without exposing a raw stack trace in the main interface. Development logs may retain the traceback.

## 13. Testing Strategy

Business logic will use pure functions wherever possible.

### Data-loading tests

- Load the bundled sample CSV.
- Preserve campaign IDs as strings.
- Normalize headers and supported platform capitalization.
- Produce a deterministic sample row count and date range.

### Validation tests

- Accept a valid minimal dataset.
- Report every missing required column.
- Reject invalid dates and numeric values.
- Reject blank campaign identifiers and names.
- Reject unsupported platforms.
- Reject negative metrics.
- Reject fractional count metrics.
- Return warnings for duplicate grain and unusual metric relationships.

### Metric tests

- Verify every total and ratio formula with hand-calculated fixtures.
- Verify ratios are calculated from aggregate totals rather than averaged row values.
- Verify zero denominators return `None`.
- Verify monetary, percentage, multiplier, and count formatting.

### Filter tests

- Verify inclusive date boundaries.
- Verify OR behavior within a filter.
- Verify AND behavior across filters.
- Verify reset-equivalent selections return the full dataset.
- Verify a non-matching selection returns an empty DataFrame.

### View-aggregation tests

- Verify platform aggregation totals.
- Verify campaign aggregation and combined categorical labels.
- Verify daily, Monday-based weekly, and monthly time-series aggregation.
- Verify ratio metrics are recalculated for each time period.

### Application smoke validation

- Import `app.py` without syntax errors.
- Start Streamlit in headless mode and confirm the server becomes healthy.
- Manually verify the sample-data path, upload path, global filters, four tabs, search, downloads, and empty state before submission.

## 14. Documentation Deliverables

### Project documentation

`docs/project-documentation.md` will contain:

1. Project overview and intended user
2. Feature summary
3. Dataset schema and sample-data explanation
4. Technology choices
5. AI prompts used during planning and implementation
6. Iterations and design decisions
7. Bugs encountered and fixes
8. Testing and validation performed
9. Learnings and observations
10. Repository and deployed-app links when available

### Prompt log

`docs/prompt-log.md` records the major user prompts and concise summaries of how AI output influenced the work. It must not claim that unimplemented suggestions were completed.

### Bug and iteration log

`docs/bug-and-iteration-log.md` records the date, symptom, cause, correction, and validation evidence for meaningful issues.

### Video demo script

`docs/video-demo-script.md` targets four to five minutes:

- 0:00–0:30: problem and audience
- 0:30–1:00: data source and schema
- 1:00–2:45: filters and four views
- 2:45–3:30: upload and validation behavior
- 3:30–4:15: AI-assisted workflow, bugs, and iterations
- 4:15–4:45: testing, takeaways, and repository link

## 15. Acceptance Checklist

- [x] Sample dataset loads on first launch.
- [x] CSV upload accepts a valid file and replaces sample data.
- [x] Invalid files produce actionable validation feedback.
- [x] Required schema contains `revenue` and does not contain `conversion_value`.
- [x] Date, platform, audience, and goal filters affect every view.
- [x] All four required views are implemented.
- [x] Campaign details are searchable.
- [x] Time-series aggregation supports daily, weekly, and monthly periods.
- [x] Metric units are visible and formulas match this specification.
- [x] Zero denominators display `N/A`.
- [x] Empty filtered results show the required message.
- [x] Filtered data and summaries can be downloaded where specified.
- [x] Automated tests pass.
- [x] Streamlit smoke validation passes.
- [x] README includes local setup, tests, data schema, and deployment instructions.
- [x] Project documentation and video script are complete.
- [x] Mockups are retained under `docs/mockups/`.

## 16. Implementation Constraints

- Prefer simple, readable functions over framework-heavy abstractions.
- Do not add a database, authentication, or external API integration.
- Do not calculate ratios by averaging precomputed row-level ratios.
- Do not silently repair invalid source values.
- Keep `app.py` focused on UI composition and orchestration.
- Ensure tests do not require a browser or network connection, except for the explicit optional smoke-validation command.
