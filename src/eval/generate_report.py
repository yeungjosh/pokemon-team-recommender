"""Generate comprehensive evaluation reports."""

import json
from pathlib import Path
from typing import Dict, List, Optional
import argparse
from datetime import datetime


def load_evaluation_results(results_path: Path) -> dict:
    """Load evaluation results from JSON file."""
    with open(results_path, 'r') as f:
        return json.load(f)


def generate_markdown_report(
    results: dict,
    ablations: Optional[dict] = None,
    title: str = "Pokemon Team Recommender Evaluation Report"
) -> str:
    """
    Generate comprehensive Markdown evaluation report.

    Args:
        results: Evaluation results from run_evaluation.py
        ablations: Optional ablation study results from run_ablations.py
        title: Report title

    Returns:
        Markdown-formatted report
    """
    lines = [f"# {title}\n"]
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

    # Configuration
    config = results.get("config", {})
    lines.append("## Configuration\n")
    lines.append("| Parameter | Value |")
    lines.append("|-----------|-------|")
    for key, value in config.items():
        lines.append(f"| {key} | {value} |")
    lines.append("")

    # Overall metrics
    metrics = results["aggregated_metrics"]
    lines.append("## Overall Performance\n")
    lines.append(f"**Test Cases:** {metrics['n_test_cases']}\n")

    lines.append("### Primary Metrics\n")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Mean Reciprocal Rank (MRR) | {metrics['avg_mrr']:.3f} |")

    for k in sorted(metrics['avg_recall'].keys()):
        lines.append(f"| Recall@{k} | {metrics['avg_recall'][k]:.3f} |")
        lines.append(f"| NDCG@{k} | {metrics['avg_ndcg'][k]:.3f} |")
        lines.append(f"| Precision@{k} | {metrics['avg_precision'][k]:.3f} |")
        lines.append(f"| Exact Match@{k} | {metrics['avg_exact_match'][k]:.3f} |")
    lines.append("")

    # Performance by archetype
    individual_results = results.get("individual_results", [])
    if individual_results:
        lines.append("## Performance by Archetype\n")
        archetype_metrics = compute_archetype_metrics(individual_results)

        lines.append("| Archetype | Count | Recall@3 | MRR | NDCG@3 | Avg Time (ms) |")
        lines.append("|-----------|-------|----------|-----|--------|---------------|")

        for archetype, arch_metrics in sorted(archetype_metrics.items()):
            lines.append(
                f"| {archetype:15} | "
                f"{arch_metrics['count']:5} | "
                f"{arch_metrics['recall_3']:.3f} | "
                f"{arch_metrics['mrr']:.3f} | "
                f"{arch_metrics['ndcg_3']:.3f} | "
                f"{arch_metrics['avg_time']:.2f} |"
            )
        lines.append("")

    # Top failures
    if individual_results:
        lines.append("## Challenging Test Cases\n")
        lines.append("*Test cases with lowest Recall@3*\n")

        # Sort by Recall@3 ascending
        sorted_results = sorted(
            individual_results,
            key=lambda r: r['metrics']['recall'][3]
        )

        lines.append("| ID | Name | Archetype | Recall@3 | MRR | Ground Truth |")
        lines.append("|----|------|-----------|----------|-----|--------------|")

        for result in sorted_results[:10]:
            lines.append(
                f"| {result['test_case_id']:3} | "
                f"{result['test_case_name']:20} | "
                f"{result['archetype']:10} | "
                f"{result['metrics']['recall'][3]:.3f} | "
                f"{result['metrics']['mrr']:.3f} | "
                f"{', '.join(result['ground_truth'][:2])}... |"
            )
        lines.append("")

    # Ablation studies (if provided)
    if ablations:
        lines.append("## Ablation Study Results\n")
        lines.append("*Measuring individual component contributions*\n")

        lines.append("| Configuration | Type | Meta | Role | Recall@3 | MRR | NDCG@3 |")
        lines.append("|---------------|------|------|------|----------|-----|--------|")

        config_weights = {
            "baseline": (0.4, 0.4, 0.2),
            "type_only": (1.0, 0.0, 0.0),
            "meta_only": (0.0, 1.0, 0.0),
            "role_only": (0.0, 0.0, 1.0),
            "type_meta": (0.5, 0.5, 0.0),
            "type_role": (0.5, 0.0, 0.5),
            "meta_role": (0.0, 0.5, 0.5),
            "equal_weights": (0.33, 0.33, 0.34),
        }

        for config_name, (t, m, r) in config_weights.items():
            if config_name in ablations:
                abl = ablations[config_name]
                lines.append(
                    f"| {config_name:15} | "
                    f"{t:.2f} | {m:.2f} | {r:.2f} | "
                    f"{abl['avg_recall']['3']:.3f} | "
                    f"{abl['avg_mrr']:.3f} | "
                    f"{abl['avg_ndcg']['3']:.3f} |"
                )
        lines.append("")

        # Best configurations
        lines.append("### Key Findings\n")
        best_recall = max(ablations.items(), key=lambda x: x[1]['avg_recall']['3'])
        best_mrr = max(ablations.items(), key=lambda x: x[1]['avg_mrr'])

        lines.append(f"- **Best Recall@3**: {best_recall[0]} ({best_recall[1]['avg_recall']['3']:.3f})")
        lines.append(f"- **Best MRR**: {best_mrr[0]} ({best_mrr[1]['avg_mrr']:.3f})")
        lines.append("")

    # Performance targets
    if individual_results:
        avg_time = sum(r['prediction_time_ms'] for r in individual_results) / len(individual_results)
        lines.append("## Performance Targets\n")
        lines.append(f"- **Avg prediction time**: {avg_time:.2f}ms")

        target_local = 2000  # 2s
        target_spaces = 4000  # 4s

        if avg_time < target_local:
            lines.append(f"- ✅ Meets local target (<{target_local}ms)")
        else:
            lines.append(f"- ❌ Exceeds local target ({avg_time:.2f}ms > {target_local}ms)")

        lines.append("")

    # Recommendations
    lines.append("## Recommendations\n")

    if metrics['avg_recall'][3] < 0.3:
        lines.append("- ⚠️ Low Recall@3 suggests difficulty finding correct Pokemon in top results")
        lines.append("- Consider: Increasing candidate pool size or refining scoring weights")

    if metrics['avg_mrr'] < 0.4:
        lines.append("- ⚠️ Low MRR indicates correct Pokemon rank poorly")
        lines.append("- Consider: Improving ranking quality through better feature weights")

    if ablations:
        baseline_recall = ablations.get('baseline', {}).get('avg_recall', {}).get('3', 0)
        type_only_recall = ablations.get('type_only', {}).get('avg_recall', {}).get('3', 0)

        if type_only_recall > baseline_recall * 1.1:
            lines.append("- 💡 Type coverage appears more important than baseline weights suggest")
            lines.append("- Consider: Increasing type weight (α)")

    lines.append("")

    return "\n".join(lines)


