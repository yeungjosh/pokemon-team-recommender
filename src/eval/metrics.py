"""Evaluation metrics for team recommendation quality."""

from typing import List, Set
import math


def recall_at_k(ground_truth: List[str], predictions: List[str], k: int) -> float:
    """
    Calculate Recall@K: fraction of ground truth items found in top K predictions.

    Recall@K = |ground_truth ∩ predictions[:k]| / |ground_truth|

    Args:
        ground_truth: List of correct Pokemon names
        predictions: List of predicted Pokemon names (ranked)
        k: Number of top predictions to consider

    Returns:
        Recall score between 0 and 1

    Example:
        >>> recall_at_k(["A", "B", "C"], ["A", "D", "B", "E", "C"], k=3)
        0.667  # Found 2 out of 3 in top 3
    """
    if not ground_truth:
        return 0.0

    gt_set = set(ground_truth)
    pred_set = set(predictions[:k])

    hits = len(gt_set & pred_set)
    return hits / len(gt_set)


def mean_reciprocal_rank(ground_truth: List[str], predictions: List[str]) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR).

    MRR measures how early the first relevant item appears in the ranked list.
    For team recommendations, we average the reciprocal ranks of all ground truth items.

    MRR = (1/|ground_truth|) * Σ(1/rank_i) for each ground truth item found

    Args:
        ground_truth: List of correct Pokemon names
        predictions: List of predicted Pokemon names (ranked)

    Returns:
        MRR score between 0 and 1

    Example:
        >>> mean_reciprocal_rank(["A", "B"], ["C", "A", "D", "B"])
        0.375  # (1/2 + 1/4) / 2 = 0.375
    """
    if not ground_truth:
        return 0.0

    gt_set = set(ground_truth)
    reciprocal_ranks = []

    for i, pred in enumerate(predictions, start=1):
        if pred in gt_set:
            reciprocal_ranks.append(1.0 / i)

    if not reciprocal_ranks:
        return 0.0

    return sum(reciprocal_ranks) / len(ground_truth)


def ndcg_at_k(ground_truth: List[str], predictions: List[str], k: int) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain (NDCG@K).

    NDCG measures ranking quality, giving more weight to correct items at top positions.

    DCG@K = Σ(rel_i / log2(i+1)) for i in 1..k
    IDCG@K = DCG of ideal ranking (all ground truth items first)
    NDCG@K = DCG@K / IDCG@K

    Args:
        ground_truth: List of correct Pokemon names
        predictions: List of predicted Pokemon names (ranked)
        k: Number of top predictions to consider

    Returns:
        NDCG score between 0 and 1

    Example:
        >>> ndcg_at_k(["A", "B", "C"], ["A", "D", "B", "C"], k=4)
        0.934  # Good ranking: A at 1, B at 3, C at 4
    """
    if not ground_truth:
        return 0.0

    gt_set = set(ground_truth)

    # Calculate DCG@K
    dcg = 0.0
    for i, pred in enumerate(predictions[:k], start=1):
        if pred in gt_set:
            relevance = 1.0  # Binary relevance: either relevant (1) or not (0)
            dcg += relevance / math.log2(i + 1)

    # Calculate IDCG@K (ideal ranking: all ground truth items first)
    idcg = 0.0
    for i in range(1, min(len(ground_truth), k) + 1):
        idcg += 1.0 / math.log2(i + 1)

    if idcg == 0.0:
        return 0.0

    return dcg / idcg


def precision_at_k(ground_truth: List[str], predictions: List[str], k: int) -> float:
    """
    Calculate Precision@K: fraction of top K predictions that are correct.

    Precision@K = |ground_truth ∩ predictions[:k]| / k

    Args:
        ground_truth: List of correct Pokemon names
        predictions: List of predicted Pokemon names (ranked)
        k: Number of top predictions to consider

    Returns:
        Precision score between 0 and 1

    Example:
        >>> precision_at_k(["A", "B", "C"], ["A", "D", "B", "E", "C"], k=3)
        0.667  # 2 out of 3 predictions are correct
    """
    if k == 0:
        return 0.0

    gt_set = set(ground_truth)
    pred_set = set(predictions[:k])

    hits = len(gt_set & pred_set)
    return hits / k


