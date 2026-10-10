# Video Demo Script — 4:45 Target

## 0:00–0:30 — Problem and audience

“This is my Ad Campaign Performance Analyzer. It helps a marketer compare campaigns and channels to see where spend is producing clicks, conversions, revenue, and return. I built it in Python with Streamlit, pandas, Plotly, and pytest.”

Show the application title and briefly point to the persistent filter sidebar and four tabs.

## 0:30–1:00 — Data source and schema

Keep **Sample data** selected.

“The app opens with a deterministic sample containing 1,080 daily records for 12 campaigns across Facebook, Instagram, Pinterest, and Twitter. An uploaded CSV uses the same 11-column schema. Revenue is required, and uploaded data is processed in memory.”

Point to the source and filtered-row caption in Overview.

## 1:00–2:45 — Filters and four views

1. In **Overview**, explain the Spend, Revenue, Conversions, ROI, CPA, and ROAS cards. Point out USD, count, percent, and multiplier units. Hover over the weekly spend-versus-conversions chart.
2. Change **Channel** to Facebook and Instagram. Say that the same filtered DataFrame powers every view.
3. Open **Platform Comparison**. Change the metric selector from Spend to ROI. Show the chart, summary table, and **Download platform summary CSV** button.
4. Open **Campaign Details**. Search for `Sales`, show the narrowed campaign rows, and point to **Download campaign details CSV**.
5. Open **Time Series**. Change Weekly to Monthly, select Revenue, then enable **Break down by platform**. Point out the labeled platform traces.
6. Briefly clear all Channel selections to show the documented empty-state message, then click the reset button.

## 2:45–3:30 — Upload and validation

Switch the source to **Upload CSV** and upload `data/sample_campaigns.csv` as a valid example.

“A valid upload replaces the sample data for this session.”

Then upload a prepared invalid CSV with a missing `revenue` header or a negative spend value.

“Blocking errors are shown together with the affected columns. Non-blocking issues, such as duplicate grain or conversions above clicks, appear as warnings while the dashboard remains usable.”

Switch back to Sample data.

## 3:30–4:15 — AI-assisted workflow and iterations

Show `docs/prompt-log.md`, the saved mockups, and `docs/bug-and-iteration-log.md`.

“I used AI to expand the assignment into a specification, define the schema, create a GUI mockup, write the implementation plan, and implement it with tests first. One important iteration was removing the ambiguous `conversion_value` fallback and requiring `revenue`. I also separated business logic from the Streamlit page so calculations could be verified independently.”

Mention the recorded sandbox socket issue and explain that the unchanged app passed its health check outside the restricted environment.

## 4:15–4:45 — Tests, takeaways, and repository

Show a terminal in `Week1/` and run:

```bash
python -m pytest -v
```

“The 68 tests cover validation, filters, formulas, aggregations, chart contracts, exports, and the Streamlit UI. My main takeaway is that rates must be recalculated from totals, and clear schema validation makes analytics more trustworthy.”

Finish by showing the repository README and GitHub location. Replace the placeholder link in the documentation after publishing.
