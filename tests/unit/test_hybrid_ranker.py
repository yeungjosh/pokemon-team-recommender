"""Tests for HybridRanker: feature extraction, training data, predict guard, save/load."""

import numpy as np
import pytest

from src.data.pokedex import Pokedex
from src.data.types import TypeChart
from src.data.usage import UsageStats
from src.features.coverage import CoverageAnalyzer
from src.features.meta import MetaAnalyzer
from src.ml.hybrid_ranker import HybridRanker

TEAM = ["Garchomp", "Raging Bolt", "Great Tusk", "Gholdengo", "Kingambit", "Dragapult"]


@pytest.fixture(scope="module")
def ctx():
    pokedex, type_chart, usage = Pokedex(), TypeChart(), UsageStats()
    return {
        "pokedex": pokedex,
        "type_chart": type_chart,
        "usage": usage,
        "coverage": CoverageAnalyzer(type_chart),
        "meta": MetaAnalyzer(type_chart, pokedex, usage),
        "team": [pokedex.get(n) for n in TEAM],
    }


def test_extract_features_shape_and_range(ctx):
    feats = HybridRanker().extract_features(ctx["team"], ctx["coverage"], ctx["meta"])
    assert feats.shape == (7,)
    assert np.all(np.isfinite(feats))
    assert np.all(feats >= 0)
    # type_diversity (index 4) is unique types / 18 and so can never exceed 1
    assert feats[4] <= 1.0
    # balance (index 5) is 1 - normalised atk/spa gap, so it lies in [0, 1]
    assert 0.0 <= feats[5] <= 1.0


def test_extract_features_is_deterministic(ctx):
    ranker = HybridRanker()
    a = ranker.extract_features(ctx["team"], ctx["coverage"], ctx["meta"])
    b = ranker.extract_features(ctx["team"], ctx["coverage"], ctx["meta"])
    np.testing.assert_array_equal(a, b)


def test_generate_training_data_shapes_and_target_bounds(ctx):
    X, y = HybridRanker().generate_training_data(
        ctx["pokedex"], ctx["type_chart"], ctx["usage"], n_samples=20
    )
    assert X.shape == (20, 7)
    assert y.shape == (20,)
    assert np.all((y >= 0) & (y <= 1))


def test_generate_training_data_is_seeded(ctx):
    args = (ctx["pokedex"], ctx["type_chart"], ctx["usage"])
    X1, y1 = HybridRanker().generate_training_data(*args, n_samples=10)
    X2, y2 = HybridRanker().generate_training_data(*args, n_samples=10)
    np.testing.assert_array_equal(X1, X2)
    np.testing.assert_array_equal(y1, y2)


def test_predict_before_training_raises(ctx):
    with pytest.raises(ValueError, match="trained"):
        HybridRanker().predict(ctx["team"], ctx["coverage"], ctx["meta"])


def test_train_predict_and_save_load_roundtrip(ctx, tmp_path, capsys):
    ranker = HybridRanker()
    ranker.train(ctx["pokedex"], ctx["type_chart"], ctx["usage"], n_samples=60)
    assert ranker.is_trained
    score = ranker.predict(ctx["team"], ctx["coverage"], ctx["meta"])
    assert 0.0 <= score <= 1.0

    path = tmp_path / "ranker.pkl"
    ranker.save(path)
    assert path.exists()

    loaded = HybridRanker()
    assert not loaded.is_trained
    loaded.load(path)
    assert loaded.is_trained
    assert loaded.predict(ctx["team"], ctx["coverage"], ctx["meta"]) == pytest.approx(score)
