"""
Generate partial teams for evaluation.

Takes complete 6-Pokemon teams and splits them into:
- Input: First 3 Pokemon (what user provides)
- Ground Truth: Last 3 Pokemon (what recommender should suggest)
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple


def generate_partial_teams(
    complete_teams_path: Path,
    output_path: Path
) -> List[Dict]:
    """
    Generate input/ground-truth pairs from complete teams.

    Args:
        complete_teams_path: Path to complete_teams.json
        output_path: Where to save partial_teams.json

    Returns:
        List of partial team test cases
    """
    # Load complete teams
    with open(complete_teams_path, 'r') as f:
        complete_teams = json.load(f)

    partial_teams = []

    for team_data in complete_teams:
        team = team_data["team"]
        assert len(team) == 6, f"Team {team_data['name']} has {len(team)} Pokemon"

        # Split: first 3 = input, last 3 = ground truth
        input_pokemon = team[:3]
        ground_truth = team[3:]

        partial_team = {
            "id": team_data["id"],
            "name": team_data["name"],
            "tier": team_data["tier"],
            "archetype": team_data["archetype"],
            "source": team_data["source"],
            "source_url": team_data["source_url"],
            "input": input_pokemon,
            "ground_truth": ground_truth,
            "complete_team": team
        }

        partial_teams.append(partial_team)

    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(partial_teams, f, indent=2)

    print(f"✅ Generated {len(partial_teams)} partial team test cases")
    print(f"   Saved to: {output_path}")
    print(f"\nExample test case:")
    example = partial_teams[0]
    print(f"  Name: {example['name']}")
    print(f"  Archetype: {example['archetype']}")
    print(f"  Input: {', '.join(example['input'])}")
    print(f"  Ground Truth: {', '.join(example['ground_truth'])}")

    return partial_teams


if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent / "data" / "test_sets"
    complete_teams_file = base_dir / "complete_teams.json"
    output_file = base_dir / "partial_teams.json"

    generate_partial_teams(complete_teams_file, output_file)
