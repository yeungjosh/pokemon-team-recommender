"""Tests for meta matchup analysis."""

import pytest

from src.data.pokedex import Pokemon
from src.data.types import TypeChart
from src.data.usage import UsageEntry
from src.features.meta import MetaAnalyzer


def make_mon(name, types, speed):
    """Build a minimal synthetic Pokémon with a given speed."""
    return Pokemon(
        name=name,
        types=types,
        base_stats={"hp": 80, "atk": 80, "def": 80, "spa": 80, "spd": 80, "spe": speed},
        learnset=[],
    )


class FakeUsage:
    """Minimal stand-in for UsageStats returning fixed entries."""

    def __init__(self, entries):
        self.entries = entries

    def get_top_k(self, k=15, tier="OU"):
        return self.entries[:k]


def entry(name, pct):
    return UsageEntry(name=name, usage_pct=pct, tier="OU", generation=9, month="2025-01")


@pytest.fixture
def chart():
    return TypeChart()


class _FakeDex:
    def __init__(self, mons):
        self.mons = mons

    def get(self, name):
        return self.mons.get(name)


def test_has_check_by_resistance(chart):
    """A Water-type resists a Fire-type attacker, even if slower."""
    analyzer = MetaAnalyzer(chart, _FakeDex({}), FakeUsage([]))
    threat = make_mon("Threat", ["Fire"], speed=150)
    resister = make_mon("Resister", ["Water"], speed=10)
    assert analyzer.has_check([resister], threat)


def test_has_check_by_speed_and_super_effective(chart):
    """A faster super-effective attacker checks a threat it doesn't resist."""
    analyzer = MetaAnalyzer(chart, _FakeDex({}), FakeUsage([]))
    threat = make_mon("Threat", ["Normal"], speed=50)  # Normal hits Electric neutrally
    fast = make_mon("Fast", ["Fighting"], speed=100)
    slow = make_mon("Slow", ["Fighting"], speed=10)
    # Fighting is super-effective vs Normal; only the faster one counts as a check
    # unless it also resists, which Fighting does not vs Normal.
    assert analyzer.has_check([fast], threat)
    assert not analyzer.has_check([slow], threat)


def test_has_check_empty_team(chart):
    analyzer = MetaAnalyzer(chart, _FakeDex({}), FakeUsage([]))
    assert not analyzer.has_check([], make_mon("Threat", ["Fire"], 100))


def test_meta_coverage_score_empty_usage(chart):
    analyzer = MetaAnalyzer(chart, _FakeDex({}), FakeUsage([]))
    assert analyzer.meta_coverage_score([make_mon("A", ["Water"], 50)]) == 0.0


def test_meta_coverage_score_is_usage_weighted(chart):
    """Checking a 75%-usage threat but not a 25%-usage one scores 0.75."""
    fire = make_mon("FireThreat", ["Fire"], speed=200)
    grass = make_mon("GrassThreat", ["Grass"], speed=200)
    team = [make_mon("Waterer", ["Water"], speed=1)]  # resists Fire, not Grass
    entries = [entry("FireThreat", 75.0), entry("GrassThreat", 25.0)]
    analyzer = MetaAnalyzer(chart, _FakeDex({m.name: m for m in (fire, grass)}), FakeUsage(entries))
    assert analyzer.meta_coverage_score(team) == pytest.approx(0.75)


def test_meta_coverage_skips_unknown_pokemon(chart):
    """Threats missing from the Pokédex are ignored rather than counted."""
    fire = make_mon("FireThreat", ["Fire"], speed=200)
    entries = [entry("Ghost Entry", 90.0), entry("FireThreat", 10.0)]
    analyzer = MetaAnalyzer(chart, _FakeDex({"FireThreat": fire}), FakeUsage(entries))
    team = [make_mon("Waterer", ["Water"], speed=1)]
    assert analyzer.meta_coverage_score(team) == pytest.approx(1.0)
    assert analyzer.get_unchecked_threats(team) == []


def test_get_unchecked_threats_and_handled(chart):
    fire = make_mon("FireThreat", ["Fire"], speed=200)
    grass = make_mon("GrassThreat", ["Grass"], speed=200)
    entries = [entry("FireThreat", 60.0), entry("GrassThreat", 40.0)]
    analyzer = MetaAnalyzer(chart, _FakeDex({m.name: m for m in (fire, grass)}), FakeUsage(entries))

    waterer = make_mon("Waterer", ["Water"], speed=1)  # resists Fire only
    fire_resist_grass = make_mon("Burner", ["Fire"], speed=1)  # resists Grass

    assert analyzer.get_unchecked_threats([waterer]) == ["GrassThreat"]
    handled = analyzer.get_threats_handled([waterer], [waterer, fire_resist_grass])
    assert handled == ["GrassThreat"]
    # Nothing newly handled when the full team adds no coverage
    assert analyzer.get_threats_handled([waterer], [waterer]) == []


def test_top_k_limits_threats_considered(chart):
    fire = make_mon("FireThreat", ["Fire"], speed=200)
    grass = make_mon("GrassThreat", ["Grass"], speed=200)
    entries = [entry("FireThreat", 60.0), entry("GrassThreat", 40.0)]
    analyzer = MetaAnalyzer(chart, _FakeDex({m.name: m for m in (fire, grass)}), FakeUsage(entries))
    team = [make_mon("Waterer", ["Water"], speed=1)]
    assert analyzer.meta_coverage_score(team, top_k=1) == pytest.approx(1.0)