def exact_match(ground_truth: List[str], predictions: List[str], k: int) -> float:
    """
    Calculate exact match: 1.0 if all ground truth items are in top K, else 0.0.

    Args:
        ground_truth: List of correct Pokemon names
        predictions: List of predicted Pokemon names (ranked)
        k: Number of top predictions to consider

    Returns:
        1.0 if perfect match, 0.0 otherwise
    """
    gt_set = set(ground_truth)
    pred_set = set(predictions[:k])

    return 1.0 if gt_set.issubset(pred_set) else 0.0


class EvaluationMetrics:
    """Container for all evaluation metrics on a single test case."""

    def __init__(
        self,
        test_case_id: int,
        ground_truth: List[str],
        predictions: List[str],
        k_values: List[int] = None
    ):
        """
        Compute all metrics for a single test case.

        Args:
            test_case_id: Unique identifier for this test case
            ground_truth: List of correct Pokemon names
            predictions: List of predicted Pokemon names (ranked)
            k_values: List of K values to evaluate (default: [3, 5, 10])
        """
        self.test_case_id = test_case_id
        self.ground_truth = ground_truth
        self.predictions = predictions
        self.k_values = k_values or [3, 5, 10]

        # Compute all metrics
        self.mrr = mean_reciprocal_rank(ground_truth, predictions)

        self.recall = {}
        self.precision = {}
        self.ndcg = {}
        self.exact_match = {}

        for k in self.k_values:
            self.recall[k] = recall_at_k(ground_truth, predictions, k)
            self.precision[k] = precision_at_k(ground_truth, predictions, k)
            self.ndcg[k] = ndcg_at_k(ground_truth, predictions, k)
            self.exact_match[k] = exact_match(ground_truth, predictions, k)

    def to_dict(self) -> dict:
        """Convert metrics to dictionary for reporting."""
        return {
            "test_case_id": self.test_case_id,
            "mrr": self.mrr,
            "recall": self.recall,
            "precision": self.precision,
            "ndcg": self.ndcg,
            "exact_match": self.exact_match,
        }

    def __repr__(self) -> str:
        """Human-readable representation."""
        lines = [f"Metrics for test case {self.test_case_id}:"]
        lines.append(f"  MRR: {self.mrr:.3f}")
        for k in self.k_values:
            lines.append(f"  Recall@{k}: {self.recall[k]:.3f}")
            lines.append(f"  NDCG@{k}: {self.ndcg[k]:.3f}")
        return "\n".join(lines)


class AggregatedMetrics:
    """Aggregated metrics across multiple test cases."""

    def __init__(self, individual_metrics: List[EvaluationMetrics]):
        """
        Aggregate metrics from multiple test cases.

        Args:
            individual_metrics: List of EvaluationMetrics objects
        """
        self.n_cases = len(individual_metrics)

        if self.n_cases == 0:
            raise ValueError("Cannot aggregate empty metrics list")

        self.k_values = individual_metrics[0].k_values

        # Average metrics
        self.avg_mrr = sum(m.mrr for m in individual_metrics) / self.n_cases

        self.avg_recall = {}
        self.avg_precision = {}
        self.avg_ndcg = {}
        self.avg_exact_match = {}

        for k in self.k_values:
            self.avg_recall[k] = sum(m.recall[k] for m in individual_metrics) / self.n_cases
            self.avg_precision[k] = sum(m.precision[k] for m in individual_metrics) / self.n_cases
            self.avg_ndcg[k] = sum(m.ndcg[k] for m in individual_metrics) / self.n_cases
            self.avg_exact_match[k] = sum(m.exact_match[k] for m in individual_metrics) / self.n_cases

    def to_dict(self) -> dict:
        """Convert aggregated metrics to dictionary."""
        return {
            "n_test_cases": self.n_cases,
            "avg_mrr": self.avg_mrr,
            "avg_recall": self.avg_recall,
            "avg_precision": self.avg_precision,
            "avg_ndcg": self.avg_ndcg,
            "avg_exact_match": self.avg_exact_match,
        }

    def __repr__(self) -> str:
        """Human-readable representation."""
        lines = [f"Aggregated Metrics ({self.n_cases} test cases):"]
        lines.append(f"  Avg MRR: {self.avg_mrr:.3f}")
        for k in self.k_values:
            lines.append(f"  Avg Recall@{k}: {self.avg_recall[k]:.3f}")
            lines.append(f"  Avg NDCG@{k}: {self.avg_ndcg[k]:.3f}")
            lines.append(f"  Avg Exact Match@{k}: {self.avg_exact_match[k]:.3f}")
        return "\n".join(lines)