def compute_archetype_metrics(individual_results: List[dict]) -> Dict[str, dict]:
    """Compute aggregated metrics by archetype."""
    archetype_data = {}

    for result in individual_results:
        archetype = result['archetype']

        if archetype not in archetype_data:
            archetype_data[archetype] = {
                'count': 0,
                'recall_3_sum': 0,
                'mrr_sum': 0,
                'ndcg_3_sum': 0,
                'time_sum': 0,
            }

        data = archetype_data[archetype]
        data['count'] += 1
        data['recall_3_sum'] += result['metrics']['recall'][3]
        data['mrr_sum'] += result['metrics']['mrr']
        data['ndcg_3_sum'] += result['metrics']['ndcg'][3]
        data['time_sum'] += result['prediction_time_ms']

    # Compute averages
    archetype_metrics = {}
    for archetype, data in archetype_data.items():
        count = data['count']
        archetype_metrics[archetype] = {
            'count': count,
            'recall_3': data['recall_3_sum'] / count,
            'mrr': data['mrr_sum'] / count,
            'ndcg_3': data['ndcg_3_sum'] / count,
            'avg_time': data['time_sum'] / count,
        }

    return archetype_metrics


def main():
    """CLI entry point for generating reports."""
    parser = argparse.ArgumentParser(description="Generate evaluation report")
    parser.add_argument(
        "--results",
        type=Path,
        required=True,
        help="Path to evaluation results JSON"
    )
    parser.add_argument(
        "--ablations",
        type=Path,
        help="Optional path to ablation results JSON"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/evaluation_report.md"),
        help="Path to save report"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="Pokemon Team Recommender Evaluation Report",
        help="Report title"
    )

    args = parser.parse_args()

    # Load results
    print(f"Loading evaluation results from {args.results}...")
    results = load_evaluation_results(args.results)

    ablations = None
    if args.ablations and args.ablations.exists():
        print(f"Loading ablation results from {args.ablations}...")
        ablations = load_evaluation_results(args.ablations)

    # Generate report
    print("Generating report...")
    report = generate_markdown_report(results, ablations, args.title)

    # Save report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        f.write(report)

    print(f"\n✅ Report saved to: {args.output}")


if __name__ == "__main__":
    main()
