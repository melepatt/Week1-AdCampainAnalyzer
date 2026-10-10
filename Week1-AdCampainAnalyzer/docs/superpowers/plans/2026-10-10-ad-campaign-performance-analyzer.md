# Ad Campaign Performance Analyzer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and validate a Streamlit dashboard that analyzes daily campaign CSV data across Facebook, Instagram, Pinterest, and Twitter using synchronized filters and four analytical views.

**Architecture:** Keep Streamlit orchestration in `app.py` and place data ingestion, validation, calculations, filtering, aggregation, formatting, and Plotly figure construction in focused modules under `src/`. All views consume one validated and globally filtered pandas DataFrame, allowing business rules to be tested without a running browser.

**Tech Stack:** Python 3.11+, Streamlit, pandas, Plotly, pytest, Streamlit AppTest

**Spec:** `Week1-AdCampainAnalyzer/docs/superpowers/specs/2026-10-10-ad-campaign-performance-analyzer-design.md`

## Global Constraints

- Use Python 3.11 or later.
- Treat all monetary values as USD; mixed currencies are out of scope.
- Accept only Facebook, Instagram, Pinterest, and Twitter as canonical platforms.
- Require `revenue`; do not support `conversion_value`.
- Calculate ratios from aggregate totals, never by averaging row-level ratios.
- Return `None` for ratios with a zero denominator and display them as `N/A`.
- Uploaded CSV data stays in memory and is never persisted.
- Use one filtered DataFrame for all four views.
- Keep tests browser- and network-independent except for the explicit local Streamlit smoke command.
- Do not add authentication, a database, live ad APIs, prediction, or campaign editing.
- Follow the approved `Week1-AdCampainAnalyzer/docs/mockups/` layout while preferring Streamlit-native, keyboard-accessible controls.
- Show metric units in cards, tables, axes, legends, and hover labels; pair chart colors with visible labels.

## Review Focus

- CSVs with normalized duplicate headers, such as both `Campaign ID` and `campaign_id`, must fail with an explicit duplicate-column error; covered in Task 2.
- CSVs containing `NaN`, `inf`, or `-inf` numeric values must fail validation rather than leak invalid Plotly values; covered in Task 2.
- A user selecting no values in a categorical filter must receive an empty result and the shared empty state, not an implicit “select all”; covered in Tasks 4 and 6.
- A campaign ID associated with multiple names must remain usable but display a warning and aggregate labels deterministically; covered in Tasks 2 and 4.
- Weekly date aggregation must use Monday-start periods across month boundaries without dropping Sunday data; covered in Task 4.

---

## File Map

| File | Responsibility |
|---|---|
| `.gitignore` | Exclude local environments, caches, coverage files, Streamlit secrets, and `.superpowers/` runtime state |
| `Week1-AdCampainAnalyzer/requirements.txt` | Runtime and test dependencies |
| `Week1-AdCampainAnalyzer/pytest.ini` | Test discovery and local import path |
| `Week1-AdCampainAnalyzer/app.py` | Streamlit page composition, source selection, shared filters, tabs, empty and error states |
| `Week1-AdCampainAnalyzer/src/data_loader.py` | CSV reading, column-name normalization, sample-data access |
| `Week1-AdCampainAnalyzer/src/validation.py` | Schema coercion, blocking errors, non-blocking warnings |
| `Week1-AdCampainAnalyzer/src/metrics.py` | Summary metric calculations and platform/campaign/time aggregations |
| `Week1-AdCampainAnalyzer/src/filters.py` | Immutable filter selection and shared filtering |
| `Week1-AdCampainAnalyzer/src/formatting.py` | Display formatting for currency, counts, percentages, and multipliers |
| `Week1-AdCampainAnalyzer/src/charts.py` | Plotly figure factories with unit-aware labels |
| `Week1-AdCampainAnalyzer/src/exporting.py` | Convert filtered summaries to deterministic UTF-8 CSV downloads |
| `Week1-AdCampainAnalyzer/scripts/generate_sample_data.py` | Deterministic 90-day, 12-campaign sample-data generator |
| `Week1-AdCampainAnalyzer/data/sample_campaigns.csv` | Bundled 1,080-row demonstration dataset |
| `Week1-AdCampainAnalyzer/tests/` | Unit, aggregation, chart-contract, and Streamlit smoke tests |
| `Week1-AdCampainAnalyzer/README.md` | Setup, run, test, schema, deployment, and project navigation |
| `Week1-AdCampainAnalyzer/docs/*.md` | Class documentation, prompt/iteration log, and video script |

