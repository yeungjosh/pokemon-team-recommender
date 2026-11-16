"""Tests for MLTeamRecommender (rule-based fallback path, no trained model needed)."""

import pytest

from src.data.pokedex import Pokedex
from src.data.types import TypeChart
from src.data.usage import UsageStats
from src.search.ml_recommender import MLScoredRecommendation, MLTeamRecommender

INPUT_TEAM = ["Garchomp", "Raging Bolt", "Great Tusk"]


@pytest.fixture(scope="module")
def recommender():
    return MLTeamRecommender(Pokedex(), TypeChart(), UsageStats(), use_ml=False)


def test_scored_recommendation_defaults_and_properties(recommender):
    mons = [recommender.pokedex.get(n) for n in ["Garchomp", "Great Tusk", "Raging Bolt"]]
    rec = MLScoredRecommendation(
        trio=mons, ml_score=0.7, type_score=0.5, meta_score=0.6, role_score=0.4
    )
    assert rec.weaknesses_covered == []
    assert rec.threats_handled == []
    assert rec.roles_added == []
    assert rec.pokemon_names == ["Garchomp", "Great Tusk", "Raging Bolt"]
    assert rec.composite_score == 0.7


def test_score_team_uses_weighted_fallback(recommender):
    team = [recommender.pokedex.get(n) for n in INPUT_TEAM]
    trio = [recommender.pokedex.get(n) for n in ["Gholdengo", "Kingambit", "Dragapult"]]
    scores = recommender.score_team(team, trio)
    expected = 0.4 * scores["type_score"] + 0.4 * scores["meta_score"] + 0.2 * scores["role_score"]
    assert scores["ml_score"] == pytest.approx(expected)


def test_recommend_returns_sorted_top_k_excluding_input(recommender):
    recs = recommender.recommend(INPUT_TEAM, top_k=3, candidate_pool_size=8)
    assert len(recs) == 3
    scores = [r.ml_score for r in recs]
    assert scores == sorted(scores, reverse=True)
    for rec in recs:
        assert len(rec.trio) == 3
        assert not set(rec.pokemon_names) & set(INPUT_TEAM)
        assert len(set(rec.pokemon_names)) == 3


def test_recommend_requires_exactly_three_inputs(recommender):
    with pytest.raises(ValueError, match="exactly 3"):
        recommender.recommend(["Garchomp", "Great Tusk"])


def test_recommend_rejects_unknown_pokemon(recommender):
    with pytest.raises(ValueError, match="not found"):
        recommender.recommend(["Garchomp", "Great Tusk", "NotAPokemon"])
