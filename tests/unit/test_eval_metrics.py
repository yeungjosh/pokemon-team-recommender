"""Unit tests for evaluation metrics."""

import pytest
from src.eval.metrics import (
    recall_at_k,
    mean_reciprocal_rank,
    ndcg_at_k,
    precision_at_k,
    exact_match,
    EvaluationMetrics,
    AggregatedMetrics,
)


class TestRecallAtK:
    """Tests for Recall@K metric."""

    def test_perfect_recall(self):
        """All ground truth items found in top K."""
        ground_truth = ["A", "B", "C"]
        predictions = ["A", "B", "C", "D", "E"]
        assert recall_at_k(ground_truth, predictions, k=3) == 1.0

    def test_partial_recall(self):
        """Some ground truth items found in top K."""
        ground_truth = ["A", "B", "C"]
        predictions = ["A", "D", "B", "E", "F"]
        assert recall_at_k(ground_truth, predictions, k=3) == pytest.approx(2/3)

    def test_zero_recall(self):
        """No ground truth items found in top K."""
        ground_truth = ["A", "B", "C"]
        predictions = ["D", "E", "F"]
        assert recall_at_k(ground_truth, predictions, k=3) == 0.0

    def test_recall_improves_with_larger_k(self):
        """Recall should increase or stay same as K increases."""
        ground_truth = ["A", "B", "C"]
        predictions = ["D", "A", "E", "B", "F", "C"]

        r3 = recall_at_k(ground_truth, predictions, k=3)
        r5 = recall_at_k(ground_truth, predictions, k=5)
        r10 = recall_at_k(ground_truth, predictions, k=10)

        assert r3 <= r5 <= r10

    def test_empty_ground_truth(self):
        """Handle empty ground truth list."""
        assert recall_at_k([], ["A", "B", "C"], k=3) == 0.0

    def test_k_larger_than_predictions(self):
        """K larger than prediction list length."""
        ground_truth = ["A", "B"]
        predictions = ["A"]
        assert recall_at_k(ground_truth, predictions, k=10) == 0.5


class TestMeanReciprocalRank:
    """Tests for Mean Reciprocal Rank (MRR)."""

    def test_perfect_ranking(self):
        """All ground truth items at top positions."""
        ground_truth = ["A", "B"]
        predictions = ["A", "B", "C", "D"]
        # MRR = (1/1 + 1/2) / 2 = 0.75
        assert mean_reciprocal_rank(ground_truth, predictions) == 0.75

    def test_late_ranking(self):
        """Ground truth items appear late in ranking."""
        ground_truth = ["A", "B"]
        predictions = ["C", "D", "E", "A", "F", "B"]
        # MRR = (1/4 + 1/6) / 2 = 0.20833...
        assert mean_reciprocal_rank(ground_truth, predictions) == pytest.approx((1/4 + 1/6) / 2)

    def test_no_matches(self):
        """No ground truth items found."""
        ground_truth = ["A", "B"]
        predictions = ["C", "D", "E"]
        assert mean_reciprocal_rank(ground_truth, predictions) == 0.0

    def test_single_ground_truth(self):
        """Single ground truth item at position 2."""
        ground_truth = ["A"]
        predictions = ["B", "A", "C"]
        assert mean_reciprocal_rank(ground_truth, predictions) == 0.5

    def test_empty_ground_truth(self):
        """Handle empty ground truth."""
        assert mean_reciprocal_rank([], ["A", "B"]) == 0.0


class TestNDCGAtK:
    """Tests for Normalized Discounted Cumulative Gain (NDCG@K)."""

    def test_perfect_ranking(self):
        """Perfect ranking (all ground truth at top)."""
        ground_truth = ["A", "B", "C"]
        predictions = ["A", "B", "C", "D", "E"]
        assert ndcg_at_k(ground_truth, predictions, k=3) == 1.0

    def test_suboptimal_ranking(self):
        """Suboptimal ranking with some irrelevant items."""
        ground_truth = ["A", "B", "C"]
        predictions = ["D", "A", "E", "B", "C"]
        # Should be less than perfect but > 0
        score = ndcg_at_k(ground_truth, predictions, k=5)
        assert 0.0 < score < 1.0

    def test_no_matches(self):
        """No ground truth items found."""
        ground_truth = ["A", "B", "C"]
        predictions = ["D", "E", "F"]
        assert ndcg_at_k(ground_truth, predictions, k=3) == 0.0

    def test_partial_match(self):
        """Some matches at different positions."""
        ground_truth = ["A", "B", "C"]
        predictions = ["A", "D", "B", "E"]
        score = ndcg_at_k(ground_truth, predictions, k=4)
        assert 0.0 < score < 1.0

    def test_empty_ground_truth(self):
        """Handle empty ground truth."""
        assert ndcg_at_k([], ["A", "B", "C"], k=3) == 0.0

    def test_monotonicity(self):
        """Better rankings should have higher NDCG."""
        ground_truth = ["A", "B"]

        good_ranking = ["A", "B", "C", "D"]
        ok_ranking = ["A", "C", "B", "D"]
        bad_ranking = ["C", "D", "A", "B"]

        good_score = ndcg_at_k(ground_truth, good_ranking, k=4)
        ok_score = ndcg_at_k(ground_truth, ok_ranking, k=4)
        bad_score = ndcg_at_k(ground_truth, bad_ranking, k=4)

        assert good_score > ok_score > bad_score