### Task 1: Project Foundation and Deterministic Sample Data

**Files:**
- Create: `.gitignore`
- Create: `Week1-AdCampainAnalyzer/requirements.txt`
- Create: `Week1-AdCampainAnalyzer/pytest.ini`
- Create: `Week1-AdCampainAnalyzer/src/__init__.py`
- Create: `Week1-AdCampainAnalyzer/scripts/generate_sample_data.py`
- Create: `Week1-AdCampainAnalyzer/data/sample_campaigns.csv`
- Create: `Week1-AdCampainAnalyzer/tests/test_sample_data.py`

**Interfaces:**
- Produces: `generate_sample_data(seed: int = 42) -> pandas.DataFrame`
- Produces: a checked-in CSV with exactly 1,080 daily rows from `2026-01-01` through `2026-03-31`
- Consumes: no application modules

- [ ] **Step 1: Write the failing sample-data contract test**

Create tests named `test_generate_sample_data_has_required_shape_and_dates`, `test_generate_sample_data_balances_platforms`, and `test_generate_sample_data_is_deterministic`. Assert:

```python
assert len(frame) == 1080
assert frame["date"].min() == pd.Timestamp("2026-01-01")
assert frame["date"].max() == pd.Timestamp("2026-03-31")
assert frame["campaign_id"].nunique() == 12
assert set(frame["platform"]) == {"Facebook", "Instagram", "Pinterest", "Twitter"}
assert frame.groupby("platform")["campaign_id"].nunique().to_dict() == {
    "Facebook": 3,
    "Instagram": 3,
    "Pinterest": 3,
    "Twitter": 3,
}
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd Week1 && python -m pytest tests/test_sample_data.py -v`
Expected: FAIL because `scripts.generate_sample_data` does not exist.

- [ ] **Step 3: Add project configuration**

