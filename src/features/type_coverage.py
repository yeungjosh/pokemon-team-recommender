"""Simplified type coverage heuristics for early prototyping."""

from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, Mapping

TypeChart = Mapping[str, Mapping[str, float]]


def offensive_coverage(team_types: Iterable[str], chart: TypeChart) -> Dict[str, float]:
    """Compute how many attacking types hit each defender for super-effective damage."""

    counts: Counter[str] = Counter()
    for atk in team_types:
        for defender, multiplier in chart.get(atk, {}).items():
            if multiplier >= 2:
                counts[defender] += 1
    return dict(counts)


def defensive_gaps(team_types: Iterable[str], chart: TypeChart) -> Dict[str, int]:
    """Identify defending types that threaten the team (>=2 weaknesses, no resist)."""

    weaknesses: Counter[str] = Counter()
    resistances: Counter[str] = Counter()
    for defender in chart:
        weaknesses[defender] = 0
        resistances[defender] = 0

    for atk in chart:
        for defender, multiplier in chart[atk].items():
            if multiplier > 1:
                weaknesses[defender] += 1
            elif 0 < multiplier < 1:
                resistances[defender] += 1

    danger = {
        defender: count
        for defender, count in weaknesses.items()
        if count >= 2 and resistances[defender] == 0
    }
    return danger


__all__ = ["offensive_coverage", "defensive_gaps"]
