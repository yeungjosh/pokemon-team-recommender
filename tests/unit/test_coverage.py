"""Tests for type coverage analysis."""

from src.data.pokedex import Pokedex
from src.data.types import TypeChart
from src.features.coverage import CoverageAnalyzer


def test_offensive_coverage():
    """Team with diverse types should have better offensive coverage."""
    dex = Pokedex()
    chart = TypeChart()
    analyzer = CoverageAnalyzer(chart)

    # Diverse team
    diverse_team = [
        dex.get("Garchomp"),  # Dragon/Ground
        dex.get("Rillaboom"),  # Grass
        dex.get("Gholdengo"),  # Steel/Ghost
    ]

    # Mono-type team
    mono_team = [
        dex.get("Dragapult"),  # Dragon/Ghost
        dex.get("Kyurem"),  # Dragon/Ice
        dex.get("Raging Bolt"),  # Electric/Dragon
    ]

    diverse_score = analyzer.offensive_coverage_score(diverse_team)
    mono_score = analyzer.offensive_coverage_score(mono_team)

    assert diverse_score > mono_score


def test_defensive_coverage():
    """Team without shared weaknesses should score higher."""
    dex = Pokedex()
    chart = TypeChart()
    analyzer = CoverageAnalyzer(chart)

    # Team with shared Ice weakness
    ice_weak = [
        dex.get("Garchomp"),  # 4x weak to Ice
        dex.get("Landorus-Therian"),  # 4x weak to Ice
        dex.get("Gliscor"),  # 4x weak to Ice
    ]

    # Balanced team
    balanced = [
        dex.get("Gholdengo"),  # Steel/Ghost
        dex.get("Great Tusk"),  # Ground/Fighting
        dex.get("Corviknight"),  # Flying/Steel
    ]

    ice_weak_score = analyzer.defensive_coverage_score(ice_weak)
    balanced_score = analyzer.defensive_coverage_score(balanced)

    assert balanced_score > ice_weak_score


def test_get_team_weaknesses():
    """Should correctly identify shared weaknesses."""
    dex = Pokedex()
    chart = TypeChart()
    analyzer = CoverageAnalyzer(chart)

    team = [
        dex.get("Garchomp"),  # Weak to Ice
        dex.get("Landorus-Therian"),  # Weak to Ice
        dex.get("Gliscor"),  # Weak to Ice
    ]

    weaknesses = analyzer.get_team_weaknesses(team)

    # All three are weak to Ice
    assert weaknesses.get("Ice") == 3
