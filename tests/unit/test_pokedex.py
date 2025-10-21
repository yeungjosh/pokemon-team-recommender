"""Tests for Pokédex data loading."""

from src.data.pokedex import Pokedex


def test_pokedex_loads():
    """Pokédex should load without errors."""
    dex = Pokedex()
    assert len(dex.all_names()) > 0


def test_get_pokemon():
    """Should be able to get Pokémon by name."""
    dex = Pokedex()
    garchomp = dex.get("Garchomp")

    assert garchomp is not None
    assert garchomp.name == "Garchomp"
    assert garchomp.types == ["Dragon", "Ground"]
    assert garchomp.speed == 102


def test_pokemon_learnset():
    """Pokémon should have learnset data."""
    dex = Pokedex()
    garchomp = dex.get("Garchomp")

    assert garchomp.can_learn("Stealth Rock")
    assert garchomp.can_learn("Earthquake")
    assert not garchomp.can_learn("Flamethrower")


def test_filter_by_type():
    """Should be able to filter Pokémon by type."""
    dex = Pokedex()
    dragons = dex.filter_by_type("Dragon")

    dragon_names = [mon.name for mon in dragons]
    assert "Garchomp" in dragon_names
    assert "Dragapult" in dragon_names
    assert "Rillaboom" not in dragon_names  # Not a Dragon type


def test_filter_by_move():
    """Should be able to filter Pokémon by move."""
    dex = Pokedex()
    hazard_setters = dex.filter_by_move("Stealth Rock")

    setter_names = [mon.name for mon in hazard_setters]
    assert "Garchomp" in setter_names
    assert "Gliscor" in setter_names
    assert "Rillaboom" not in setter_names  # Can't learn Stealth Rock
