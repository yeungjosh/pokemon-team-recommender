"""Team recommendation engine with composite scoring and search."""

from dataclasses import dataclass
from typing import List
from itertools import combinations

from src.data.pokedex import Pokemon, Pokedex
from src.data.types import TypeChart
from src.data.usage import UsageStats
from src.features.coverage import CoverageAnalyzer
from src.features.meta import MetaAnalyzer
from src.features.roles import RoleDetector


@dataclass
class ScoredRecommendation:
    """A recommended trio with scores and explanations."""

    trio: List[Pokemon]
    composite_score: float
    type_score: float
    meta_score: float
    role_score: float

    @property
    def pokemon_names(self) -> List[str]:
        return [mon.name for mon in self.trio]


class TeamRecommender:
    """Recommend Pokémon to complete a team."""

    def __init__(
        self,
        pokedex: Pokedex,
        type_chart: TypeChart,
        usage_stats: UsageStats,
        type_weight: float = 0.4,
        meta_weight: float = 0.4,
        role_weight: float = 0.2,
    ):
        self.pokedex = pokedex
        self.type_chart = type_chart
        self.usage_stats = usage_stats

        self.coverage_analyzer = CoverageAnalyzer(type_chart)
        self.meta_analyzer = MetaAnalyzer(type_chart, pokedex, usage_stats)
        self.role_detector = RoleDetector()

        self.type_weight = type_weight
        self.meta_weight = meta_weight
        self.role_weight = role_weight

    def score_team(self, input_team: List[Pokemon], candidate_trio: List[Pokemon]) -> dict:
        """
        Score a complete 6-Pokémon team.

        Returns:
            Dict with composite_score, type_score, meta_score, role_score
        """
        full_team = input_team + candidate_trio

        type_score = self.coverage_analyzer.type_coverage_score(full_team)
        meta_score = self.meta_analyzer.meta_coverage_score(full_team)
        role_score = self.role_detector.role_diversity_score(full_team)

        composite_score = (
            self.type_weight * type_score
            + self.meta_weight * meta_score
            + self.role_weight * role_score
        )

        return {
            "composite_score": composite_score,
            "type_score": type_score,
            "meta_score": meta_score,
            "role_score": role_score,
        }

    def recommend(
        self, input_names: List[str], top_k: int = 5, candidate_pool_size: int = 100
    ) -> List[ScoredRecommendation]:
        """
        Recommend trios to complete a team.

        Args:
            input_names: List of 3 Pokémon names (user's partial team)
            top_k: Number of recommendations to return
            candidate_pool_size: Size of candidate pool (top N by usage)

        Returns:
            List of ScoredRecommendation objects, sorted by score descending
        """
        # Validate input
        if len(input_names) != 3:
            raise ValueError("Must provide exactly 3 Pokémon")

        input_team = []
        for name in input_names:
            mon = self.pokedex.get(name)
            if mon is None:
                raise ValueError(f"Pokémon not found: {name}")
            input_team.append(mon)

        # Build candidate pool (top N by usage, excluding input)
        all_names = self.usage_stats.get_all_names()
        candidate_names = [name for name in all_names if name not in input_names][
            :candidate_pool_size
        ]

        candidates = [self.pokedex.get(name) for name in candidate_names]
        candidates = [c for c in candidates if c is not None]

        # Score all possible trios
        recommendations = []

        for trio in combinations(candidates, 3):
            scores = self.score_team(input_team, list(trio))

            rec = ScoredRecommendation(
                trio=list(trio),
                composite_score=scores["composite_score"],
                type_score=scores["type_score"],
                meta_score=scores["meta_score"],
                role_score=scores["role_score"],
            )
            recommendations.append(rec)

        # Sort by composite score and return top K
        recommendations.sort(key=lambda r: r.composite_score, reverse=True)
        return recommendations[:top_k]
