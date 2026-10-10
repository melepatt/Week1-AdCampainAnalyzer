"""Generate the deterministic demonstration dataset used by the dashboard."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


COLUMNS = [
    "date",
    "campaign_id",
    "campaign_name",
    "platform",
    "audience",
    "campaign_goal",
    "spend",
    "impressions",
    "clicks",
    "conversions",
    "revenue",
]

CAMPAIGNS = (
    ("FB001", "Facebook Brand Lift", "Facebook", "Broad Adults", "Awareness", 45.0),
    ("FB002", "Facebook Site Visits", "Facebook", "Website Visitors", "Traffic", 62.0),
    ("FB003", "Facebook Holiday Sales", "Facebook", "Past Customers", "Sales", 105.0),
    ("IG001", "Instagram Reach", "Instagram", "Young Adults", "Awareness", 48.0),
    ("IG002", "Instagram Style Guide", "Instagram", "Fashion Enthusiasts", "Traffic", 68.0),
    ("IG003", "Instagram Shop Now", "Instagram", "Past Customers", "Sales", 115.0),
    ("PI001", "Pinterest Inspiration", "Pinterest", "Home Decor Fans", "Awareness", 52.0),
    ("PI002", "Pinterest Planning", "Pinterest", "DIY Planners", "Traffic", 72.0),
    ("PI003", "Pinterest Lead Magnet", "Pinterest", "New Homeowners", "Leads", 82.0),
    ("TW001", "Twitter Conversation", "Twitter", "Tech Professionals", "Awareness", 42.0),
    ("TW002", "Twitter Product News", "Twitter", "Website Visitors", "Traffic", 66.0),
    ("TW003", "Twitter Demo Leads", "Twitter", "Business Decision Makers", "Leads", 94.0),
)


def generate_sample_data(seed: int = 42) -> pd.DataFrame:
    """Return 90 daily observations for each of 12 fixed campaigns."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2026-01-01", "2026-03-31", freq="D")
    rows: list[dict[str, object]] = []

    for campaign_index, campaign in enumerate(CAMPAIGNS):
        campaign_id, name, platform, audience, goal, purchase_value = campaign
        platform_factor = 0.9 + (campaign_index % 4) * 0.08
        for day_index, date in enumerate(dates):
            weekday_factor = 1.12 if date.dayofweek in (4, 5) else 1.0
            trend = 1.0 + day_index * 0.0015
            spend = round(max(18.0, rng.normal(118 + campaign_index * 4, 13)) * trend, 2)
            impressions = int(max(500, round(spend * rng.uniform(42, 58) * platform_factor)))
            click_rate = rng.uniform(0.018, 0.048) * weekday_factor
            clicks = min(impressions, int(round(impressions * click_rate)))
            conversion_rate = rng.uniform(0.035, 0.13)
            conversions = min(clicks, int(round(clicks * conversion_rate)))
            revenue = round(conversions * purchase_value * rng.uniform(0.9, 1.12), 2)
            rows.append(
                {
                    "date": date,
                    "campaign_id": campaign_id,
                    "campaign_name": name,
                    "platform": platform,
                    "audience": audience,
                    "campaign_goal": goal,
                    "spend": spend,
                    "impressions": impressions,
                    "clicks": clicks,
                    "conversions": conversions,
                    "revenue": revenue,
                }
            )

    return pd.DataFrame(rows, columns=COLUMNS)


def main() -> None:
    destination = Path(__file__).resolve().parents[1] / "data" / "sample_campaigns.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    generate_sample_data().to_csv(destination, index=False, date_format="%Y-%m-%d")
    print(f"Wrote {destination} with 1,080 rows")


if __name__ == "__main__":
    main()
