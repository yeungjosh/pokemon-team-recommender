"""Tests for usage statistics loading."""

from src.data.usage import UsageStats


def test_usage_stats_loads():
    """Usage stats should load without errors."""
    usage = UsageStats()
    assert len(usage.df) > 0


def test_get_usage():
    """Should be able to get usage percentage for a Pokémon."""
    usage = UsageStats()

    dragapult_usage = usage.get_usage("Dragapult")
    assert dragapult_usage > 0
    assert dragapult_usage < 100  # Should be a reasonable percentage

    # Non-existent Pokémon should return 0
    fake_usage = usage.get_usage("FakemonDoesNotExist")
    assert fake_usage == 0.0


def test_get_top_k():
    """Should be able to get top K most-used Pokémon."""
    usage = UsageStats()

    top_5 = usage.get_top_k(k=5, tier="OU")
    assert len(top_5) == 5

    # Should be sorted by usage descending
    for i in range(len(top_5) - 1):
        assert top_5[i].usage_pct >= top_5[i + 1].usage_pct

    # Dragapult should be in top 5 (highest usage in sample data)
    top_names = [entry.name for entry in top_5]
    assert "Dragapult" in top_names


def test_get_all_names():
    """Should be able to get all Pokémon names sorted by usage."""
    usage = UsageStats()

    all_names = usage.get_all_names(tier="OU")
    assert len(all_names) > 0

    # First should be highest usage (Dragapult in sample data)
    assert all_names[0] == "Dragapult"
