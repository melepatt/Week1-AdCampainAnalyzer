# Ad Campaign Performance Analyzer

A Streamlit dashboard for comparing campaign spend, clicks, conversions, revenue, and return across Facebook, Instagram, Pinterest, and Twitter. It opens with a deterministic sample dataset and can analyze a conforming uploaded CSV entirely in memory.

## Features

- One shared set of date, channel, audience, and campaign-goal filters
- Overview KPIs and weekly spend-versus-conversions trends
- Channel comparisons with a selectable metric and CSV download
- Searchable campaign-level details and CSV download
- Daily, weekly, and monthly time-series exploration
- Actionable CSV validation errors and non-blocking quality warnings
- Explicit USD, count, percent, and multiplier units
- A clear empty state when filters match no records

## Run locally

Python 3.11 or later is required.

```bash
cd Week1
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. The bundled sample data is selected by default.

Run the automated tests:

```bash
cd Week1
python -m pytest -v
```

Regenerate the deterministic sample CSV:

```bash
cd Week1
python scripts/generate_sample_data.py
```

## CSV schema

Each row represents one campaign on one platform, for one audience and campaign goal, on one calendar day. Headers are normalized to lowercase snake case, but all of these fields are required:

```csv
date,campaign_id,campaign_name,platform,audience,campaign_goal,spend,impressions,clicks,conversions,revenue
```

| Column | Type and rule |
|---|---|
| `date` | `YYYY-MM-DD` date |
| `campaign_id` | Non-blank text; leading zeroes are preserved |
| `campaign_name` | Non-blank text |
| `platform` | Facebook, Instagram, Pinterest, or Twitter |
| `audience` | Text |
| `campaign_goal` | Text |
| `spend` | Non-negative USD decimal |
| `impressions` | Non-negative integer |
| `clicks` | Non-negative integer |
| `conversions` | Non-negative integer |
| `revenue` | Non-negative USD decimal |

`revenue` is required. The application intentionally does not accept `conversion_value` as an alias. Uploaded files are processed in memory and are not persisted.

## Metric formulas

Ratios are calculated from filtered aggregate totals, never averaged from row-level ratios.

| Metric | Formula | Unit |
|---|---|---|
| CTR | `clicks / impressions × 100` | percent |
| CPC | `spend / clicks` | USD per click |
| Conversion rate | `conversions / clicks × 100` | percent |
| CPA | `spend / conversions` | USD per conversion |
| ROAS | `revenue / spend` | multiplier |
| ROI | `(revenue - spend) / spend × 100` | percent |

A zero denominator displays as `N/A`.

## Deploy

### Streamlit Community Cloud

1. Push the repository to GitHub.
2. In Streamlit Community Cloud, create an app from the repository.
3. Set the app file to `Week1/app.py`.
4. Deploy; dependencies are installed from `Week1/requirements.txt`.

### Replit

1. Import the GitHub repository into a Python Repl.
2. Install with `pip install -r Week1/requirements.txt`.
3. Use this run command: `streamlit run Week1/app.py --server.address 0.0.0.0 --server.port 3000`.
4. Open the generated web preview.

## Project materials

- [Design specification](docs/superpowers/specs/2026-10-10-ad-campaign-performance-analyzer-design.md)
- [Implementation plan](docs/superpowers/plans/2026-10-10-ad-campaign-performance-analyzer.md)
- [Saved GUI mockups](docs/mockups/README.md)
- [Project documentation](docs/project-documentation.md)
- [Prompt log](docs/prompt-log.md)
- [Bug and iteration log](docs/bug-and-iteration-log.md)
- [Video demo script](docs/video-demo-script.md)
