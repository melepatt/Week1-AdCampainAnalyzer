from datetime import date

import pandas as pd

from src.filters import FilterSelection, apply_filters


def _frame():
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]),
            "platform": ["Facebook", "Instagram", "Facebook"],
            "audience": ["Adults", "Adults", "Students"],
            "campaign_goal": ["Sales", "Traffic", "Sales"],
            "campaign_id": ["C1", "C2", "C3"],
        }
    )


def _selection(**overrides):
    values = {
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 1, 3),
        "platforms": ("Facebook", "Instagram"),
        "audiences": ("Adults", "Students"),
        "goals": ("Sales", "Traffic"),
    }
    values.update(overrides)
    return FilterSelection(**values)


def test_date_bounds_are_inclusive_and_input_is_not_mutated():
    source = _frame()
    original = source.copy(deep=True)
    result = apply_filters(source, _selection(start_date=date(2026, 1, 2), end_date=date(2026, 1, 3)))

    assert result["campaign_id"].tolist() == ["C2", "C3"]
    pd.testing.assert_frame_equal(source, original)


def test_platform_selection_uses_or_logic():
    result = apply_filters(_frame(), _selection(platforms=("Facebook", "Instagram")))
    assert set(result["platform"]) == {"Facebook", "Instagram"}


def test_filter_groups_use_and_logic():
    result = apply_filters(
        _frame(),
        _selection(platforms=("Facebook",), audiences=("Students",), goals=("Sales",)),
    )
    assert result["campaign_id"].tolist() == ["C3"]


def test_full_selection_preserves_every_row():
    assert len(apply_filters(_frame(), _selection())) == 3


def test_empty_categorical_selection_returns_no_rows():
    assert apply_filters(_frame(), _selection(platforms=())).empty


def test_non_matching_selection_returns_no_rows():
    assert apply_filters(_frame(), _selection(audiences=("Missing",))).empty
