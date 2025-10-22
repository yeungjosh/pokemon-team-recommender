"""ML-powered team recommendation engine.

Hybrid approach: uses rule-based features + learned weights.
"""

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

from src.data.pokedex import Pokedex, Pokemon
from src.data.types import TypeChart
from src.data.usage import UsageStats
from src.features.coverage import CoverageAnalyzer
from src.features.meta import MetaAnalyzer
from src.features.roles import RoleDetector
from src.ml.hybrid_ranker import HybridRanker


@dataclass
class MLScoredRecommendation:
    """A recommended trio with ML-predicted score."""

    trio: list[Pokemon]
    ml_score: float  # ML model prediction
    type_score: float  # Individual component scores for explainability
    meta_score: float
    role_score: float

    # Explanation context (for UI explanations)
    weaknesses_covered: list[str] = None  # Type names: ["Fire", "Ice"]
    threats_handled: list[str] = None  # Pokemon names: ["Garchomp", "Kingambit"]
    roles_added: list[str] = None  # Role names: ["Hazard Control", "Pivot"]

    def __post_init__(self):
        """Initialize empty lists for optional fields."""
        if self.weaknesses_covered is None:
            self.weaknesses_covered = []
        if self.threats_handled is None:
            self.threats_handled = []
        if self.roles_added is None:
            self.roles_added = []

    @property
    def pokemon_names(self) -> list[str]:
        return [mon.name for mon in self.trio]

    @property
    def composite_score(self) -> float:
        """Alias for compatibility with existing UI."""
        return self.ml_score


class MLTeamRecommender:
    """Team recommender powered by hybrid ML model."""

    def __init__(
        self,
        pokedex: Pokedex,
        type_chart: TypeChart,
        usage_stats: UsageStats,
        model_path: Path | None = None,
        use_ml: bool = True,
    ):
        self.pokedex = pokedex
        self.type_chart = type_chart
        self.usage_stats = usage_stats

        # Rule-based scorers (used as feature extractors)
        self.coverage_analyzer = CoverageAnalyzer(type_chart)
        self.meta_analyzer = MetaAnalyzer(type_chart, pokedex, usage_stats)
        self.role_detector = RoleDetector()

        # ML model
        self.use_ml = use_ml
        self.ml_ranker = HybridRanker()

        if use_ml:
            if model_path is None:
                model_path = Path(__file__).parents[2] / "models" / "hybrid_ranker.pkl"

            if model_path.exists():
                self.ml_ranker.load(model_path)
                print(f"✓ Loaded ML model from {model_path}")
            else:
                print(f"⚠️  Model not found at {model_path}")
                print("   Training new model...")
                self.ml_ranker.train(pokedex, type_chart, usage_stats, n_samples=5000)
                model_path.parent.mkdir(exist_ok=True, parents=True)
                self.ml_ranker.save(model_path)

    def score_team(
        self, input_team: list[Pokemon], candidate_trio: list[Pokemon]
    ) -> dict:
        """Score a complete 6-Pokémon team using ML model."""
        full_team = input_team + candidate_trio

        # Get individual component scores for explainability
        type_score = self.coverage_analyzer.type_coverage_score(full_team)
        meta_score = self.meta_analyzer.meta_coverage_score(full_team)
        role_score = self.role_detector.role_diversity_score(full_team)

        if self.use_ml and self.ml_ranker.is_trained:
            # Use ML model to predict final score
            ml_score = self.ml_ranker.predict(full_team, self.coverage_analyzer, self.meta_analyzer)
        else:
            # Fallback to rule-based weighted average
            ml_score = 0.4 * type_score + 0.4 * meta_score + 0.2 * role_score

        return {
            "ml_score": ml_score,
            "type_score": type_score,
            "meta_score": meta_score,
            "role_score": role_score,
        }

    def recommend(
        self,
        input_names: list[str],
        top_k: int = 5,
        candidate_pool_size: int = 100,
    ) -> list[MLScoredRecommendation]:
        """
        Recommend trios to complete the input team.

        Args:
            input_names: List of 3 Pokémon names already on the team
            top_k: Number of recommendations to return
            candidate_pool_size: Size of candidate pool to search

        Returns:
            List of top K scored recommendations
        """
        if len(input_names) != 3:
            raise ValueError(
                f"Input must contain exactly 3 Pokémon (got {len(input_names)})"
            )

        # Validate and get input team
        input_team = []
        for name in input_names:
            mon = self.pokedex.get(name)
            if not mon:
                raise ValueError(f"Pokémon not found: {name}")
            input_team.append(mon)

        # Get candidate pool (top N most used Pokémon, excluding input team)
        input_names_set = set(input_names)
        all_candidates = self.usage_stats.get_all_names(tier="OU")
        candidates = [
            self.pokedex.get(name)
            for name in all_candidates
            if name not in input_names_set
        ][:candidate_pool_size]

        # Generate and score all possible trios
        recommendations = []
        for trio in combinations(candidates, 3):
            trio_list = list(trio)
            full_team = input_team + trio_list

            # Get scores
            scores = self.score_team(input_team, trio_list)

            # Get explanation context
            weaknesses_covered = self.coverage_analyzer.get_weaknesses_covered(
                input_team, full_team
            )
            threats_handled = self.meta_analyzer.get_threats_handled(
                input_team, full_team
            )
            roles_added = self.role_detector.get_roles_added(input_team, full_team)

            rec = MLScoredRecommendation(
                trio=trio_list,
                ml_score=scores["ml_score"],
                type_score=scores["type_score"],
                meta_score=scores["meta_score"],
                role_score=scores["role_score"],
                weaknesses_covered=weaknesses_covered,
                threats_handled=threats_handled,
                roles_added=roles_added,
            )
            recommendations.append(rec)

        # Sort by ML score and return top K
        recommendations.sort(key=lambda x: x.ml_score, reverse=True)
        return recommendations[:top_k]
