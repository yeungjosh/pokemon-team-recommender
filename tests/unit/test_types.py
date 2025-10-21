"""Tests for type effectiveness data loading."""

from src.data.types import TypeChart


def test_type_chart_loads():
    """Type chart should load without errors."""
    chart = TypeChart()
    assert len(chart.types) == 18


def test_basic_effectiveness():
    """Test basic type matchups."""
    chart = TypeChart()

    # Fire is super-effective against Grass
    assert chart.get_effectiveness("Fire", "Grass") == 2.0

    # Water resists Fire
    assert chart.get_effectiveness("Fire", "Water") == 0.5

    # Normal has no effect on Ghost
    assert chart.get_effectiveness("Normal", "Ghost") == 0.0


def test_dual_type_matchup():
    """Test effectiveness against dual-type Pokémon."""
    chart = TypeChart()

    # Ground vs Garchomp (Dragon/Ground)
    # Ground is neutral vs Dragon (1.0) and neutral vs Ground (1.0)
    # So attacking with Ground = 1.0 * 1.0 = 1.0
    assert chart.get_matchup("Ground", ["Dragon", "Ground"]) == 1.0

    # Ice vs Garchomp (Dragon/Ground)
    # Ice is super-effective vs both Dragon (2.0) and Ground (2.0)
    # So 2.0 * 2.0 = 4.0 (4x weakness)
    assert chart.get_matchup("Ice", ["Dragon", "Ground"]) == 4.0


def test_weaknesses():
    """Test getting weaknesses for a Pokémon."""
    chart = TypeChart()

    # Garchomp (Dragon/Ground) is 4x weak to Ice
    garchomp_types = ["Dragon", "Ground"]
    weaknesses = chart.get_weaknesses(garchomp_types)

    assert "Ice" in weaknesses
    assert "Dragon" in weaknesses  # 2x from Dragon
    assert "Fairy" in weaknesses  # 2x from Fairy


def test_resistances():
    """Test getting resistances for a Pokémon."""
    chart = TypeChart()

    # Steel/Flying (Corviknight) resists many types
    corviknight_types = ["Flying", "Steel"]
    resistances = chart.get_resistances(corviknight_types)

    assert "Bug" in resistances  # 0.25x (resisted by both types)
    assert "Grass" in resistances


def test_immunities():
    """Test getting immunities for a Pokémon."""
    chart = TypeChart()

    # Ghost/Dark (Dragapult) is immune to Normal, Fighting, Psychic
    dragapult_types = ["Dragon", "Ghost"]
    immunities = chart.get_immunities(dragapult_types)

    assert "Normal" in immunities  # Ghost immune to Normal
    assert "Fighting" in immunities  # Ghost immune to Fighting
