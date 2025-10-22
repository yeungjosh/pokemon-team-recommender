"""Run ablation studies to measure component contributions."""

import json
from pathlib import Path
from typing import List, Dict, Tuple
import argparse

from src.data.pokedex import Pokedex
from src.data.types import TypeChart
from src.data.usage import UsageStats
from src.search.recommender import TeamRecommender
from src.eval.run_evaluation import load_test_cases, run_evaluation, TestCase
from src.eval.metrics import AggregatedMetrics


def run_ablation_studies(
    pokedex: Pokedex,
    type_chart: TypeChart,
    usage_stats: UsageStats,
    test_cases: List[TestCase],
    top_k: int = 10
) -> Dict[str, AggregatedMetrics]:
    """
    Run ablation studies with different weight configurations.

    Tests:
    1. Baseline: α=0.4, β=0.4, γ=0.2
    2. Type-only: α=1.0, β=0.0, γ=0.0
    3. Meta-only: α=0.0, β=1.0, γ=0.0
    4. Role-only: α=0.0, β=0.0, γ=1.0
    5. Type+Meta: α=0.5, β=0.5, γ=0.0
    6. Type+Role: α=0.5, β=0.0, γ=0.5
    7. Meta+Role: α=0.0, β=0.5, γ=0.5
    8. Equal weights: α=0.33, β=0.33, γ=0.34

    Args:
        pokedex: Pokemon database
        type_chart: Type effectiveness chart
        usage_stats: Usage statistics
        test_cases: List of test cases
        top_k: Number of recommendations to retrieve

    Returns:
        Dict mapping config name to aggregated metrics
    """
    configs = {
        "baseline": {"type": 0.4, "meta": 0.4, "role": 0.2},
        "type_only": {"type": 1.0, "meta": 0.0, "role": 0.0},
        "meta_only": {"type": 0.0, "meta": 1.0, "role": 0.0},
        "role_only": {"type": 0.0, "meta": 0.0, "role": 1.0},
        "type_meta": {"type": 0.5, "meta": 0.5, "role": 0.0},
        "type_role": {"type": 0.5, "meta": 0.0, "role": 0.5},
        "meta_role": {"type": 0.0, "meta": 0.5, "role": 0.5},
        "equal_weights": {"type": 0.33, "meta": 0.33, "role": 0.34},
    }

    results = {}

    for name, weights in configs.items():
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print(f"Weights: type={weights['type']:.2f}, meta={weights['meta']:.2f}, role={weights['role']:.2f}")
        print(f"{'='*60}")

        recommender = TeamRecommender(
            pokedex=pokedex,
            type_chart=type_chart,
            usage_stats=usage_stats,
            type_weight=weights['type'],
            meta_weight=weights['meta'],
            role_weight=weights['role'],
        )

        _, aggregated = run_evaluation(
            recommender=recommender,
            test_cases=test_cases,
            top_k=top_k,
            verbose=False
        )

        results[name] = aggregated
        print(f"\nRecall@3: {aggregated.avg_recall[3]:.3f}")
        print(f"MRR: {aggregated.avg_mrr:.3f}")
        print(f"NDCG@3: {aggregated.avg_ndcg[3]:.3f}")

    return results


def compare_ablations(results: Dict[str, AggregatedMetrics]) -> str:
    """
    Generate comparison report for ablation studies.

    Args:
        results: Dict mapping config name to aggregated metrics

    Returns:
        Markdown-formatted comparison report
    """
    lines = ["# Ablation Study Results\n"]

    # Summary table
    lines.append("## Summary Comparison\n")
    lines.append("| Configuration | Recall@3 | Recall@5 | MRR | NDCG@3 | NDCG@5 |")
    lines.append("|--------------|----------|----------|-----|--------|--------|")

    for name, metrics in results.items():
        lines.append(
            f"| {name:20} | "
            f"{metrics.avg_recall[3]:.3f} | "
            f"{metrics.avg_recall[5]:.3f} | "
            f"{metrics.avg_mrr:.3f} | "
            f"{metrics.avg_ndcg[3]:.3f} | "
            f"{metrics.avg_ndcg[5]:.3f} |"
        )

    # Find best configuration for each metric
    lines.append("\n## Best Configurations by Metric\n")

    metrics_to_compare = [
        ("Recall@3", lambda m: m.avg_recall[3]),
        ("Recall@5", lambda m: m.avg_recall[5]),
        ("MRR", lambda m: m.avg_mrr),
        ("NDCG@3", lambda m: m.avg_ndcg[3]),
        ("NDCG@5", lambda m: m.avg_ndcg[5]),
    ]

    for metric_name, metric_fn in metrics_to_compare:
        best_config = max(results.items(), key=lambda x: metric_fn(x[1]))
        lines.append(f"- **{metric_name}**: {best_config[0]} ({metric_fn(best_config[1]):.3f})")

    # Analysis
    lines.append("\n## Analysis\n")
    baseline = results.get("baseline")
    if baseline:
        lines.append(f"Baseline performance (α=0.4, β=0.4, γ=0.2):")
        lines.append(f"- Recall@3: {baseline.avg_recall[3]:.3f}")
        lines.append(f"- MRR: {baseline.avg_mrr:.3f}")
        lines.append(f"- NDCG@3: {baseline.avg_ndcg[3]:.3f}\n")

    # Component contributions
    type_only = results.get("type_only")
    meta_only = results.get("meta_only")
    role_only = results.get("role_only")

    if type_only and meta_only and role_only:
        lines.append("### Individual Component Performance\n")
        lines.append(f"- **Type coverage only**: Recall@3={type_only.avg_recall[3]:.3f}")
        lines.append(f"- **Meta coverage only**: Recall@3={meta_only.avg_recall[3]:.3f}")
        lines.append(f"- **Role diversity only**: Recall@3={role_only.avg_recall[3]:.3f}\n")

    return "\n".join(lines)


def save_ablation_results(
    results: Dict[str, AggregatedMetrics],
    output_path: Path
):
    """Save ablation study results to JSON."""
    output = {}
    for name, metrics in results.items():
        output[name] = metrics.to_dict()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nAblation results saved to: {output_path}")


def main():
    """CLI entry point for running ablation studies."""
    parser = argparse.ArgumentParser(description="Run ablation studies")
    parser.add_argument(
        "--test-set",
        type=Path,
        default=Path("data/test_sets/partial_teams.json"),
        help="Path to test set JSON file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/ablations.json"),
        help="Path to save ablation results"
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("results/ablation_report.md"),
        help="Path to save comparison report"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Number of recommendations to retrieve"
    )

    args = parser.parse_args()

    # Load data
    print("Loading data...")
    pokedex = Pokedex(Path("data/raw/pokedex.json"))
    type_chart = TypeChart(Path("data/raw/type_chart.json"))
    usage_stats = UsageStats(Path("data/raw/usage_ou.csv"))

    # Load test cases
    test_cases = load_test_cases(args.test_set)
    print(f"Loaded {len(test_cases)} test cases from {args.test_set}\n")

    # Run ablation studies
    print("Running ablation studies...")
    results = run_ablation_studies(
        pokedex=pokedex,
        type_chart=type_chart,
        usage_stats=usage_stats,
        test_cases=test_cases,
        top_k=args.top_k
    )

    # Save results
    save_ablation_results(results, args.output)

    # Generate and save report
    report = compare_ablations(results)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with open(args.report, 'w') as f:
        f.write(report)
    print(f"Comparison report saved to: {args.report}")

    print(f"\n{'='*60}")
    print("ABLATION STUDIES COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
