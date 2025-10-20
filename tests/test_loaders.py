from __future__ import annotations

from src.data import loaders


def test_load_type_chart_contains_fire():
    chart = loaders.load_type_chart()
    assert "fire" in chart
    assert chart["fire"]["grass"] == 2.0


def test_load_usage_has_great_tusk():
    usage = loaders.load_usage()
    names = {row["name"] for row in usage}
    assert "Great Tusk" in names