class TestPrecisionAtK:
    """Tests for Precision@K metric."""

    def test_perfect_precision(self):
        """All top K predictions are correct."""
        ground_truth = ["A", "B", "C"]
        predictions = ["A", "B", "C", "D", "E"]
        assert precision_at_k(ground_truth, predictions, k=3) == 1.0

    def test_partial_precision(self):
        """Some top K predictions are correct."""
        ground_truth = ["A", "B", "C"]
        predictions = ["A", "D", "B", "E", "F"]
        assert precision_at_k(ground_truth, predictions, k=3) == pytest.approx(2/3)

    def test_zero_precision(self):
        """No top K predictions are correct."""
        ground_truth = ["A", "B", "C"]
        predictions = ["D", "E", "F"]
        assert precision_at_k(ground_truth, predictions, k=3) == 0.0

    def test_k_zero(self):
        """Handle K=0."""
        assert precision_at_k(["A"], ["A", "B"], k=0) == 0.0


class TestExactMatch:
    """Tests for exact match metric."""

    def test_exact_match_success(self):
        """All ground truth found in top K."""
        ground_truth = ["A", "B"]
        predictions = ["A", "B", "C"]
        assert exact_match(ground_truth, predictions, k=3) == 1.0

    def test_exact_match_failure(self):
        """Not all ground truth found."""
        ground_truth = ["A", "B", "C"]
        predictions = ["A", "B", "D"]
        assert exact_match(ground_truth, predictions, k=3) == 0.0

    def test_exact_match_order_independent(self):
        """Order shouldn't matter for exact match."""
        ground_truth = ["A", "B"]
        predictions1 = ["A", "B", "C"]
        predictions2 = ["B", "A", "C"]
        assert exact_match(ground_truth, predictions1, k=3) == exact_match(ground_truth, predictions2, k=3)


class TestEvaluationMetrics:
    """Tests for EvaluationMetrics class."""

    def test_metrics_computation(self):
        """All metrics computed correctly."""
        ground_truth = ["A", "B", "C"]
        predictions = ["A", "D", "B", "E", "C", "F"]

        metrics = EvaluationMetrics(
            test_case_id=1,
            ground_truth=ground_truth,
            predictions=predictions,
            k_values=[3, 5]
        )

        assert metrics.test_case_id == 1
        assert metrics.mrr > 0
        assert 3 in metrics.recall
        assert 5 in metrics.recall
        assert 3 in metrics.ndcg
        assert 5 in metrics.ndcg

    def test_to_dict(self):
        """Convert to dictionary."""
        metrics = EvaluationMetrics(
            test_case_id=1,
            ground_truth=["A", "B"],
            predictions=["A", "C", "B"],
            k_values=[3]
        )

        data = metrics.to_dict()
        assert data["test_case_id"] == 1
        assert "mrr" in data
        assert "recall" in data
        assert "ndcg" in data

    def test_repr(self):
        """String representation works."""
        metrics = EvaluationMetrics(
            test_case_id=1,
            ground_truth=["A", "B"],
            predictions=["A", "C", "B"],
            k_values=[3]
        )
        assert "test case 1" in repr(metrics)
        assert "MRR" in repr(metrics)


class TestAggregatedMetrics:
    """Tests for AggregatedMetrics class."""

    def test_aggregation(self):
        """Aggregate multiple metrics correctly."""
        metrics1 = EvaluationMetrics(1, ["A", "B"], ["A", "B", "C"], k_values=[3])
        metrics2 = EvaluationMetrics(2, ["A", "B"], ["C", "A", "B"], k_values=[3])

        agg = AggregatedMetrics([metrics1, metrics2])

        assert agg.n_cases == 2
        assert 0 < agg.avg_mrr <= 1.0
        assert 0 < agg.avg_recall[3] <= 1.0

    def test_empty_list_raises(self):
        """Cannot aggregate empty list."""
        with pytest.raises(ValueError, match="Cannot aggregate empty"):
            AggregatedMetrics([])

    def test_to_dict(self):
        """Convert to dictionary."""
        metrics1 = EvaluationMetrics(1, ["A"], ["A"], k_values=[3])
        agg = AggregatedMetrics([metrics1])

        data = agg.to_dict()
        assert data["n_test_cases"] == 1
        assert "avg_mrr" in data
        assert "avg_recall" in data

    def test_repr(self):
        """String representation works."""
        metrics1 = EvaluationMetrics(1, ["A"], ["A"], k_values=[3])
        agg = AggregatedMetrics([metrics1])
        assert "1 test cases" in repr(agg)


class TestMetricsInvariants:
    """Property-based tests for metric invariants."""

    def test_recall_bounded(self):
        """Recall should always be between 0 and 1."""
        ground_truth = ["A", "B", "C"]
        predictions = ["D", "A", "E", "B", "F"]

        for k in [1, 3, 5, 10]:
            r = recall_at_k(ground_truth, predictions, k)
            assert 0 <= r <= 1.0

    def test_mrr_bounded(self):
        """MRR should always be between 0 and 1."""
        ground_truth = ["A", "B"]
        predictions = ["C", "D", "A", "B"]

        mrr = mean_reciprocal_rank(ground_truth, predictions)
        assert 0 <= mrr <= 1.0

    def test_ndcg_bounded(self):
        """NDCG should always be between 0 and 1."""
        ground_truth = ["A", "B", "C"]
        predictions = ["D", "B", "A", "C"]

        for k in [1, 3, 5]:
            ndcg = ndcg_at_k(ground_truth, predictions, k)
            assert 0 <= ndcg <= 1.0

    def test_precision_bounded(self):
        """Precision should always be between 0 and 1."""
        ground_truth = ["A", "B"]
        predictions = ["A", "C", "D"]

        for k in [1, 2, 3]:
            p = precision_at_k(ground_truth, predictions, k)
            assert 0 <= p <= 1.0
