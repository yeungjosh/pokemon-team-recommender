"""Tests for team recommender."""

from src.data.pokedex import Pokedex
from src.data.types import TypeChart
from src.data.usage import UsageStats
from src.search.recommender import TeamRecommender


def test_recommender_initialization():
    """Recommender should initialize with data loaders."""
    dex = Pokedex()
    chart = TypeChart()
    usage = UsageStats()

    recommender = TeamRecommender(dex, chart, usage)

    assert recommender.type_weight == 0.4
    assert recommender.meta_weight == 0.4
    assert recommender.role_weight == 0.2


def test_recommend_returns_results():
    """Recommender should return top K recommendations."""
    dex = Pokedex()
    chart = TypeChart()
    usage = UsageStats()

    recommender = TeamRecommender(dex, chart, usage)

    # Test with a sample team
    input_team = ["Garchomp", "Raging Bolt", "Great Tusk"]

    recommendations = recommender.recommend(input_team, top_k=3, candidate_pool_size=12)

    assert len(recommendations) <= 3  # May be fewer if not enough candidates
    assert all(rec.composite_score >= 0 for rec in recommendations)


def test_recommendations_sorted():
    """Recommendations should be sorted by composite score descending."""
    dex = Pokedex()
    chart = TypeChart()
    usage = UsageStats()

    recommender = TeamRecommender(dex, chart, usage)

    input_team = ["Garchomp", "Raging Bolt", "Great Tusk"]
    recommendations = recommender.recommend(input_team, top_k=5, candidate_pool_size=12)

    # Check sorted order
    for i in range(len(recommendations) - 1):
        assert recommendations[i].composite_score >= recommendations[i + 1].composite_score


def test_score_team():
    """Should calculate all score components for a team."""
    dex = Pokedex()
    chart = TypeChart()
    usage = UsageStats()

    recommender = TeamRecommender(dex, chart, usage)

    input_team = [dex.get("Garchomp"), dex.get("Raging Bolt"), dex.get("Great Tusk")]
    candidate_trio = [dex.get("Rillaboom"), dex.get("Corviknight"), dex.get("Gholdengo")]

    scores = recommender.score_team(input_team, candidate_trio)

    assert "composite_score" in scores
    assert "type_score" in scores
    assert "meta_score" in scores
    assert "role_score" in scores

    # All scores should be 0-1
    assert 0 <= scores["composite_score"] <= 1
    assert 0 <= scores["type_score"] <= 1
    assert 0 <= scores["meta_score"] <= 1
    assert 0 <= scores["role_score"] <= 1


def test_invalid_input():
    """Should raise error for invalid input."""
    dex = Pokedex()
    chart = TypeChart()
    usage = UsageStats()

    recommender = TeamRecommender(dex, chart, usage)

    # Test with wrong number of Pokémon
    try:
        recommender.recommend(["Garchomp", "Raging Bolt"], top_k=3)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "exactly 3" in str(e).lower()

    # Test with non-existent Pokémon
    try:
        recommender.recommend(["Garchomp", "FakeMon", "Great Tusk"], top_k=3)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e).lower()
