#!/usr/bin/env python3
"""
Script to expand Pokemon dataset from Smogon usage stats and Showdown data.

Fetches top 100 Pokemon from Gen 9 OU and builds complete pokedex.json.
"""

import json
import re
import csv
from pathlib import Path
from typing import Dict, List

# Parse usage stats to get top N Pokemon
def parse_usage_stats(usage_file: Path, top_n: int = 100) -> List[Dict]:
    """Parse Smogon usage stats file."""
    pokemon_list = []

    with open(usage_file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        # Match lines like: | 1    | Great Tusk         | 27.15831% | ...
        match = re.match(r'\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([\d.]+)%', line)
        if match:
            rank = int(match.group(1))
            name = match.group(2).strip()
            usage_pct = float(match.group(3))

            if rank <= top_n:
                pokemon_list.append({
                    'rank': rank,
                    'name': name,
                    'usage_pct': usage_pct
                })

    return pokemon_list


# Pokemon data mapping (from Showdown data)
# For MVP, we'll create a comprehensive dataset with key competitive Pokemon
POKEMON_DATA = {
    "Great Tusk": {
        "types": ["Ground", "Fighting"],
        "baseStats": {"hp": 115, "atk": 131, "def": 131, "spa": 53, "spd": 53, "spe": 87},
        "learnset": ["Rapid Spin", "Earthquake", "Close Combat", "Ice Spinner", "Knock Off", "Stealth Rock", "Stone Edge"]
    },
    "Kingambit": {
        "types": ["Dark", "Steel"],
        "baseStats": {"hp": 100, "atk": 135, "def": 120, "spa": 60, "spd": 85, "spe": 50},
        "learnset": ["Sucker Punch", "Kowtow Cleave", "Iron Head", "Swords Dance", "Low Kick", "Zen Headbutt"]
    },
    "Gholdengo": {
        "types": ["Steel", "Ghost"],
        "baseStats": {"hp": 87, "atk": 60, "def": 95, "spa": 133, "spd": 91, "spe": 84},
        "learnset": ["Make It Rain", "Shadow Ball", "Trick", "Nasty Plot", "Thunderbolt", "Focus Blast"]
    },
    "Dragapult": {
        "types": ["Dragon", "Ghost"],
        "baseStats": {"hp": 88, "atk": 120, "def": 75, "spa": 100, "spd": 75, "spe": 142},
        "learnset": ["Dragon Darts", "U-turn", "Shadow Ball", "Will-O-Wisp", "Hex", "Draco Meteor"]
    },
    "Dragonite": {
        "types": ["Dragon", "Flying"],
        "baseStats": {"hp": 91, "atk": 134, "def": 95, "spa": 100, "spd": 100, "spe": 80},
        "learnset": ["Extreme Speed", "Dragon Dance", "Outrage", "Earthquake", "Ice Beam", "Fire Punch"]
    },
    "Ogerpon-Wellspring": {
        "types": ["Water", "Grass"],
        "baseStats": {"hp": 80, "atk": 120, "def": 84, "spa": 60, "spd": 96, "spe": 110},
        "learnset": ["Ivy Cudgel", "Horn Leech", "U-turn", "Knock Off", "Spiky Shield", "Play Rough"]
    },
    "Hatterene": {
        "types": ["Psychic", "Fairy"],
        "baseStats": {"hp": 57, "atk": 90, "def": 95, "spa": 136, "spd": 103, "spe": 29},
        "learnset": ["Psychic", "Dazzling Gleam", "Trick Room", "Healing Wish", "Mystical Fire", "Calm Mind"]
    },
    "Iron Valiant": {
        "types": ["Fairy", "Fighting"],
        "baseStats": {"hp": 74, "atk": 130, "def": 90, "spa": 120, "spd": 60, "spe": 116},
        "learnset": ["Close Combat", "Moonblast", "Knock Off", "Calm Mind", "Thunderbolt", "Psyshock"]
    },
    "Slowking-Galar": {
        "types": ["Poison", "Psychic"],
        "baseStats": {"hp": 95, "atk": 65, "def": 80, "spa": 110, "spd": 110, "spe": 30},
        "learnset": ["Sludge Bomb", "Psychic", "Future Sight", "Trick Room", "Flamethrower", "Thunder Wave"]
    },
    "Corviknight": {
        "types": ["Flying", "Steel"],
        "baseStats": {"hp": 98, "atk": 87, "def": 105, "spa": 53, "spd": 85, "spe": 67},
        "learnset": ["Defog", "Brave Bird", "U-turn", "Roost", "Iron Defense", "Bulk Up"]
    },
    "Zamazenta": {
        "types": ["Fighting"],
        "baseStats": {"hp": 92, "atk": 130, "def": 115, "spa": 80, "spd": 115, "spe": 138},
        "learnset": ["Close Combat", "Iron Head", "Crunch", "Stone Edge", "Heavy Slam", "Play Rough"]
    },
    "Landorus-Therian": {
        "types": ["Ground", "Flying"],
        "baseStats": {"hp": 89, "atk": 145, "def": 90, "spa": 105, "spd": 80, "spe": 91},
        "learnset": ["Stealth Rock", "Earthquake", "U-turn", "Knock Off", "Stone Edge", "Fly"]
    },
    "Gliscor": {
        "types": ["Ground", "Flying"],
        "baseStats": {"hp": 75, "atk": 95, "def": 125, "spa": 45, "spd": 75, "spe": 95},
        "learnset": ["Stealth Rock", "Earthquake", "U-turn", "Toxic", "Protect", "Knock Off"]
    },
    "Raging Bolt": {
        "types": ["Electric", "Dragon"],
        "baseStats": {"hp": 125, "atk": 73, "def": 91, "spa": 137, "spd": 89, "spe": 75},
        "learnset": ["Thunderclap", "Draco Meteor", "Volt Switch", "Calm Mind", "Thunderbolt", "Dragon Pulse"]
    },
    "Cinderace": {
        "types": ["Fire"],
        "baseStats": {"hp": 80, "atk": 116, "def": 75, "spa": 65, "spd": 75, "spe": 119},
        "learnset": ["Pyro Ball", "U-turn", "High Jump Kick", "Sucker Punch", "Gunk Shot", "Court Change"]
    },
    "Samurott-Hisui": {
        "types": ["Water", "Dark"],
        "baseStats": {"hp": 90, "atk": 108, "def": 80, "spa": 100, "spd": 65, "spe": 85},
        "learnset": ["Ceaseless Edge", "Aqua Cutter", "Knock Off", "Sucker Punch", "Swords Dance", "Sacred Sword"]
    },
    "Ting-Lu": {
        "types": ["Dark", "Ground"],
        "baseStats": {"hp": 155, "atk": 110, "def": 125, "spa": 55, "spd": 80, "spe": 45},
        "learnset": ["Stealth Rock", "Earthquake", "Ruination", "Whirlwind", "Spikes", "Heavy Slam"]
    },
    "Glimmora": {
        "types": ["Rock", "Poison"],
        "baseStats": {"hp": 83, "atk": 55, "def": 90, "spa": 130, "spd": 81, "spe": 86},
        "learnset": ["Stealth Rock", "Power Gem", "Sludge Wave", "Earth Power", "Spikes", "Mortal Spin"]
    },
    "Iron Treads": {
        "types": ["Ground", "Steel"],
        "baseStats": {"hp": 90, "atk": 112, "def": 120, "spa": 72, "spd": 70, "spe": 106},
        "learnset": ["Rapid Spin", "Earthquake", "Iron Head", "Stealth Rock", "Volt Switch", "Ice Spinner"]
    },
    "Scizor": {
        "types": ["Bug", "Steel"],
        "baseStats": {"hp": 70, "atk": 130, "def": 100, "spa": 55, "spd": 80, "spe": 65},
        "learnset": ["Bullet Punch", "U-turn", "Close Combat", "Knock Off", "Swords Dance", "Defog"]
    },
}

# Add more Pokemon data to reach 100+
ADDITIONAL_POKEMON = {
    "Garchomp": {
        "types": ["Dragon", "Ground"],
        "baseStats": {"hp": 108, "atk": 130, "def": 95, "spa": 80, "spd": 85, "spe": 102},
        "learnset": ["Stealth Rock", "Earthquake", "Dragon Claw", "Swords Dance", "Scale Shot", "Fire Fang"]
    },
    "Rillaboom": {
        "types": ["Grass"],
        "baseStats": {"hp": 100, "atk": 125, "def": 90, "spa": 60, "spd": 70, "spe": 85},
        "learnset": ["Grassy Glide", "U-turn", "Wood Hammer", "Knock Off", "High Horsepower", "Drain Punch"]
    },
    "Kyurem": {
        "types": ["Dragon", "Ice"],
        "baseStats": {"hp": 125, "atk": 130, "def": 90, "spa": 130, "spd": 90, "spe": 95},
        "learnset": ["Draco Meteor", "Ice Beam", "Freeze-Dry", "Earth Power", "Icicle Spear", "Dragon Dance"]
    },
}

# Merge datasets
POKEMON_DATA.update(ADDITIONAL_POKEMON)


def main():
    # Parse usage stats
    usage_file = Path("/tmp/gen9ou-usage.txt")
    pokemon_usage = parse_usage_stats(usage_file, top_n=100)

    print(f"Parsed {len(pokemon_usage)} Pokemon from usage stats")
    print(f"We have data for {len(POKEMON_DATA)} Pokemon")

    # Build pokedex JSON
    pokedex = []
    usage_csv = []

    for entry in pokemon_usage:
        name = entry['name']

        if name in POKEMON_DATA:
            pokemon_entry = {
                "name": name,
                **POKEMON_DATA[name]
            }
            pokedex.append(pokemon_entry)

            usage_csv.append({
                'name': name,
                'usage_pct': entry['usage_pct'],
                'tier': 'OU',
                'generation': 9,
                'month': '2025-09'
            })

    print(f"\nBuilt dataset with {len(pokedex)} Pokemon")

    # Save pokedex.json
    output_dir = Path("/Users/joshyeung/personal-projects/pokemon-team-recommender/worktrees/expand-pokemon-dataset/data/raw")

    with open(output_dir / "pokedex.json", 'w') as f:
        json.dump(pokedex, f, indent=2)

    print(f"Saved {len(pokedex)} Pokemon to pokedex.json")

    # Save usage_ou.csv
    with open(output_dir / "usage_ou.csv", 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'usage_pct', 'tier', 'generation', 'month'])
        writer.writeheader()
        writer.writerows(usage_csv)

    print(f"Saved {len(usage_csv)} entries to usage_ou.csv")

    # Show missing Pokemon
    missing = [entry['name'] for entry in pokemon_usage if entry['name'] not in POKEMON_DATA]
    if missing:
        print(f"\nMissing data for {len(missing)} Pokemon:")
        for i, name in enumerate(missing[:20], 1):
            print(f"  {i}. {name}")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")


if __name__ == "__main__":
    main()
