"""
Build comprehensive test set of competitive Pokemon teams.

This script creates a curated test set of 100+ competitive teams
from various archetypes for evaluation purposes.
"""

import json
from pathlib import Path
from typing import List, Dict

# Test teams curated from competitive knowledge and common archetypes
TEST_TEAMS = [
    # Balance teams (20 teams)
    {
        "name": "Balance Core 1",
        "archetype": "balance",
        "team": ["Garchomp", "Great Tusk", "Raging Bolt", "Rillaboom", "Iron Valiant", "Dragapult"]
    },
    {
        "name": "Balance Core 2",
        "archetype": "balance",
        "team": ["Landorus-Therian", "Toxapex", "Heatran", "Tapu Koko", "Ferrothorn", "Dragapult"]
    },
    {
        "name": "Balance Core 3",
        "archetype": "balance",
        "team": ["Garchomp", "Corviknight", "Toxapex", "Rillaboom", "Heatran", "Tapu Lele"]
    },
    {
        "name": "Balance Core 4",
        "archetype": "balance",
        "team": ["Great Tusk", "Gholdengo", "Corviknight", "Primarina", "Landorus-Therian", "Rillaboom"]
    },
    {
        "name": "Balance Core 5",
        "archetype": "balance",
        "team": ["Dragapult", "Toxapex", "Landorus-Therian", "Rillaboom", "Heatran", "Slowbro"]
    },
    {
        "name": "Balance Core 6",
        "archetype": "balance",
        "team": ["Kingambit", "Great Tusk", "Gholdengo", "Dragapult", "Landorus-Therian", "Toxapex"]
    },
    {
        "name": "Balance Core 7",
        "archetype": "balance",
        "team": ["Raging Bolt", "Corviknight", "Great Tusk", "Iron Valiant", "Landorus-Therian", "Slowking-Galar"]
    },
    {
        "name": "Balance Core 8",
        "archetype": "balance",
        "team": ["Garchomp", "Gliscor", "Gholdengo", "Primarina", "Rillaboom", "Iron Moth"]
    },
    {
        "name": "Balance Core 9",
        "archetype": "balance",
        "team": ["Ting-Lu", "Dragapult", "Heatran", "Landorus-Therian", "Primarina", "Rillaboom"]
    },
    {
        "name": "Balance Core 10",
        "archetype": "balance",
        "team": ["Zapdos", "Garchomp", "Toxapex", "Rillaboom", "Heatran", "Slowking-Galar"]
    },
    {
        "name": "Balance Core 11",
        "archetype": "balance",
        "team": ["Great Tusk", "Dragonite", "Gholdengo", "Landorus-Therian", "Toxapex", "Rillaboom"]
    },
    {
        "name": "Balance Core 12",
        "archetype": "balance",
        "team": ["Iron Valiant", "Corviknight", "Ting-Lu", "Heatran", "Dragapult", "Primarina"]
    },
    {
        "name": "Balance Core 13",
        "archetype": "balance",
        "team": ["Garchomp", "Slowbro", "Rillaboom", "Gholdengo", "Zapdos", "Landorus-Therian"]
    },
    {
        "name": "Balance Core 14",
        "archetype": "balance",
        "team": ["Kingambit", "Great Tusk", "Primarina", "Dragapult", "Landorus-Therian", "Corviknight"]
    },
    {
        "name": "Balance Core 15",
        "archetype": "balance",
        "team": ["Raging Bolt", "Gliscor", "Gholdengo", "Iron Valiant", "Primarina", "Rillaboom"]
    },
    {
        "name": "Balance Core 16",
        "archetype": "balance",
        "team": ["Dragapult", "Toxapex", "Landorus-Therian", "Rillaboom", "Moltres", "Ting-Lu"]
    },
    {
        "name": "Balance Core 17",
        "archetype": "balance",
        "team": ["Great Tusk", "Heatran", "Corviknight", "Primarina", "Kingambit", "Dragonite"]
    },
    {
        "name": "Balance Core 18",
        "archetype": "balance",
        "team": ["Iron Moth", "Ting-Lu", "Landorus-Therian", "Slowbro", "Rillaboom", "Dragapult"]
    },
    {
        "name": "Balance Core 19",
        "archetype": "balance",
        "team": ["Garchomp", "Toxapex", "Gholdengo", "Zapdos", "Rillaboom", "Iron Valiant"]
    },
    {
        "name": "Balance Core 20",
        "archetype": "balance",
        "team": ["Raging Bolt", "Corviknight", "Great Tusk", "Primarina", "Landorus-Therian", "Kingambit"]
    },

    # Hyper Offense teams (20 teams)
    {
        "name": "HO 1",
        "archetype": "hyperoffense",
        "team": ["Dragapult", "Iron Valiant", "Roaring Moon", "Great Tusk", "Gholdengo", "Rillaboom"]
    },
    {
        "name": "HO 2",
        "archetype": "hyperoffense",
        "team": ["Iron Moth", "Dragonite", "Great Tusk", "Kingambit", "Raging Bolt", "Landorus-Therian"]
    },
    {
        "name": "HO 3",
        "archetype": "hyperoffense",
        "team": ["Roaring Moon", "Iron Valiant", "Garchomp", "Rillaboom", "Gholdengo", "Great Tusk"]
    },
    {
        "name": "HO 4",
        "archetype": "hyperoffense",
        "team": ["Dragapult", "Dragonite", "Kingambit", "Iron Moth", "Great Tusk", "Raging Bolt"]
    },
    {
        "name": "HO 5",
        "archetype": "hyperoffense",
        "team": ["Iron Valiant", "Roaring Moon", "Landorus-Therian", "Gholdengo", "Rillaboom", "Great Tusk"]
    },
    {
        "name": "HO 6",
        "archetype": "hyperoffense",
        "team": ["Dragapult", "Garchomp", "Iron Moth", "Kingambit", "Raging Bolt", "Great Tusk"]
    },
    {
        "name": "HO 7",
        "archetype": "hyperoffense",
        "team": ["Roaring Moon", "Dragonite", "Iron Valiant", "Landorus-Therian", "Rillaboom", "Gholdengo"]
    },
    {
        "name": "HO 8",
        "archetype": "hyperoffense",
        "team": ["Iron Moth", "Dragapult", "Great Tusk", "Kingambit", "Garchomp", "Raging Bolt"]
    },
    {
        "name": "HO 9",
        "archetype": "hyperoffense",
        "team": ["Iron Valiant", "Roaring Moon", "Dragonite", "Gholdengo", "Great Tusk", "Rillaboom"]
    },
    {
        "name": "HO 10",
        "archetype": "hyperoffense",
        "team": ["Dragapult", "Landorus-Therian", "Kingambit", "Iron Moth", "Garchomp", "Great Tusk"]
    },
    {
        "name": "HO 11",
        "archetype": "hyperoffense",
        "team": ["Roaring Moon", "Iron Valiant", "Raging Bolt", "Gholdengo", "Dragonite", "Great Tusk"]
    },
    {
        "name": "HO 12",
        "archetype": "hyperoffense",
        "team": ["Iron Moth", "Dragapult", "Kingambit", "Garchomp", "Landorus-Therian", "Rillaboom"]
    },
    {
        "name": "HO 13",
        "archetype": "hyperoffense",
        "team": ["Dragonite", "Iron Valiant", "Roaring Moon", "Great Tusk", "Gholdengo", "Raging Bolt"]
    },
    {
        "name": "HO 14",
        "archetype": "hyperoffense",
        "team": ["Dragapult", "Kingambit", "Iron Moth", "Garchomp", "Landorus-Therian", "Great Tusk"]
    },
    {
        "name": "HO 15",
        "archetype": "hyperoffense",
        "team": ["Roaring Moon", "Dragonite", "Raging Bolt", "Rillaboom", "Iron Valiant", "Gholdengo"]
    },
    {
        "name": "HO 16",
        "archetype": "hyperoffense",
        "team": ["Iron Moth", "Dragapult", "Great Tusk", "Kingambit", "Landorus-Therian", "Garchomp"]
    },
    {
        "name": "HO 17",
        "archetype": "hyperoffense",
        "team": ["Iron Valiant", "Roaring Moon", "Dragonite", "Gholdengo", "Raging Bolt", "Great Tusk"]
    },
    {
        "name": "HO 18",
        "archetype": "hyperoffense",
        "team": ["Dragapult", "Garchomp", "Kingambit", "Iron Moth", "Rillaboom", "Landorus-Therian"]
    },
    {
        "name": "HO 19",
        "archetype": "hyperoffense",
        "team": ["Roaring Moon", "Iron Valiant", "Great Tusk", "Gholdengo", "Dragonite", "Raging Bolt"]
    },
    {
        "name": "HO 20",
        "archetype": "hyperoffense",
        "team": ["Iron Moth", "Dragapult", "Kingambit", "Landorus-Therian", "Garchomp", "Great Tusk"]
    },

    # Stall teams (15 teams)
    {
        "name": "Stall 1",
        "archetype": "stall",
        "team": ["Toxapex", "Corviknight", "Ting-Lu", "Clodsire", "Gliscor", "Alomomola"]
    },
    {
        "name": "Stall 2",
        "archetype": "stall",
        "team": ["Toxapex", "Corviknight", "Clodsire", "Ting-Lu", "Blissey", "Alomomola"]
    },
    {
        "name": "Stall 3",
        "archetype": "stall",
        "team": ["Gliscor", "Corviknight", "Toxapex", "Ting-Lu", "Skeledirge", "Alomomola"]
    },
    {
        "name": "Stall 4",
        "archetype": "stall",
        "team": ["Toxapex", "Corviknight", "Clodsire", "Gliscor", "Dondozo", "Ting-Lu"]
    },
    {
        "name": "Stall 5",
        "archetype": "stall",
        "team": ["Toxapex", "Corviknight", "Ting-Lu", "Alomomola", "Blissey", "Gliscor"]
    },
    {
        "name": "Stall 6",
        "archetype": "stall",
        "team": ["Clodsire", "Corviknight", "Toxapex", "Ting-Lu", "Skeledirge", "Dondozo"]
    },
    {
        "name": "Stall 7",
        "archetype": "stall",
        "team": ["Gliscor", "Corviknight", "Toxapex", "Clodsire", "Alomomola", "Ting-Lu"]
    },
    {
        "name": "Stall 8",
        "archetype": "stall",
        "team": ["Toxapex", "Corviknight", "Ting-Lu", "Blissey", "Clodsire", "Skeledirge"]
    },
    {
        "name": "Stall 9",
        "archetype": "stall",
        "team": ["Gliscor", "Corviknight", "Toxapex", "Dondozo", "Ting-Lu", "Alomomola"]
    },
    {
        "name": "Stall 10",
        "archetype": "stall",
        "team": ["Toxapex", "Corviknight", "Clodsire", "Ting-Lu", "Blissey", "Gliscor"]
    },
    {
        "name": "Stall 11",
        "archetype": "stall",
        "team": ["Toxapex", "Corviknight", "Skeledirge", "Ting-Lu", "Clodsire", "Alomomola"]
    },
    {
        "name": "Stall 12",
        "archetype": "stall",
        "team": ["Gliscor", "Corviknight", "Toxapex", "Ting-Lu", "Dondozo", "Blissey"]
    },
    {
        "name": "Stall 13",
        "archetype": "stall",
        "team": ["Toxapex", "Corviknight", "Clodsire", "Alomomola", "Ting-Lu", "Skeledirge"]
    },
    {
        "name": "Stall 14",
        "archetype": "stall",
        "team": ["Gliscor", "Corviknight", "Toxapex", "Ting-Lu", "Blissey", "Clodsire"]
    },
    {
        "name": "Stall 15",
        "archetype": "stall",
        "team": ["Toxapex", "Corviknight", "Ting-Lu", "Dondozo", "Alomomola", "Gliscor"]
    },

    # Rain teams (15 teams)
    {
        "name": "Rain 1",
        "archetype": "rain",
        "team": ["Pelipper", "Barraskewda", "Rotom-Wash", "Ferrothorn", "Kingambit", "Landorus-Therian"]
    },
    {
        "name": "Rain 2",
        "archetype": "rain",
        "team": ["Pelipper", "Barraskewda", "Ferrothorn", "Kingambit", "Garchomp", "Rotom-Wash"]
    },
    {
        "name": "Rain 3",
        "archetype": "rain",
        "team": ["Pelipper", "Archaludon", "Barraskewda", "Landorus-Therian", "Rotom-Wash", "Great Tusk"]
    },
    {
        "name": "Rain 4",
        "archetype": "rain",
        "team": ["Pelipper", "Barraskewda", "Kingambit", "Ferrothorn", "Landorus-Therian", "Iron Valiant"]
    },
    {
        "name": "Rain 5",
        "archetype": "rain",
        "team": ["Pelipper", "Archaludon", "Rotom-Wash", "Garchomp", "Barraskewda", "Great Tusk"]
    },
    {
        "name": "Rain 6",
        "archetype": "rain",
        "team": ["Pelipper", "Barraskewda", "Ferrothorn", "Landorus-Therian", "Kingambit", "Rotom-Wash"]
    },
    {
        "name": "Rain 7",
        "archetype": "rain",
        "team": ["Pelipper", "Archaludon", "Barraskewda", "Iron Valiant", "Rotom-Wash", "Great Tusk"]
    },
    {
        "name": "Rain 8",
        "archetype": "rain",
        "team": ["Pelipper", "Barraskewda", "Kingambit", "Garchomp", "Ferrothorn", "Landorus-Therian"]
    },
    {
        "name": "Rain 9",
        "archetype": "rain",
        "team": ["Pelipper", "Archaludon", "Rotom-Wash", "Barraskewda", "Great Tusk", "Landorus-Therian"]
    },
    {
        "name": "Rain 10",
        "archetype": "rain",
        "team": ["Pelipper", "Barraskewda", "Ferrothorn", "Kingambit", "Iron Valiant", "Rotom-Wash"]
    },
    {
        "name": "Rain 11",
        "archetype": "rain",
        "team": ["Pelipper", "Archaludon", "Barraskewda", "Landorus-Therian", "Garchomp", "Rotom-Wash"]
    },
    {
        "name": "Rain 12",
        "archetype": "rain",
        "team": ["Pelipper", "Barraskewda", "Kingambit", "Ferrothorn", "Great Tusk", "Rotom-Wash"]
    },
    {
        "name": "Rain 13",
        "archetype": "rain",
        "team": ["Pelipper", "Archaludon", "Barraskewda", "Iron Valiant", "Landorus-Therian", "Rotom-Wash"]
    },
    {
        "name": "Rain 14",
        "archetype": "rain",
        "team": ["Pelipper", "Barraskewda", "Ferrothorn", "Garchomp", "Kingambit", "Rotom-Wash"]
    },
    {
        "name": "Rain 15",
        "archetype": "rain",
        "team": ["Pelipper", "Archaludon", "Rotom-Wash", "Barraskewda", "Landorus-Therian", "Great Tusk"]
    },

    # Sun teams (10 teams)
    {
        "name": "Sun 1",
        "archetype": "sun",
        "team": ["Torkoal", "Walking Wake", "Roaring Moon", "Rillaboom", "Landorus-Therian", "Iron Moth"]
    },
    {
        "name": "Sun 2",
        "archetype": "sun",
        "team": ["Torkoal", "Walking Wake", "Iron Moth", "Landorus-Therian", "Great Tusk", "Roaring Moon"]
    },
    {
        "name": "Sun 3",
        "archetype": "sun",
        "team": ["Torkoal", "Walking Wake", "Rillaboom", "Iron Moth", "Landorus-Therian", "Garchomp"]
    },
    {
        "name": "Sun 4",
        "archetype": "sun",
        "team": ["Torkoal", "Walking Wake", "Roaring Moon", "Great Tusk", "Iron Moth", "Rillaboom"]
    },
    {
        "name": "Sun 5",
        "archetype": "sun",
        "team": ["Torkoal", "Walking Wake", "Landorus-Therian", "Iron Moth", "Garchomp", "Roaring Moon"]
    },
    {
        "name": "Sun 6",
        "archetype": "sun",
        "team": ["Torkoal", "Walking Wake", "Rillaboom", "Great Tusk", "Iron Moth", "Landorus-Therian"]
    },
    {
        "name": "Sun 7",
        "archetype": "sun",
        "team": ["Torkoal", "Walking Wake", "Iron Moth", "Roaring Moon", "Garchomp", "Rillaboom"]
    },
    {
        "name": "Sun 8",
        "archetype": "sun",
        "team": ["Torkoal", "Walking Wake", "Landorus-Therian", "Great Tusk", "Iron Moth", "Roaring Moon"]
    },
    {
        "name": "Sun 9",
        "archetype": "sun",
        "team": ["Torkoal", "Walking Wake", "Rillaboom", "Iron Moth", "Garchomp", "Landorus-Therian"]
    },
    {
        "name": "Sun 10",
        "archetype": "sun",
        "team": ["Torkoal", "Walking Wake", "Roaring Moon", "Iron Moth", "Great Tusk", "Landorus-Therian"]
    },

    # Bulky Offense teams (15 teams)
    {
        "name": "Bulky Offense 1",
        "archetype": "bulky-offense",
        "team": ["Landorus-Therian", "Garchomp", "Rillaboom", "Dragapult", "Corviknight", "Heatran"]
    },
    {
        "name": "Bulky Offense 2",
        "archetype": "bulky-offense",
        "team": ["Great Tusk", "Gholdengo", "Corviknight", "Dragapult", "Landorus-Therian", "Primarina"]
    },
    {
        "name": "Bulky Offense 3",
        "archetype": "bulky-offense",
        "team": ["Garchomp", "Rillaboom", "Slowbro", "Dragapult", "Heatran", "Landorus-Therian"]
    },
    {
        "name": "Bulky Offense 4",
        "archetype": "bulky-offense",
        "team": ["Great Tusk", "Kingambit", "Corviknight", "Dragapult", "Primarina", "Landorus-Therian"]
    },
    {
        "name": "Bulky Offense 5",
        "archetype": "bulky-offense",
        "team": ["Garchomp", "Gholdengo", "Slowbro", "Dragapult", "Rillaboom", "Heatran"]
    },
    {
        "name": "Bulky Offense 6",
        "archetype": "bulky-offense",
        "team": ["Landorus-Therian", "Great Tusk", "Corviknight", "Iron Valiant", "Primarina", "Gholdengo"]
    },
    {
        "name": "Bulky Offense 7",
        "archetype": "bulky-offense",
        "team": ["Garchomp", "Rillaboom", "Slowbro", "Dragapult", "Landorus-Therian", "Kingambit"]
    },
    {
        "name": "Bulky Offense 8",
        "archetype": "bulky-offense",
        "team": ["Great Tusk", "Gholdengo", "Corviknight", "Dragapult", "Heatran", "Landorus-Therian"]
    },
    {
        "name": "Bulky Offense 9",
        "archetype": "bulky-offense",
        "team": ["Garchomp", "Rillaboom", "Slowbro", "Iron Valiant", "Primarina", "Landorus-Therian"]
    },
    {
        "name": "Bulky Offense 10",
        "archetype": "bulky-offense",
        "team": ["Great Tusk", "Kingambit", "Corviknight", "Dragapult", "Gholdengo", "Landorus-Therian"]
    },
    {
        "name": "Bulky Offense 11",
        "archetype": "bulky-offense",
        "team": ["Garchomp", "Rillaboom", "Heatran", "Dragapult", "Slowbro", "Landorus-Therian"]
    },
    {
        "name": "Bulky Offense 12",
        "archetype": "bulky-offense",
        "team": ["Great Tusk", "Gholdengo", "Corviknight", "Iron Valiant", "Primarina", "Landorus-Therian"]
    },
    {
        "name": "Bulky Offense 13",
        "archetype": "bulky-offense",
        "team": ["Garchomp", "Kingambit", "Slowbro", "Dragapult", "Rillaboom", "Landorus-Therian"]
    },
    {
        "name": "Bulky Offense 14",
        "archetype": "bulky-offense",
        "team": ["Great Tusk", "Gholdengo", "Corviknight", "Dragapult", "Heatran", "Primarina"]
    },
    {
        "name": "Bulky Offense 15",
        "archetype": "bulky-offense",
        "team": ["Garchomp", "Rillaboom", "Slowbro", "Iron Valiant", "Landorus-Therian", "Gholdengo"]
    },

    # Screens teams (10 teams)
    {
        "name": "Screens 1",
        "archetype": "screens",
        "team": ["Grimmsnarl", "Dragonite", "Iron Valiant", "Roaring Moon", "Kingambit", "Great Tusk"]
    },
    {
        "name": "Screens 2",
        "archetype": "screens",
        "team": ["Grimmsnarl", "Dragapult", "Iron Valiant", "Garchomp", "Kingambit", "Landorus-Therian"]
    },
    {
        "name": "Screens 3",
        "archetype": "screens",
        "team": ["Grimmsnarl", "Dragonite", "Roaring Moon", "Iron Moth", "Great Tusk", "Kingambit"]
    },
    {
        "name": "Screens 4",
        "archetype": "screens",
        "team": ["Grimmsnarl", "Dragapult", "Iron Valiant", "Garchomp", "Roaring Moon", "Great Tusk"]
    },
    {
        "name": "Screens 5",
        "archetype": "screens",
        "team": ["Grimmsnarl", "Dragonite", "Iron Moth", "Kingambit", "Landorus-Therian", "Iron Valiant"]
    },
    {
        "name": "Screens 6",
        "archetype": "screens",
        "team": ["Grimmsnarl", "Dragapult", "Roaring Moon", "Great Tusk", "Kingambit", "Garchomp"]
    },
    {
        "name": "Screens 7",
        "archetype": "screens",
        "team": ["Grimmsnarl", "Dragonite", "Iron Valiant", "Iron Moth", "Roaring Moon", "Great Tusk"]
    },
    {
        "name": "Screens 8",
        "archetype": "screens",
        "team": ["Grimmsnarl", "Dragapult", "Garchomp", "Kingambit", "Landorus-Therian", "Iron Valiant"]
    },
    {
        "name": "Screens 9",
        "archetype": "screens",
        "team": ["Grimmsnarl", "Dragonite", "Roaring Moon", "Great Tusk", "Iron Moth", "Kingambit"]
    },
    {
        "name": "Screens 10",
        "archetype": "screens",
        "team": ["Grimmsnarl", "Dragapult", "Iron Valiant", "Garchomp", "Roaring Moon", "Landorus-Therian"]
    },
]


def build_test_set(output_path: Path) -> List[Dict]:
    """Build complete test set with metadata."""
    complete_teams = []

    for idx, team_data in enumerate(TEST_TEAMS, start=1):
        team = {
            "id": idx,
            "name": team_data["name"],
            "tier": "gen9ou",
            "archetype": team_data["archetype"],
            "source": "Curated",
            "source_url": "",
            "team": team_data["team"]
        }

        # Validate team has 6 Pokemon
        assert len(team["team"]) == 6, f"Team {team['name']} has {len(team['team'])} Pokemon, expected 6"

        complete_teams.append(team)

    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(complete_teams, f, indent=2)

    print(f"✅ Created test set with {len(complete_teams)} teams")
    print(f"   Saved to: {output_path}")

    # Print archetype distribution
    archetype_counts = {}
    for team in complete_teams:
        arch = team["archetype"]
        archetype_counts[arch] = archetype_counts.get(arch, 0) + 1

    print("\nArchetype distribution:")
    for arch, count in sorted(archetype_counts.items()):
        print(f"  {arch}: {count} teams")

    return complete_teams


if __name__ == "__main__":
    output_file = Path(__file__).parent.parent / "data" / "test_sets" / "complete_teams.json"
    build_test_set(output_file)