Create dependencies for Streamlit, pandas, Plotly, and pytest in `requirements.txt`. Configure `pytest.ini` with `pythonpath = .` and `testpaths = tests`. Add `.superpowers/`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.coverage`, `htmlcov/`, and `.streamlit/secrets.toml` to the repository-root `.gitignore`; unstage existing `.superpowers/` runtime files without deleting them.

- [ ] **Step 4: Implement the deterministic generator**

Implement `generate_sample_data(seed: int = 42) -> pd.DataFrame` with 12 fixed campaign definitions and 90 dates. Use a local NumPy random generator or deterministic arithmetic, ensure non-negative values, and derive revenue from conversions and a fixed campaign purchase value only inside the generator; the produced CSV contains only the required schema and actual `revenue` values.

- [ ] **Step 5: Generate and check in the sample CSV**

Run: `cd Week1 && python scripts/generate_sample_data.py`
Expected: creates `data/sample_campaigns.csv` with 1,080 rows and canonical header order.

- [ ] **Step 6: Run the tests and generator verification**

Run: `cd Week1 && python -m pytest tests/test_sample_data.py -v`
Expected: all sample-data tests PASS.

- [ ] **Step 7: Commit**

```bash
git add .gitignore Week1-AdCampainAnalyzer/requirements.txt Week1-AdCampainAnalyzer/pytest.ini Week1-AdCampainAnalyzer/src/__init__.py Week1-AdCampainAnalyzer/scripts/generate_sample_data.py Week1-AdCampainAnalyzer/data/sample_campaigns.csv Week1-AdCampainAnalyzer/tests/test_sample_data.py
git commit -m "feat: add project foundation and sample campaign data"
```

### Task 2: CSV Loading and Validation

**Files:**
- Create: `Week1-AdCampainAnalyzer/src/data_loader.py`
- Create: `Week1-AdCampainAnalyzer/src/validation.py`
- Create: `Week1-AdCampainAnalyzer/tests/conftest.py`
- Create: `Week1-AdCampainAnalyzer/tests/test_data_loader.py`
- Create: `Week1-AdCampainAnalyzer/tests/test_validation.py`

**Interfaces:**
- Consumes: `Week1-AdCampainAnalyzer/data/sample_campaigns.csv`
- Produces: `normalize_column_name(name: object) -> str`
- Produces: `read_campaign_csv(source: str | pathlib.Path | BinaryIO) -> pandas.DataFrame`
- Produces: `load_sample_data(path: pathlib.Path | None = None) -> pandas.DataFrame`
- Produces: immutable `ValidationResult(data: pandas.DataFrame | None, errors: tuple[str, ...], warnings: tuple[str, ...])`
- Produces: `validate_campaign_data(frame: pandas.DataFrame) -> ValidationResult`

- [ ] **Step 1: Add shared valid-data fixtures**

Create `valid_campaign_frame` with two rows that exercise two platforms and preserve campaign IDs `C001` and `0012` as strings.

- [ ] **Step 2: Write failing loader tests**

Add tests for canonicalizing `Campaign ID` to `campaign_id`, trimming headers, preserving leading-zero IDs, loading from `io.BytesIO`, loading the bundled sample file, and rejecting two headers that normalize to the same name.

- [ ] **Step 3: Run loader tests to verify failure**

Run: `cd Week1 && python -m pytest tests/test_data_loader.py -v`
Expected: FAIL because `src.data_loader` does not exist.

- [ ] **Step 4: Implement the loader**

Read all fields as strings so IDs remain intact. Normalize headers using lowercase snake case, reject duplicate normalized names with `ValueError`, and expose `REQUIRED_COLUMNS`, `NUMERIC_COLUMNS`, `COUNT_COLUMNS`, `TEXT_COLUMNS`, and `SUPPORTED_PLATFORMS` constants for validation.

- [ ] **Step 5: Run loader tests**

Run: `cd Week1 && python -m pytest tests/test_data_loader.py -v`
Expected: all loader tests PASS.

- [ ] **Step 6: Write failing validation tests**

Add tests named for: valid coercion, every missing column reported, empty frame, invalid dates, blank identifiers and names, unsupported platform, non-numeric metrics, negative metrics, fractional counts, non-finite metrics, duplicate-grain warning, clicks-over-impressions warning, conversions-over-clicks warning, zero-spend-positive-revenue warning, and campaign-ID/name conflict warning.

- [ ] **Step 7: Run validation tests to verify failure**

Run: `cd Week1 && python -m pytest tests/test_validation.py -v`
Expected: FAIL because `validate_campaign_data` does not exist.

- [ ] **Step 8: Implement validation and typed output**

Return all blocking errors in one result. On success, return a defensive copy with datetime dates, float `spend` and `revenue`, integer counts, trimmed text, and canonical platform values. Sort messages deterministically to keep tests and UI stable.

- [ ] **Step 9: Run data-layer tests**

Run: `cd Week1 && python -m pytest tests/test_data_loader.py tests/test_validation.py -v`
Expected: all data-layer tests PASS.

- [ ] **Step 10: Commit**

```bash
git add Week1-AdCampainAnalyzer/src/data_loader.py Week1-AdCampainAnalyzer/src/validation.py Week1-AdCampainAnalyzer/tests/conftest.py Week1-AdCampainAnalyzer/tests/test_data_loader.py Week1-AdCampainAnalyzer/tests/test_validation.py
git commit -m "feat: validate campaign CSV data"
```

### Task 3: Metrics and Formatting

**Files:**
- Create: `Week1-AdCampainAnalyzer/src/metrics.py`
- Create: `Week1-AdCampainAnalyzer/src/formatting.py`
- Create: `Week1-AdCampainAnalyzer/tests/test_metrics.py`
- Create: `Week1-AdCampainAnalyzer/tests/test_formatting.py`

**Interfaces:**
- Consumes: validated campaign DataFrames from Task 2
- Produces: `safe_ratio(numerator: float, denominator: float, scale: float = 1.0) -> float | None`
- Produces: `calculate_summary(frame: pandas.DataFrame) -> dict[str, int | float | None]`
- Produces: `add_ratio_metrics(frame: pandas.DataFrame) -> pandas.DataFrame`
- Produces: `format_currency(value: float | None) -> str`
- Produces: `format_count(value: int | float | None) -> str`
- Produces: `format_percent(value: float | None) -> str`
- Produces: `format_multiplier(value: float | None) -> str`

- [ ] **Step 1: Write failing metric tests**

Use a two-row fixture where the average of row ratios differs from the aggregate ratio. Assert totals and exact formulas for `ctr`, `cpc`, `conversion_rate`, `cpa`, `roas`, and `roi`. Assert each zero denominator returns `None` and no result is infinite.

- [ ] **Step 2: Run metric tests to verify failure**

Run: `cd Week1 && python -m pytest tests/test_metrics.py -v`
Expected: FAIL because `src.metrics` does not exist.

- [ ] **Step 3: Implement summary calculations**

Use canonical output keys: `spend`, `revenue`, `impressions`, `clicks`, `conversions`, `ctr`, `cpc`, `conversion_rate`, `cpa`, `roas`, and `roi`. `add_ratio_metrics` accepts aggregate rows containing the five additive metrics and appends the six ratios without mutating its input.

- [ ] **Step 4: Run metric tests**

Run: `cd Week1 && python -m pytest tests/test_metrics.py -v`
Expected: all metric tests PASS.

- [ ] **Step 5: Write failing formatting tests**

Assert examples: `$12,450.75`, `2,418`, `182.7%`, `2.83×`, and `N/A` for `None` or non-finite inputs.

- [ ] **Step 6: Implement display formatting and run tests**

Run: `cd Week1 && python -m pytest tests/test_formatting.py tests/test_metrics.py -v`
Expected: all metric and formatting tests PASS.

- [ ] **Step 7: Commit**

```bash
git add Week1-AdCampainAnalyzer/src/metrics.py Week1-AdCampainAnalyzer/src/formatting.py Week1-AdCampainAnalyzer/tests/test_metrics.py Week1-AdCampainAnalyzer/tests/test_formatting.py
git commit -m "feat: calculate and format campaign metrics"
```

### Task 4: Shared Filters and Analytical Aggregations

**Files:**
- Create: `Week1-AdCampainAnalyzer/src/filters.py`
- Modify: `Week1-AdCampainAnalyzer/src/metrics.py`
- Create: `Week1-AdCampainAnalyzer/tests/test_filters.py`
- Create: `Week1-AdCampainAnalyzer/tests/test_aggregations.py`

**Interfaces:**
- Consumes: `add_ratio_metrics` from Task 3
- Produces: immutable `FilterSelection(start_date: datetime.date, end_date: datetime.date, platforms: tuple[str, ...], audiences: tuple[str, ...], goals: tuple[str, ...])`
- Produces: `apply_filters(frame: pandas.DataFrame, selection: FilterSelection) -> pandas.DataFrame`
- Produces: `aggregate_by_platform(frame: pandas.DataFrame) -> pandas.DataFrame`
- Produces: `aggregate_by_campaign(frame: pandas.DataFrame) -> pandas.DataFrame`
- Produces: `aggregate_time_series(frame: pandas.DataFrame, frequency: Literal["Daily", "Weekly", "Monthly"], break_down_by_platform: bool = False) -> pandas.DataFrame`

- [ ] **Step 1: Write failing filter tests**

Test inclusive date bounds, OR logic within platforms, AND logic across platform/audience/goal, full selections preserving all rows, empty categorical selections returning no rows, and non-matching selections returning no rows. Assert the input DataFrame is not mutated.

- [ ] **Step 2: Run filter tests to verify failure**

Run: `cd Week1 && python -m pytest tests/test_filters.py -v`
Expected: FAIL because `src.filters` does not exist.

- [ ] **Step 3: Implement immutable shared filtering**

Apply date and categorical masks in one function and return a copied, date-sorted DataFrame with its index reset.

- [ ] **Step 4: Run filter tests**

Run: `cd Week1 && python -m pytest tests/test_filters.py -v`
Expected: all filter tests PASS.

- [ ] **Step 5: Write failing aggregation tests**

Assert additive totals and recalculated ratios for platform and campaign output. Assert campaign category labels are sorted, comma-separated, and stable. Test Daily, Weekly, and Monthly results; include Saturday, Sunday, and Monday around a month boundary and assert Sunday belongs to the Monday-start week containing it. Assert `break_down_by_platform=True` retains one row per date period and platform.

- [ ] **Step 6: Implement aggregation functions**

Use `date.to_period("W-SUN").start_time` for Monday-start weekly labels and calendar month starts for Monthly. Aggregate the five additive metrics first, then call `add_ratio_metrics`.

- [ ] **Step 7: Run calculation tests**

Run: `cd Week1 && python -m pytest tests/test_filters.py tests/test_aggregations.py tests/test_metrics.py -v`
Expected: all calculation tests PASS.

- [ ] **Step 8: Commit**

```bash
git add Week1-AdCampainAnalyzer/src/filters.py Week1-AdCampainAnalyzer/src/metrics.py Week1-AdCampainAnalyzer/tests/test_filters.py Week1-AdCampainAnalyzer/tests/test_aggregations.py
git commit -m "feat: add shared filters and campaign aggregations"
```

### Task 5: Plotly Figure Factories

**Files:**
- Create: `Week1-AdCampainAnalyzer/src/charts.py`
- Create: `Week1-AdCampainAnalyzer/tests/test_charts.py`

**Interfaces:**
- Consumes: aggregate DataFrames from Task 4
- Produces: `build_spend_conversions_chart(time_frame: pandas.DataFrame) -> plotly.graph_objects.Figure`
- Produces: `build_platform_metric_chart(platform_frame: pandas.DataFrame, metric: str) -> plotly.graph_objects.Figure`
- Produces: `build_time_series_chart(time_frame: pandas.DataFrame, metric: str, break_down_by_platform: bool = False) -> plotly.graph_objects.Figure`
- Produces: `METRIC_LABELS` and `METRIC_UNITS` mappings used by charts and UI selectors

- [ ] **Step 1: Write failing chart-contract tests**

Assert the overview chart contains a spend bar trace and conversions line trace with separate labeled axes. Parameterize platform and time-series tests across USD, count, percent, and multiplier metrics; assert titles, axis units, hover templates, category order, and empty-input behavior.

- [ ] **Step 2: Run chart tests to verify failure**

Run: `cd Week1 && python -m pytest tests/test_charts.py -v`
Expected: FAIL because `src.charts` does not exist.

- [ ] **Step 3: Implement figure factories**

Use accessible labels, restrained platform colors, responsive margins, horizontal bars for platform comparison, and no global mutable figure state. Empty inputs return figures with a centered “No data” annotation.

- [ ] **Step 4: Run chart tests**

Run: `cd Week1 && python -m pytest tests/test_charts.py -v`
Expected: all chart tests PASS.

- [ ] **Step 5: Commit**

```bash
git add Week1-AdCampainAnalyzer/src/charts.py Week1-AdCampainAnalyzer/tests/test_charts.py
git commit -m "feat: add campaign analysis charts"
```

### Task 6: Streamlit Application and Four Views

**Files:**
- Create: `Week1-AdCampainAnalyzer/app.py`
- Create: `Week1-AdCampainAnalyzer/src/exporting.py`
- Create: `Week1-AdCampainAnalyzer/tests/test_app.py`
- Create: `Week1-AdCampainAnalyzer/tests/test_exporting.py`

**Interfaces:**
- Consumes: every public interface from Tasks 2–5
- Produces: `dataframe_to_csv_bytes(frame: pandas.DataFrame) -> bytes`
- Produces: executable Streamlit application with Overview, Platform Comparison, Campaign Details, and Time Series tabs

- [ ] **Step 1: Write failing non-UI app helper test**

Assert `dataframe_to_csv_bytes` returns deterministic UTF-8 CSV bytes with the input column order and no index column.

- [ ] **Step 2: Write failing Streamlit AppTest smoke test**

Load `app.py` with sample data and assert: no exception, page title is present, sidebar contains the four required filter groups, all four tab labels exist, and the initial view includes spend, revenue, conversions, and ROI labels.

- [ ] **Step 3: Run app tests to verify failure**

Run: `cd Week1 && python -m pytest tests/test_exporting.py tests/test_app.py -v`
Expected: FAIL because `src.exporting` and `app.py` do not exist.

- [ ] **Step 4: Implement application shell and data-source flow**

Configure wide layout, render the approved title, expose Sample data and Upload CSV modes, read and validate the selected source, show all blocking errors together, and stop before filters when validation fails. Show warnings in an expander when validation succeeds with warnings. Catch unexpected load or rendering exceptions at the page boundary, log the traceback, and show a concise user-facing error without a raw stack trace.

- [ ] **Step 5: Implement synchronized filters and empty state**

Create one `FilterSelection`, call `apply_filters` once, display the active-filter summary, and use the exact shared empty-state copy from the spec. A Reset filters button restores the full source selections through Streamlit session state.

- [ ] **Step 6: Implement Overview and Platform Comparison**

Render unit-labeled KPI cards, supporting CPA and ROAS values, the weekly spend/conversions chart, ROI-by-platform chart, platform summary, a single-metric selector, and a platform-summary download using `dataframe_to_csv_bytes`.

- [ ] **Step 7: Implement Campaign Details and Time Series**

Add case-insensitive campaign ID/name search, the complete campaign aggregate table, searched-table download using `dataframe_to_csv_bytes`, metric and frequency selectors, and the platform-breakdown toggle. Recalculate ratio metrics after every time grouping.

- [ ] **Step 8: Run app tests**

Run: `cd Week1 && python -m pytest tests/test_exporting.py tests/test_app.py -v`
Expected: all export and app tests PASS.

- [ ] **Step 9: Run the full automated suite**

Run: `cd Week1 && python -m pytest -v`
Expected: all tests PASS with no warnings originating from project code.

- [ ] **Step 10: Run the local Streamlit smoke check**

Run: `cd Week1 && python -m streamlit run app.py --server.headless true --server.port 8501`
Expected: process starts and reports a local URL without an exception; stop it after checking the health endpoint or initial page.

- [ ] **Step 11: Commit**

```bash
git add Week1-AdCampainAnalyzer/app.py Week1-AdCampainAnalyzer/src/exporting.py Week1-AdCampainAnalyzer/tests/test_app.py Week1-AdCampainAnalyzer/tests/test_exporting.py
git commit -m "feat: build campaign performance dashboard"
```

### Task 7: Class Documentation and Release Validation

**Files:**
- Create: `Week1-AdCampainAnalyzer/README.md`
- Create: `Week1-AdCampainAnalyzer/docs/project-documentation.md`
- Create: `Week1-AdCampainAnalyzer/docs/prompt-log.md`
- Create: `Week1-AdCampainAnalyzer/docs/bug-and-iteration-log.md`
- Create: `Week1-AdCampainAnalyzer/docs/video-demo-script.md`
- Modify: `Week1-AdCampainAnalyzer/docs/superpowers/specs/2026-10-10-ad-campaign-performance-analyzer-design.md`

**Interfaces:**
- Consumes: final application behavior and verification evidence from Tasks 1–6
- Produces: GitHub-ready instructions and the three class submission support documents

- [ ] **Step 1: Write README setup and usage instructions**

Document Python 3.11+, virtual-environment setup, `pip install -r requirements.txt`, `streamlit run app.py`, `pytest -v`, required CSV schema, metric formulas, deployment steps for Streamlit Community Cloud and Replit, and links to the design and mockups.

- [ ] **Step 2: Write project documentation**

Cover the project overview, dataset, architecture, four views, filters, AI-assisted workflow, prompt summary, implemented iterations, encountered bugs, testing evidence, and learnings. Label the GitHub and deployment links `Not published yet` until the student supplies them.

- [ ] **Step 3: Complete prompt and bug logs**

Record the prompts already supplied in this thread and only the bugs actually encountered. Use dated entries with symptom, cause, change, and verification evidence; do not invent failures.

- [ ] **Step 4: Write the timed video script**

Create a four-to-five-minute narration following the timing in the spec, with explicit clicks for sample data, one filter change, all four tabs, valid upload, invalid upload, tests, and repository location.

- [ ] **Step 5: Update spec status and acceptance checklist**

Change status to `Implemented and verified` only for requirements supported by fresh verification. Mark each acceptance item individually and leave any unmet item unchecked with a note.

- [ ] **Step 6: Run release verification**

Run: `cd Week1 && python -m pytest -v`
Expected: all tests PASS.

Run: `cd Week1 && python -m compileall app.py src scripts tests`
Expected: exit code 0.

Run: `git diff --check`
Expected: no whitespace errors.

- [ ] **Step 7: Compare implementation against the acceptance checklist**

Manually verify both data-source modes, all global filters, all four views, metric units, search, downloads, warnings, blocking errors, zero denominators, and empty-filter behavior. Record evidence in `docs/project-documentation.md`.

- [ ] **Step 8: Commit**

```bash
git add Week1-AdCampainAnalyzer/README.md Week1-AdCampainAnalyzer/docs/project-documentation.md Week1-AdCampainAnalyzer/docs/prompt-log.md Week1-AdCampainAnalyzer/docs/bug-and-iteration-log.md Week1-AdCampainAnalyzer/docs/video-demo-script.md Week1-AdCampainAnalyzer/docs/superpowers/specs/2026-10-10-ad-campaign-performance-analyzer-design.md
git commit -m "docs: complete campaign analyzer submission materials"
```
