"""Tests for role detection."""

from src.data.pokedex import Pokedex
from src.features.roles import RoleDetector


def test_detect_hazard_setter():
    """Pokémon with Stealth Rock should be detected as hazard setter."""
    dex = Pokedex()
    garchomp = dex.get("Garchomp")

    roles = RoleDetector.detect_roles(garchomp)
    assert "hazard_setter" in roles


def test_detect_hazard_removal():
    """Pokémon with Defog/Rapid Spin should be detected as hazard removal."""
    dex = Pokedex()
    corviknight = dex.get("Corviknight")
    great_tusk = dex.get("Great Tusk")

    assert "hazard_removal" in RoleDetector.detect_roles(corviknight)  # Defog
    assert "hazard_removal" in RoleDetector.detect_roles(great_tusk)  # Rapid Spin


def test_detect_pivot():
    """Pokémon with U-turn/Volt Switch should be detected as pivot."""
    dex = Pokedex()
    rillaboom = dex.get("Rillaboom")

    roles = RoleDetector.detect_roles(rillaboom)
    assert "pivot" in roles


def test_detect_speed_control():
    """Fast Pokémon or priority users should be detected as speed control."""
    dex = Pokedex()
    dragapult = dex.get("Dragapult")  # 142 speed
    kingambit = dex.get("Kingambit")  # 50 speed but has Sucker Punch

    assert "speed_control" in RoleDetector.detect_roles(dragapult)  # Fast
    assert "speed_control" in RoleDetector.detect_roles(kingambit)  # Priority


def test_role_diversity_score():
    """Team with more roles should score higher."""
    dex = Pokedex()

    # Team with limited roles
    team1 = [dex.get("Dragapult"), dex.get("Raging Bolt"), dex.get("Kyurem")]

    # Team with diverse roles
    team2 = [
        dex.get("Garchomp"),  # Hazard setter, speed control
        dex.get("Great Tusk"),  # Hazard removal, speed control
        dex.get("Rillaboom"),  # Pivot
    ]

    score1 = RoleDetector.role_diversity_score(team1)
    score2 = RoleDetector.role_diversity_score(team2)

    assert score2 > score1
