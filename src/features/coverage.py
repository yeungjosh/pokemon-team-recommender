"""Type coverage analysis for Pokémon teams."""

from typing import List
from src.data.pokedex import Pokemon
from src.data.types import TypeChart


class CoverageAnalyzer:
    """Analyze offensive and defensive type coverage for teams."""

    def __init__(self, type_chart: TypeChart):
        self.type_chart = type_chart

    def offensive_coverage_score(self, team: List[Pokemon]) -> float:
        """
        Calculate offensive type coverage (0-1).

        Score = (number of defending types team can hit super-effectively) / 18

        A defending type is "covered" if at least one team member has STAB
        super-effective against it.
        """
        covered_types = set()

        # For each team member, check which types they hit super-effectively with STAB
        for mon in team:
            for mon_type in mon.types:
                # Check all defending types
                for def_type in self.type_chart.types:
                    effectiveness = self.type_chart.get_effectiveness(mon_type, def_type)
                    if effectiveness > 1.0:  # Super-effective (2x)
                        covered_types.add(def_type)

        return len(covered_types) / 18.0

    def defensive_coverage_score(self, team: List[Pokemon]) -> float:
        """
        Calculate defensive type coverage (0-1).

        For each attacking type, check if team has multiple weaknesses
        and no resists/immunities. Penalize uncovered weaknesses.

        Score = 1 - (penalty / 18)
        """
        penalty = 0

        for atk_type in self.type_chart.types:
            weak_count = 0
            resist_count = 0

            for mon in team:
                effectiveness = self.type_chart.get_matchup(atk_type, mon.types)

                if effectiveness > 1.0:
                    weak_count += 1
                elif effectiveness < 1.0:
                    resist_count += 1

            # Penalize if 2+ weaknesses and 0 resists/immunities
            if weak_count >= 2 and resist_count == 0:
                penalty += 1

        return 1.0 - (penalty / 18.0)

    def type_coverage_score(
        self, team: List[Pokemon], offensive_weight: float = 0.6, defensive_weight: float = 0.4
    ) -> float:
        """
        Calculate combined type coverage score.

        Default weights: 60% offensive, 40% defensive
        """
        offensive = self.offensive_coverage_score(team)
        defensive = self.defensive_coverage_score(team)

        return offensive_weight * offensive + defensive_weight * defensive

    def get_team_weaknesses(self, team: List[Pokemon]) -> dict:
        """Get all attacking types and how many team members are weak to each."""
        weakness_counts = {}

        for atk_type in self.type_chart.types:
            weak_count = sum(
                1
                for mon in team
                if self.type_chart.get_matchup(atk_type, mon.types) > 1.0
            )
            if weak_count > 0:
                weakness_counts[atk_type] = weak_count

        return weakness_counts

    def get_team_resistances(self, team: List[Pokemon]) -> dict:
        """Get all attacking types and how many team members resist each."""
        resistance_counts = {}

        for atk_type in self.type_chart.types:
            resist_count = sum(
                1
                for mon in team
                if self.type_chart.get_matchup(atk_type, mon.types) < 1.0
            )
            if resist_count > 0:
                resistance_counts[atk_type] = resist_count

        return resistance_counts
