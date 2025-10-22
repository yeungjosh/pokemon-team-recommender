"""Run offline evaluation on test sets."""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import argparse

from src.data.pokedex import Pokedex
from src.data.types import TypeChart
from src.data.usage import UsageStats
from src.search.recommender import TeamRecommender
from src.eval.metrics import EvaluationMetrics, AggregatedMetrics


@dataclass
class TestCase:
    """Single test case for evaluation."""
    id: int
    name: str
    archetype: str
    input: List[str]
    ground_truth: List[str]
    complete_team: List[str]


@dataclass
class EvaluationResult:
    """Results for a single test case."""
    test_case_id: int
    test_case_name: str
    archetype: str
    input: List[str]
    ground_truth: List[str]
    predictions: List[str]
    prediction_time_ms: float
    metrics: dict


def load_test_cases(test_set_path: Path) -> List[TestCase]:
    """Load test cases from JSON file."""
    with open(test_set_path, 'r') as f:
        data = json.load(f)

    test_cases = []
    for item in data:
        tc = TestCase(
            id=item["id"],
            name=item["name"],
            archetype=item["archetype"],
            input=item["input"],
            ground_truth=item["ground_truth"],
            complete_team=item["complete_team"]
        )
        test_cases.append(tc)

    return test_cases


def run_evaluation(
    recommender: TeamRecommender,
    test_cases: List[TestCase],
    top_k: int = 10,
    k_values: List[int] = None,
    verbose: bool = True
) -> tuple[List[EvaluationResult], AggregatedMetrics]:
    """
    Run evaluation on all test cases.

    Args:
        recommender: Recommender instance to evaluate
        test_cases: List of test cases
        top_k: Number of recommendations to retrieve
        k_values: K values for metrics (default: [3, 5, 10])
        verbose: Print progress

    Returns:
        Tuple of (individual results, aggregated metrics)
    """
    k_values = k_values or [3, 5, 10]
    results = []
    all_metrics = []

    if verbose:
        print(f"Running evaluation on {len(test_cases)} test cases...")
        print(f"Retrieving top {top_k} recommendations per case")
        print(f"Computing metrics for K = {k_values}\n")

    for i, test_case in enumerate(test_cases, start=1):
        if verbose and i % 10 == 0:
            print(f"Progress: {i}/{len(test_cases)} test cases")

        try:
            # Get recommendations
            start_time = time.time()
            recommendations = recommender.recommend(
                input_names=test_case.input,
                top_k=top_k,
                candidate_pool_size=100
            )
            elapsed_ms = (time.time() - start_time) * 1000

            # Extract predicted Pokemon names (flattened from trios)
            predictions = []
            for rec in recommendations:
                for pokemon in rec.trio:
                    if pokemon.name not in predictions:
                        predictions.append(pokemon.name)

            # Compute metrics
            metrics = EvaluationMetrics(
                test_case_id=test_case.id,
                ground_truth=test_case.ground_truth,
                predictions=predictions,
                k_values=k_values
            )
            all_metrics.append(metrics)

            # Store result
            result = EvaluationResult(
                test_case_id=test_case.id,
                test_case_name=test_case.name,
                archetype=test_case.archetype,
                input=test_case.input,
                ground_truth=test_case.ground_truth,
                predictions=predictions[:top_k],
                prediction_time_ms=elapsed_ms,
                metrics=metrics.to_dict()
            )
            results.append(result)

        except Exception as e:
            print(f"Error on test case {test_case.id} ({test_case.name}): {e}")
            # Create zero metrics for failed case
            metrics = EvaluationMetrics(
                test_case_id=test_case.id,
                ground_truth=test_case.ground_truth,
                predictions=[],
                k_values=k_values
            )
            all_metrics.append(metrics)

    # Aggregate metrics
    aggregated = AggregatedMetrics(all_metrics)

    if verbose:
        print(f"\n{'='*60}")
        print("EVALUATION COMPLETE")
        print(f"{'='*60}")
        print(aggregated)
        print(f"\nAvg prediction time: {sum(r.prediction_time_ms for r in results) / len(results):.2f}ms")

    return results, aggregated


def save_results(
    results: List[EvaluationResult],
    aggregated: AggregatedMetrics,
    output_path: Path,
    config: Optional[dict] = None
):
    """Save evaluation results to JSON file."""
    output = {
        "config": config or {},
        "aggregated_metrics": aggregated.to_dict(),
        "individual_results": [asdict(r) for r in results],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")


def main():
    """CLI entry point for running evaluation."""
    parser = argparse.ArgumentParser(description="Run offline evaluation on test sets")
    parser.add_argument(
        "--test-set",
        type=Path,
        default=Path("data/test_sets/partial_teams.json"),
        help="Path to test set JSON file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/evaluation_results.json"),
        help="Path to save results"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Number of recommendations to retrieve"
    )
    parser.add_argument(
        "--type-weight",
        type=float,
        default=0.4,
        help="Weight for type coverage score"
    )
    parser.add_argument(
        "--meta-weight",
        type=float,
        default=0.4,
        help="Weight for meta coverage score"
    )
    parser.add_argument(
        "--role-weight",
        type=float,
        default=0.2,
        help="Weight for role diversity score"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output"
    )

    args = parser.parse_args()

    # Load data
    print("Loading data...")
    pokedex = Pokedex(Path("data/raw/pokedex.json"))
    type_chart = TypeChart(Path("data/raw/type_chart.json"))
    usage_stats = UsageStats(Path("data/raw/usage_ou.csv"))

    # Initialize recommender
    recommender = TeamRecommender(
        pokedex=pokedex,
        type_chart=type_chart,
        usage_stats=usage_stats,
        type_weight=args.type_weight,
        meta_weight=args.meta_weight,
        role_weight=args.role_weight,
    )

    # Load test cases
    test_cases = load_test_cases(args.test_set)
    print(f"Loaded {len(test_cases)} test cases from {args.test_set}\n")

    # Run evaluation
    results, aggregated = run_evaluation(
        recommender=recommender,
        test_cases=test_cases,
        top_k=args.top_k,
        verbose=not args.quiet
    )

    # Save results
    config = {
        "test_set": str(args.test_set),
        "top_k": args.top_k,
        "type_weight": args.type_weight,
        "meta_weight": args.meta_weight,
        "role_weight": args.role_weight,
    }
    save_results(results, aggregated, args.output, config)


if __name__ == "__main__":
    main()
