# Video Demo Script — 4:45 Target

## Before recording — not timed

1. Start from the final project directory and launch the app:

   ```bash
   cd Week1-AdCampainAnalyzer
   source .venv/bin/activate
   python -m streamlit run app.py
   ```

2. Keep these items ready to show:
   - the running Streamlit application with **Sample data** selected;
   - `data/test_campaigns_april_september.csv` for the upload demonstration;
   - `docs/prompt-log.md`, `docs/bug-and-iteration-log.md`, and `docs/mockups/`;
   - a terminal in `Week1-AdCampainAnalyzer/`;
   - the public GitHub repository at <https://github.com/melepatt/Week1-AdCampainAnalyzer>.
3. Reset all filters and close unrelated windows or notifications.

## 0:00–0:25 — Problem, audience, and technology

Show the application title, four tabs, and global-filter sidebar.

> “This is my Ad Campaign Performance Analyzer. It helps a marketer or marketing student understand which campaigns and advertising channels are delivering results. I built it with Python, Streamlit, pandas, Plotly, and pytest to compare Facebook, Instagram, Pinterest, and Twitter.”

## 0:25–0:55 — Default data and schema

Keep **Sample data** selected and point to the source caption in **Overview**.

> “The app opens with a deterministic sample containing 1,080 daily records for 12 campaigns from January through March 2026. Each row represents one campaign, platform, audience, goal, and date. Uploaded files use the same required 11-column schema, including spend, clicks, conversions, and revenue. Revenue is the only attributed-value field, and uploads are processed in memory rather than saved.”

## 0:55–2:35 — Global filters and four views

1. In **Overview**, point to **Spend (USD)**, **Revenue (USD)**, **Conversions (count)**, **ROI (%)**, **CPA (USD/conversion)**, and **ROAS (multiplier)**. Hover over the weekly spend-versus-conversions chart.

   > “Every metric shows its unit. Ratios are recalculated from filtered totals instead of averaging row-level percentages.”

2. In the sidebar, select only Facebook and Instagram under **Channel**.

   > “The date, channel, audience, and campaign-goal filters are global, so one filtered dataset powers every view.”

3. Open **Platform Comparison**, change **Platform comparison metric** from Spend to ROI, and show the chart, summary table, and **Download platform summary CSV** button.
4. Open **Campaign Details**, search for `Sales`, and point to the narrowed result and **Download campaign details CSV** button.
5. Open **Time Series**, select Revenue, change **Time aggregation** to Monthly, and enable **Break down by platform**.
6. Clear all **Channel** selections to display the shared empty-state message, then click **Reset filters to show all campaigns**.

   > “An empty selection has an explicit message and recovery action instead of showing misleading blank charts.”

## 2:35–3:15 — Six-month upload and date-range behavior

Switch **Data source** to **Upload CSV** and upload `data/test_campaigns_april_september.csv`.

> “For broader testing, I added a second deterministic dataset with 1,464 records, eight campaigns, and equal coverage across all four platforms from April through September 2026. Selecting a new file resets incompatible filter values for that source.”

Point to the April 1–September 30 date range. Select a later start date and an end date, then show that the filtered-record count and visible metrics update without the start date jumping back.

> “The date control preserves Streamlit’s temporary one-date selection while I choose the end date. CSV validation reports all blocking errors together, while usable anomalies such as duplicate grain are shown as warnings.”

Click **Reset filters**, then return to **Sample data**.

## 3:15–4:05 — AI-assisted workflow and iterations

Show `docs/prompt-log.md`, the images under `docs/mockups/`, and `docs/bug-and-iteration-log.md`.

> “I used AI to expand the assignment into a detailed specification, define the data contract, create and save GUI mockups, write an implementation plan, and build the application with tests first. The prompt log records the major requests and how each one influenced the project.”

> “Important iterations included removing the ambiguous `conversion_value` fallback, preserving in-progress date selections, resetting filters safely when the data source changes, and validating large integer counts without precision loss. After renaming the project directory, an old Streamlit process caused a file-not-found error, which was resolved by restarting the app from the final directory.”

## 4:05–4:45 — Tests, documentation, and repository

In the project terminal, run:

```bash
python -m pytest -q
```

Point to the `76 passed` result.

> “The 76 automated tests cover CSV loading and validation, filters, formulas, aggregations, unit formatting, charts, downloads, date-range behavior, and the Streamlit interface.”

Show the GitHub repository and briefly point to the README, project documentation, prompt log, saved mockups, and this video script.

> “The complete code and documentation are published on GitHub. My main takeaway is that reliable analytics require a clear data contract, consistent filters, visible units, and ratios recalculated from aggregate totals. Those choices make the dashboard easier to understand and trust.”
