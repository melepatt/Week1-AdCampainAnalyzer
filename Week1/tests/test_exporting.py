import pandas as pd

from src.exporting import dataframe_to_csv_bytes


def test_dataframe_to_csv_bytes_is_deterministic_utf8_without_index():
    frame = pd.DataFrame(
        {"campaign_id": ["0012"], "campaign_name": ["Café Launch"], "spend_usd": [12.5]}
    )

    first = dataframe_to_csv_bytes(frame)
    second = dataframe_to_csv_bytes(frame)

    assert first == second
    assert first.decode("utf-8") == "campaign_id,campaign_name,spend_usd\n0012,Café Launch,12.5\n"
    assert not first.decode("utf-8").startswith(",")
