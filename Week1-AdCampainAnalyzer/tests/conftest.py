import pandas as pd
import pytest


@pytest.fixture
def valid_campaign_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "date": "2026-01-01",
                "campaign_id": "C001",
                "campaign_name": "New Year Awareness",
                "platform": "Facebook",
                "audience": "Broad Adults",
                "campaign_goal": "Awareness",
                "spend": "100.50",
                "impressions": "10000",
                "clicks": "400",
                "conversions": "20",
                "revenue": "300.00",
            },
            {
                "date": "2026-01-02",
                "campaign_id": "0012",
                "campaign_name": "Style Sales",
                "platform": "Instagram",
                "audience": "Young Adults",
                "campaign_goal": "Sales",
                "spend": "75.25",
                "impressions": "7000",
                "clicks": "280",
                "conversions": "14",
                "revenue": "245.00",
            },
        ]
    )
