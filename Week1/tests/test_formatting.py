import math

import pytest

from src.formatting import format_count, format_currency, format_multiplier, format_percent


def test_formatters_show_expected_units():
    assert format_currency(12450.75) == "$12,450.75"
    assert format_count(2418) == "2,418"
    assert format_percent(182.74) == "182.7%"
    assert format_multiplier(2.834) == "2.83×"


@pytest.mark.parametrize("value", [None, math.nan, math.inf, -math.inf])
def test_formatters_show_na_for_missing_or_non_finite_values(value):
    assert format_currency(value) == "N/A"
    assert format_count(value) == "N/A"
    assert format_percent(value) == "N/A"
    assert format_multiplier(value) == "N/A"
