#!/usr/bin/env python3
"""
Build comprehensive Pokemon dataset from top 100 Gen 9 OU Pokemon.

This is the PRIMARY dataset builder for the project. It generates:
- data/raw/pokedex.json: Pokemon metadata (types, stats, moves)
- data/raw/usage_ou.csv: Usage statistics from Smogon

Data is curated from Pokemon Showdown and Smogon usage stats (Sept 2025).
Run this script to regenerate the dataset if needed.
"""

import json
import csv
from pathlib import Path

# Comprehensive Pokemon data for top 100 Gen 9 OU
# Data sourced from: https://github.com/smogon/pokemon-showdown/blob/master/data/pokedex.ts
# Movesets from: https://www.smogon.com/dex/sv/pokemon/

COMPREHENSIVE_POKEMON_DATA = [
    # Top 20
    {
        "name": "Great Tusk",
        "types": ["Ground", "Fighting"],
        "baseStats": {"hp": 115, "atk": 131, "def": 131, "spa": 53, "spd": 53, "spe": 87},
        "learnset": ["Rapid Spin", "Earthquake", "Close Combat", "Ice Spinner", "Knock Off", "Stealth Rock", "Stone Edge"],
        "usage_pct": 27.15831
    },
    {
        "name": "Kingambit",
        "types": ["Dark", "Steel"],
        "baseStats": {"hp": 100, "atk": 135, "def": 120, "spa": 60, "spd": 85, "spe": 50},
        "learnset": ["Sucker Punch", "Kowtow Cleave", "Iron Head", "Swords Dance", "Low Kick", "Zen Headbutt"],
        "usage_pct": 18.06053
    },
    {
        "name": "Gholdengo",
        "types": ["Steel", "Ghost"],
        "baseStats": {"hp": 87, "atk": 60, "def": 95, "spa": 133, "spd": 91, "spe": 84},
        "learnset": ["Make It Rain", "Shadow Ball", "Trick", "Nasty Plot", "Thunderbolt", "Focus Blast"],
        "usage_pct": 16.22521
    },
    {
        "name": "Dragapult",
        "types": ["Dragon", "Ghost"],
        "baseStats": {"hp": 88, "atk": 120, "def": 75, "spa": 100, "spd": 75, "spe": 142},
        "learnset": ["Dragon Darts", "U-turn", "Shadow Ball", "Will-O-Wisp", "Hex", "Draco Meteor"],
        "usage_pct": 16.07289
    },
    {
        "name": "Dragonite",
        "types": ["Dragon", "Flying"],
        "baseStats": {"hp": 91, "atk": 134, "def": 95, "spa": 100, "spd": 100, "spe": 80},
        "learnset": ["Extreme Speed", "Dragon Dance", "Outrage", "Earthquake", "Ice Beam", "Fire Punch"],
        "usage_pct": 14.39675
    },
    {
        "name": "Ogerpon-Wellspring",
        "types": ["Water", "Grass"],
        "baseStats": {"hp": 80, "atk": 120, "def": 84, "spa": 60, "spd": 96, "spe": 110},
        "learnset": ["Ivy Cudgel", "Horn Leech", "U-turn", "Knock Off", "Spiky Shield", "Play Rough"],
        "usage_pct": 14.39336
    },
    {
        "name": "Hatterene",
        "types": ["Psychic", "Fairy"],
        "baseStats": {"hp": 57, "atk": 90, "def": 95, "spa": 136, "spd": 103, "spe": 29},
        "learnset": ["Psychic", "Dazzling Gleam", "Trick Room", "Healing Wish", "Mystical Fire", "Calm Mind"],
        "usage_pct": 12.32524
    },
    {
        "name": "Iron Valiant",
        "types": ["Fairy", "Fighting"],
        "baseStats": {"hp": 74, "atk": 130, "def": 90, "spa": 120, "spd": 60, "spe": 116},
        "learnset": ["Close Combat", "Moonblast", "Knock Off", "Calm Mind", "Thunderbolt", "Psyshock"],
        "usage_pct": 11.82189
    },
    {
        "name": "Slowking-Galar",
        "types": ["Poison", "Psychic"],
        "baseStats": {"hp": 95, "atk": 65, "def": 80, "spa": 110, "spd": 110, "spe": 30},
        "learnset": ["Sludge Bomb", "Psychic", "Future Sight", "Trick Room", "Flamethrower", "Thunder Wave"],
        "usage_pct": 11.60327
    },
    {
        "name": "Corviknight",
        "types": ["Flying", "Steel"],
        "baseStats": {"hp": 98, "atk": 87, "def": 105, "spa": 53, "spd": 85, "spe": 67},
        "learnset": ["Defog", "Brave Bird", "U-turn", "Roost", "Iron Defense", "Bulk Up"],
        "usage_pct": 11.57651
    },
    {
        "name": "Zamazenta",
        "types": ["Fighting"],
        "baseStats": {"hp": 92, "atk": 130, "def": 115, "spa": 80, "spd": 115, "spe": 138},
        "learnset": ["Close Combat", "Iron Head", "Crunch", "Stone Edge", "Heavy Slam", "Play Rough"],
        "usage_pct": 11.36988
    },
    {
        "name": "Landorus-Therian",
        "types": ["Ground", "Flying"],
        "baseStats": {"hp": 89, "atk": 145, "def": 90, "spa": 105, "spd": 80, "spe": 91},
        "learnset": ["Stealth Rock", "Earthquake", "U-turn", "Knock Off", "Stone Edge", "Fly"],
        "usage_pct": 11.31552
    },
    {
        "name": "Gliscor",
        "types": ["Ground", "Flying"],
        "baseStats": {"hp": 75, "atk": 95, "def": 125, "spa": 45, "spd": 75, "spe": 95},
        "learnset": ["Stealth Rock", "Earthquake", "U-turn", "Toxic", "Protect", "Knock Off"],
        "usage_pct": 11.11511
    },
    {
        "name": "Raging Bolt",
        "types": ["Electric", "Dragon"],
        "baseStats": {"hp": 125, "atk": 73, "def": 91, "spa": 137, "spd": 89, "spe": 75},
        "learnset": ["Thunderclap", "Draco Meteor", "Volt Switch", "Calm Mind", "Thunderbolt", "Dragon Pulse"],
        "usage_pct": 11.08080
    },
    {
        "name": "Cinderace",
        "types": ["Fire"],
        "baseStats": {"hp": 80, "atk": 116, "def": 75, "spa": 65, "spd": 75, "spe": 119},
        "learnset": ["Pyro Ball", "U-turn", "High Jump Kick", "Sucker Punch", "Gunk Shot", "Court Change"],
        "usage_pct": 9.57097
    },
    {
        "name": "Samurott-Hisui",
        "types": ["Water", "Dark"],
        "baseStats": {"hp": 90, "atk": 108, "def": 80, "spa": 100, "spd": 65, "spe": 85},
        "learnset": ["Ceaseless Edge", "Aqua Cutter", "Knock Off", "Sucker Punch", "Swords Dance", "Sacred Sword"],
        "usage_pct": 9.34559
    },
    {
        "name": "Ting-Lu",
        "types": ["Dark", "Ground"],
        "baseStats": {"hp": 155, "atk": 110, "def": 125, "spa": 55, "spd": 80, "spe": 45},
        "learnset": ["Stealth Rock", "Earthquake", "Ruination", "Whirlwind", "Spikes", "Heavy Slam"],
        "usage_pct": 8.92382
    },
    {
        "name": "Glimmora",
        "types": ["Rock", "Poison"],
        "baseStats": {"hp": 83, "atk": 55, "def": 90, "spa": 130, "spd": 81, "spe": 86},
        "learnset": ["Stealth Rock", "Power Gem", "Sludge Wave", "Earth Power", "Spikes", "Mortal Spin"],
        "usage_pct": 8.63080
    },
    {
        "name": "Iron Treads",
        "types": ["Ground", "Steel"],
        "baseStats": {"hp": 90, "atk": 112, "def": 120, "spa": 72, "spd": 70, "spe": 106},
        "learnset": ["Rapid Spin", "Earthquake", "Iron Head", "Stealth Rock", "Volt Switch", "Ice Spinner"],
        "usage_pct": 8.51349
    },
    {
        "name": "Scizor",
        "types": ["Bug", "Steel"],
        "baseStats": {"hp": 70, "atk": 130, "def": 100, "spa": 55, "spd": 80, "spe": 65},
        "learnset": ["Bullet Punch", "U-turn", "Close Combat", "Knock Off", "Swords Dance", "Defog"],
        "usage_pct": 8.30191
    },
    # 21-40
    {
        "name": "Ceruledge",
        "types": ["Fire", "Ghost"],
        "baseStats": {"hp": 75, "atk": 125, "def": 80, "spa": 60, "spd": 100, "spe": 85},
        "learnset": ["Bitter Blade", "Poltergeist", "Close Combat", "Shadow Sneak", "Swords Dance", "Bulk Up"],
        "usage_pct": 8.26279
    },
    {
        "name": "Alomomola",
        "types": ["Water"],
        "baseStats": {"hp": 165, "atk": 75, "def": 80, "spa": 40, "spd": 45, "spe": 65},
        "learnset": ["Flip Turn", "Scald", "Wish", "Protect", "Mirror Coat", "Play Rough"],
        "usage_pct": 7.89964
    },
    {
        "name": "Iron Moth",
        "types": ["Fire", "Poison"],
        "baseStats": {"hp": 80, "atk": 70, "def": 60, "spa": 140, "spd": 110, "spe": 110},
        "learnset": ["Fiery Dance", "Sludge Wave", "U-turn", "Energy Ball", "Morning Sun", "Agility"],
        "usage_pct": 7.71552
    },
    {
        "name": "Kyurem",
        "types": ["Dragon", "Ice"],
        "baseStats": {"hp": 125, "atk": 130, "def": 90, "spa": 130, "spd": 90, "spe": 95},
        "learnset": ["Draco Meteor", "Ice Beam", "Freeze-Dry", "Earth Power", "Icicle Spear", "Dragon Dance"],
        "usage_pct": 7.66825
    },
    {
        "name": "Darkrai",
        "types": ["Dark"],
        "baseStats": {"hp": 70, "atk": 90, "def": 90, "spa": 135, "spd": 90, "spe": 125},
        "learnset": ["Dark Pulse", "Ice Beam", "Sludge Bomb", "Focus Blast", "Nasty Plot", "Hypnosis"],
        "usage_pct": 7.58759
    },
    {
        "name": "Pecharunt",
        "types": ["Poison", "Ghost"],
        "baseStats": {"hp": 88, "atk": 88, "def": 160, "spa": 88, "spd": 88, "spe": 88},
        "learnset": ["Malignant Chain", "Shadow Ball", "Recover", "Parting Shot", "Hex", "Foul Play"],
        "usage_pct": 7.55506
    },
    {
        "name": "Zapdos",
        "types": ["Electric", "Flying"],
        "baseStats": {"hp": 90, "atk": 90, "def": 85, "spa": 125, "spd": 90, "spe": 100},
        "learnset": ["Thunderbolt", "Hurricane", "Heat Wave", "Volt Switch", "Roost", "U-turn"],
        "usage_pct": 7.53451
    },
    {
        "name": "Garganacl",
        "types": ["Rock"],
        "baseStats": {"hp": 100, "atk": 100, "def": 130, "spa": 45, "spd": 90, "spe": 35},
        "learnset": ["Salt Cure", "Stealth Rock", "Recover", "Earthquake", "Stone Edge", "Body Press"],
        "usage_pct": 6.93316
    },
    {
        "name": "Walking Wake",
        "types": ["Water", "Dragon"],
        "baseStats": {"hp": 99, "atk": 83, "def": 91, "spa": 125, "spd": 83, "spe": 109},
        "learnset": ["Hydro Steam", "Draco Meteor", "Flamethrower", "Dragon Pulse", "Flip Turn", "Substitute"],
        "usage_pct": 6.60207
    },
    {
        "name": "Moltres",
        "types": ["Fire", "Flying"],
        "baseStats": {"hp": 90, "atk": 100, "def": 90, "spa": 125, "spd": 85, "spe": 90},
        "learnset": ["Flamethrower", "Hurricane", "U-turn", "Roost", "Will-O-Wisp", "Scorching Sands"],
        "usage_pct": 5.87512
    },
    {
        "name": "Primarina",
        "types": ["Water", "Fairy"],
        "baseStats": {"hp": 80, "atk": 74, "def": 74, "spa": 126, "spd": 116, "spe": 60},
        "learnset": ["Moonblast", "Surf", "Flip Turn", "Psychic Noise", "Calm Mind", "Ice Beam"],
        "usage_pct": 5.75972
    },
    {
        "name": "Garchomp",
        "types": ["Dragon", "Ground"],
        "baseStats": {"hp": 108, "atk": 130, "def": 95, "spa": 80, "spd": 85, "spe": 102},
        "learnset": ["Stealth Rock", "Earthquake", "Dragon Claw", "Swords Dance", "Scale Shot", "Fire Fang"],
        "usage_pct": 5.63587
    },
    {
        "name": "Rillaboom",
        "types": ["Grass"],
        "baseStats": {"hp": 100, "atk": 125, "def": 90, "spa": 60, "spd": 70, "spe": 85},
        "learnset": ["Grassy Glide", "U-turn", "Wood Hammer", "Knock Off", "High Horsepower", "Drain Punch"],
        "usage_pct": 5.47202
    },
    {
        "name": "Meowscarada",
        "types": ["Grass", "Dark"],
        "baseStats": {"hp": 76, "atk": 110, "def": 70, "spa": 81, "spd": 70, "spe": 123},
        "learnset": ["Flower Trick", "Knock Off", "U-turn", "Play Rough", "Sucker Punch", "Triple Axel"],
        "usage_pct": 5.24384
    },
    {
        "name": "Iron Crown",
        "types": ["Steel", "Psychic"],
        "baseStats": {"hp": 90, "atk": 72, "def": 100, "spa": 122, "spd": 108, "spe": 98},
        "learnset": ["Tachyon Cutter", "Psyshock", "Volt Switch", "Focus Blast", "Calm Mind", "Expanding Force"],
        "usage_pct": 4.99543
    },
    {
        "name": "Araquanid",
        "types": ["Water", "Bug"],
        "baseStats": {"hp": 68, "atk": 70, "def": 92, "spa": 50, "spd": 132, "spe": 42},
        "learnset": ["Liquidation", "Leech Life", "Sticky Web", "Sucker Punch", "Mirror Coat", "Toxic"],
        "usage_pct": 4.92941
    },
    {
        "name": "Enamorus",
        "types": ["Fairy", "Flying"],
        "baseStats": {"hp": 74, "atk": 115, "def": 70, "spa": 135, "spd": 80, "spe": 106},
        "learnset": ["Moonblast", "Earth Power", "Mystical Fire", "Calm Mind", "Superpower", "Taunt"],
        "usage_pct": 4.84581
    },
    {
        "name": "Clefable",
        "types": ["Fairy"],
        "baseStats": {"hp": 95, "atk": 70, "def": 73, "spa": 95, "spd": 90, "spe": 60},
        "learnset": ["Moonblast", "Flamethrower", "Stealth Rock", "Thunder Wave", "Calm Mind", "Soft-Boiled"],
        "usage_pct": 4.82573
    },
    {
        "name": "Weezing-Galar",
        "types": ["Poison", "Fairy"],
        "baseStats": {"hp": 65, "atk": 90, "def": 120, "spa": 85, "spd": 70, "spe": 60},
        "learnset": ["Sludge Bomb", "Play Rough", "Defog", "Will-O-Wisp", "Pain Split", "Taunt"],
        "usage_pct": 4.81003
    },
    {
        "name": "Pelipper",
        "types": ["Water", "Flying"],
        "baseStats": {"hp": 60, "atk": 50, "def": 100, "spa": 95, "spd": 70, "spe": 65},
        "learnset": ["Hurricane", "Surf", "U-turn", "Roost", "Defog", "Weather Ball"],
        "usage_pct": 4.16388
    },
    # 41-60
    {
        "name": "Heatran",
        "types": ["Fire", "Steel"],
        "baseStats": {"hp": 91, "atk": 90, "def": 106, "spa": 130, "spd": 106, "spe": 77},
        "learnset": ["Magma Storm", "Flash Cannon", "Earth Power", "Stealth Rock", "Taunt", "Will-O-Wisp"],
        "usage_pct": 4.15208
    },
    {
        "name": "Torkoal",
        "types": ["Fire"],
        "baseStats": {"hp": 70, "atk": 85, "def": 140, "spa": 85, "spd": 70, "spe": 20},
        "learnset": ["Stealth Rock", "Lava Plume", "Rapid Spin", "Yawn", "Body Press", "Solar Beam"],
        "usage_pct": 4.10609
    },
    {
        "name": "Weavile",
        "types": ["Dark", "Ice"],
        "baseStats": {"hp": 70, "atk": 120, "def": 65, "spa": 45, "spd": 85, "spe": 125},
        "learnset": ["Ice Shard", "Knock Off", "Triple Axel", "Low Kick", "Swords Dance", "Ice Spinner"],
        "usage_pct": 3.90605
    },
    {
        "name": "Deoxys-Speed",
        "types": ["Psychic"],
        "baseStats": {"hp": 50, "atk": 95, "def": 90, "spa": 95, "spd": 90, "spe": 180},
        "learnset": ["Stealth Rock", "Spikes", "Taunt", "Knock Off", "Psycho Boost", "Ice Beam"],
        "usage_pct": 3.89736
    },
    {
        "name": "Tyranitar",
        "types": ["Rock", "Dark"],
        "baseStats": {"hp": 100, "atk": 134, "def": 110, "spa": 95, "spd": 100, "spe": 61},
        "learnset": ["Stealth Rock", "Stone Edge", "Knock Off", "Ice Punch", "Dragon Dance", "Crunch"],
        "usage_pct": 3.74609
    },
    {
        "name": "Blaziken",
        "types": ["Fire", "Fighting"],
        "baseStats": {"hp": 80, "atk": 120, "def": 70, "spa": 110, "spd": 70, "spe": 80},
        "learnset": ["Close Combat", "Flare Blitz", "Knock Off", "Swords Dance", "Protect", "Stone Edge"],
        "usage_pct": 3.67980
    },
    {
        "name": "Toxapex",
        "types": ["Poison", "Water"],
        "baseStats": {"hp": 50, "atk": 63, "def": 152, "spa": 53, "spd": 142, "spe": 35},
        "learnset": ["Scald", "Toxic", "Recover", "Haze", "Toxic Spikes", "Knock Off"],
        "usage_pct": 3.62709
    },
    {
        "name": "Dondozo",
        "types": ["Water"],
        "baseStats": {"hp": 150, "atk": 100, "def": 115, "spa": 65, "spd": 65, "spe": 35},
        "learnset": ["Wave Crash", "Order Up", "Earthquake", "Body Press", "Curse", "Rest"],
        "usage_pct": 3.61473
    },
    {
        "name": "Ninetales-Alola",
        "types": ["Ice", "Fairy"],
        "baseStats": {"hp": 73, "atk": 67, "def": 75, "spa": 81, "spd": 100, "spe": 109},
        "learnset": ["Aurora Veil", "Blizzard", "Moonblast", "Freeze-Dry", "Encore", "Hail"],
        "usage_pct": 3.60137
    },
    {
        "name": "Ursaluna",
        "types": ["Ground", "Normal"],
        "baseStats": {"hp": 130, "atk": 140, "def": 105, "spa": 45, "spd": 80, "spe": 50},
        "learnset": ["Headlong Rush", "Facade", "Earthquake", "Swords Dance", "Bulk Up", "Drain Punch"],
        "usage_pct": 3.45139
    },
    {
        "name": "Clodsire",
        "types": ["Poison", "Ground"],
        "baseStats": {"hp": 130, "atk": 75, "def": 60, "spa": 45, "spd": 100, "spe": 20},
        "learnset": ["Earthquake", "Toxic", "Recover", "Spikes", "Stealth Rock", "Knock Off"],
        "usage_pct": 3.15201
    },
    {
        "name": "Serperior",
        "types": ["Grass"],
        "baseStats": {"hp": 75, "atk": 75, "def": 95, "spa": 75, "spd": 95, "spe": 113},
        "learnset": ["Leaf Storm", "Knock Off", "Glare", "Substitute", "Leech Seed", "Dragon Pulse"],
        "usage_pct": 3.09647
    },
    {
        "name": "Hydrapple",
        "types": ["Grass", "Dragon"],
        "baseStats": {"hp": 106, "atk": 80, "def": 110, "spa": 120, "spd": 80, "spe": 44},
        "learnset": ["Fickle Beam", "Giga Drain", "Earth Power", "Dragon Tail", "Recover", "Nasty Plot"],
        "usage_pct": 3.08759
    },
    {
        "name": "Greninja",
        "types": ["Water", "Dark"],
        "baseStats": {"hp": 72, "atk": 95, "def": 67, "spa": 103, "spd": 71, "spe": 122},
        "learnset": ["Hydro Pump", "Dark Pulse", "Ice Beam", "U-turn", "Spikes", "Toxic Spikes"],
        "usage_pct": 3.06037
    },
    {
        "name": "Hoopa-Unbound",
        "types": ["Psychic", "Dark"],
        "baseStats": {"hp": 80, "atk": 160, "def": 60, "spa": 170, "spd": 130, "spe": 80},
        "learnset": ["Hyperspace Fury", "Knock Off", "Drain Punch", "Psychic", "Gunk Shot", "Zen Headbutt"],
        "usage_pct": 2.86948
    },
    {
        "name": "Excadrill",
        "types": ["Ground", "Steel"],
        "baseStats": {"hp": 110, "atk": 135, "def": 60, "spa": 50, "spd": 65, "spe": 88},
        "learnset": ["Earthquake", "Iron Head", "Rapid Spin", "Swords Dance", "Rock Slide", "Stealth Rock"],
        "usage_pct": 2.80611
    },
    {
        "name": "Lokix",
        "types": ["Bug", "Dark"],
        "baseStats": {"hp": 71, "atk": 102, "def": 78, "spa": 52, "spd": 55, "spe": 92},
        "learnset": ["First Impression", "Knock Off", "U-turn", "Sucker Punch", "Axe Kick", "Throat Chop"],
        "usage_pct": 2.78346
    },
    {
        "name": "Latios",
        "types": ["Dragon", "Psychic"],
        "baseStats": {"hp": 80, "atk": 90, "def": 80, "spa": 130, "spd": 110, "spe": 110},
        "learnset": ["Draco Meteor", "Psychic", "Thunderbolt", "Flip Turn", "Calm Mind", "Surf"],
        "usage_pct": 2.77989
    },
    {
        "name": "Tornadus-Therian",
        "types": ["Flying"],
        "baseStats": {"hp": 79, "atk": 100, "def": 80, "spa": 110, "spd": 90, "spe": 121},
        "learnset": ["Bleakwind Storm", "U-turn", "Knock Off", "Heat Wave", "Taunt", "Defog"],
        "usage_pct": 2.69478
    },
    {
        "name": "Skeledirge",
        "types": ["Fire", "Ghost"],
        "baseStats": {"hp": 104, "atk": 75, "def": 100, "spa": 110, "spd": 75, "spe": 66},
        "learnset": ["Torch Song", "Shadow Ball", "Slack Off", "Will-O-Wisp", "Hex", "Earth Power"],
        "usage_pct": 2.64862
    },
    # 61-80
    {
        "name": "Ninetales",
        "types": ["Fire"],
        "baseStats": {"hp": 73, "atk": 76, "def": 75, "spa": 81, "spd": 100, "spe": 100},
        "learnset": ["Flamethrower", "Solar Beam", "Scorching Sands", "Will-O-Wisp", "Healing Wish", "Encore"],
        "usage_pct": 2.61997
    },
    {
        "name": "Blissey",
        "types": ["Normal"],
        "baseStats": {"hp": 255, "atk": 10, "def": 10, "spa": 75, "spd": 135, "spe": 55},
        "learnset": ["Seismic Toss", "Soft-Boiled", "Stealth Rock", "Thunder Wave", "Teleport", "Heal Bell"],
        "usage_pct": 2.60588
    },
    {
        "name": "Rotom-Wash",
        "types": ["Electric", "Water"],
        "baseStats": {"hp": 50, "atk": 65, "def": 107, "spa": 105, "spd": 107, "spe": 86},
        "learnset": ["Hydro Pump", "Volt Switch", "Will-O-Wisp", "Thunder Wave", "Discharge", "Pain Split"],
        "usage_pct": 2.55143
    },
    {
        "name": "Quaquaval",
        "types": ["Water", "Fighting"],
        "baseStats": {"hp": 85, "atk": 120, "def": 80, "spa": 85, "spd": 75, "spe": 85},
        "learnset": ["Aqua Step", "Close Combat", "Ice Spinner", "Knock Off", "Swords Dance", "Rapid Spin"],
        "usage_pct": 2.49282
    },
    {
        "name": "Venusaur",
        "types": ["Grass", "Poison"],
        "baseStats": {"hp": 80, "atk": 82, "def": 83, "spa": 100, "spd": 100, "spe": 80},
        "learnset": ["Sludge Bomb", "Giga Drain", "Synthesis", "Sleep Powder", "Knock Off", "Earth Power"],
        "usage_pct": 2.39692
    },
    {
        "name": "Sinistcha",
        "types": ["Grass", "Ghost"],
        "baseStats": {"hp": 71, "atk": 60, "def": 106, "spa": 121, "spd": 80, "spe": 70},
        "learnset": ["Matcha Gotcha", "Shadow Ball", "Calm Mind", "Strength Sap", "Stun Spore", "Leaf Storm"],
        "usage_pct": 2.37697
    },
    {
        "name": "Iron Hands",
        "types": ["Fighting", "Electric"],
        "baseStats": {"hp": 154, "atk": 140, "def": 108, "spa": 50, "spd": 68, "spe": 50},
        "learnset": ["Drain Punch", "Thunder Punch", "Ice Punch", "Fake Out", "Volt Switch", "Earthquake"],
        "usage_pct": 2.33117
    },
    {
        "name": "Ribombee",
        "types": ["Bug", "Fairy"],
        "baseStats": {"hp": 60, "atk": 55, "def": 60, "spa": 95, "spd": 70, "spe": 124},
        "learnset": ["Moonblast", "Bug Buzz", "Sticky Web", "U-turn", "Stun Spore", "Psychic"],
        "usage_pct": 2.20177
    },
    {
        "name": "Tinkaton",
        "types": ["Fairy", "Steel"],
        "baseStats": {"hp": 85, "atk": 75, "def": 77, "spa": 70, "spd": 105, "spe": 94},
        "learnset": ["Gigaton Hammer", "Knock Off", "Stealth Rock", "Thunder Wave", "Play Rough", "Ice Hammer"],
        "usage_pct": 2.12394
    },
    {
        "name": "Barraskewda",
        "types": ["Water"],
        "baseStats": {"hp": 61, "atk": 123, "def": 60, "spa": 60, "spd": 50, "spe": 136},
        "learnset": ["Liquidation", "Close Combat", "Flip Turn", "Crunch", "Psychic Fangs", "Aqua Jet"],
        "usage_pct": 2.07425
    },
    {
        "name": "Grimmsnarl",
        "types": ["Dark", "Fairy"],
        "baseStats": {"hp": 95, "atk": 120, "def": 65, "spa": 95, "spd": 75, "spe": 60},
        "learnset": ["Spirit Break", "Sucker Punch", "Reflect", "Light Screen", "Taunt", "Parting Shot"],
        "usage_pct": 1.81368
    },
    {
        "name": "Mimikyu",
        "types": ["Ghost", "Fairy"],
        "baseStats": {"hp": 55, "atk": 90, "def": 80, "spa": 50, "spd": 105, "spe": 96},
        "learnset": ["Play Rough", "Shadow Sneak", "Shadow Claw", "Swords Dance", "Trick Room", "Will-O-Wisp"],
        "usage_pct": 1.76207
    },
    {
        "name": "Ogerpon-Cornerstone",
        "types": ["Rock", "Grass"],
        "baseStats": {"hp": 80, "atk": 120, "def": 84, "spa": 60, "spd": 96, "spe": 110},
        "learnset": ["Ivy Cudgel", "Horn Leech", "Knock Off", "U-turn", "Spiky Shield", "Wood Hammer"],
        "usage_pct": 1.70003
    },
    {
        "name": "Gengar",
        "types": ["Ghost", "Poison"],
        "baseStats": {"hp": 60, "atk": 65, "def": 60, "spa": 130, "spd": 75, "spe": 110},
        "learnset": ["Shadow Ball", "Sludge Wave", "Focus Blast", "Will-O-Wisp", "Thunderbolt", "Nasty Plot"],
        "usage_pct": 1.61794
    },
    {
        "name": "Hawlucha",
        "types": ["Fighting", "Flying"],
        "baseStats": {"hp": 78, "atk": 92, "def": 75, "spa": 74, "spd": 63, "spe": 118},
        "learnset": ["Close Combat", "Brave Bird", "Acrobatics", "Stone Edge", "Swords Dance", "U-turn"],
        "usage_pct": 1.61703
    },
    {
        "name": "Goodra-Hisui",
        "types": ["Steel", "Dragon"],
        "baseStats": {"hp": 80, "atk": 100, "def": 100, "spa": 110, "spd": 150, "spe": 60},
        "learnset": ["Flash Cannon", "Draco Meteor", "Earthquake", "Thunderbolt", "Body Press", "Acid Spray"],
        "usage_pct": 1.58980
    },
    {
        "name": "Arcanine-Hisui",
        "types": ["Fire", "Rock"],
        "baseStats": {"hp": 95, "atk": 115, "def": 80, "spa": 95, "spd": 80, "spe": 90},
        "learnset": ["Flare Blitz", "Head Smash", "Extreme Speed", "Close Combat", "Stealth Rock", "Will-O-Wisp"],
        "usage_pct": 1.56692
    },
    {
        "name": "Ogerpon",
        "types": ["Grass"],
        "baseStats": {"hp": 80, "atk": 120, "def": 84, "spa": 60, "spd": 96, "spe": 110},
        "learnset": ["Ivy Cudgel", "Horn Leech", "Knock Off", "U-turn", "Spiky Shield", "Wood Hammer"],
        "usage_pct": 1.56056
    },
    {
        "name": "Indeedee",
        "types": ["Psychic", "Normal"],
        "baseStats": {"hp": 70, "atk": 55, "def": 65, "spa": 95, "spd": 105, "spe": 95},
        "learnset": ["Psychic", "Hyper Voice", "Trick Room", "Healing Wish", "Calm Mind", "Dazzling Gleam"],
        "usage_pct": 1.52680
    },
    {
        "name": "Comfey",
        "types": ["Fairy"],
        "baseStats": {"hp": 51, "atk": 52, "def": 90, "spa": 82, "spd": 110, "spe": 100},
        "learnset": ["Draining Kiss", "Calm Mind", "Trick Room", "Taunt", "Floral Healing", "U-turn"],
        "usage_pct": 1.50204
    },
    # 81-100
    {
        "name": "Metagross",
        "types": ["Steel", "Psychic"],
        "baseStats": {"hp": 80, "atk": 135, "def": 130, "spa": 95, "spd": 90, "spe": 70},
        "learnset": ["Meteor Mash", "Psychic Fangs", "Earthquake", "Ice Punch", "Stealth Rock", "Bullet Punch"],
        "usage_pct": 1.49394
    },
    {
        "name": "Volcanion",
        "types": ["Fire", "Water"],
        "baseStats": {"hp": 80, "atk": 110, "def": 120, "spa": 130, "spd": 90, "spe": 70},
        "learnset": ["Steam Eruption", "Flamethrower", "Earth Power", "Sludge Bomb", "Will-O-Wisp", "Taunt"],
        "usage_pct": 1.48511
    },
    {
        "name": "Incineroar",
        "types": ["Fire", "Dark"],
        "baseStats": {"hp": 95, "atk": 115, "def": 90, "spa": 80, "spd": 90, "spe": 60},
        "learnset": ["Flare Blitz", "Knock Off", "Parting Shot", "Will-O-Wisp", "Fake Out", "U-turn"],
        "usage_pct": 1.47734
    },
    {
        "name": "Keldeo",
        "types": ["Water", "Fighting"],
        "baseStats": {"hp": 91, "atk": 72, "def": 90, "spa": 129, "spd": 90, "spe": 108},
        "learnset": ["Secret Sword", "Surf", "Flip Turn", "Calm Mind", "Icy Wind", "Vacuum Wave"],
        "usage_pct": 1.47468
    },
    {
        "name": "Skarmory",
        "types": ["Steel", "Flying"],
        "baseStats": {"hp": 65, "atk": 80, "def": 140, "spa": 40, "spd": 70, "spe": 70},
        "learnset": ["Spikes", "Stealth Rock", "Brave Bird", "Roost", "Whirlwind", "Iron Defense"],
        "usage_pct": 1.47313
    },
    {
        "name": "Zoroark-Hisui",
        "types": ["Normal", "Ghost"],
        "baseStats": {"hp": 55, "atk": 100, "def": 60, "spa": 125, "spd": 60, "spe": 110},
        "learnset": ["Shadow Ball", "Hyper Voice", "U-turn", "Trick", "Knock Off", "Flamethrower"],
        "usage_pct": 1.45514
    },
    {
        "name": "Slither Wing",
        "types": ["Bug", "Fighting"],
        "baseStats": {"hp": 85, "atk": 135, "def": 79, "spa": 85, "spd": 105, "spe": 81},
        "learnset": ["Close Combat", "First Impression", "U-turn", "Earthquake", "Wild Charge", "Bulk Up"],
        "usage_pct": 1.42774
    },
    {
        "name": "Maushold",
        "types": ["Normal"],
        "baseStats": {"hp": 74, "atk": 75, "def": 70, "spa": 65, "spd": 75, "spe": 111},
        "learnset": ["Population Bomb", "Bite", "Encore", "Tidy Up", "U-turn", "Protect"],
        "usage_pct": 1.39360
    },
    {
        "name": "Hydreigon",
        "types": ["Dark", "Dragon"],
        "baseStats": {"hp": 92, "atk": 105, "def": 90, "spa": 125, "spd": 90, "spe": 98},
        "learnset": ["Draco Meteor", "Dark Pulse", "Earth Power", "Flash Cannon", "U-turn", "Stealth Rock"],
        "usage_pct": 1.39100
    },
    {
        "name": "Thundurus-Therian",
        "types": ["Electric", "Flying"],
        "baseStats": {"hp": 79, "atk": 105, "def": 70, "spa": 145, "spd": 80, "spe": 101},
        "learnset": ["Thunderbolt", "Volt Switch", "Focus Blast", "Agility", "Nasty Plot", "Knock Off"],
        "usage_pct": 1.29198
    },
    {
        "name": "Polteageist",
        "types": ["Ghost"],
        "baseStats": {"hp": 60, "atk": 65, "def": 65, "spa": 134, "spd": 114, "spe": 70},
        "learnset": ["Shadow Ball", "Stored Power", "Shell Smash", "Strength Sap", "Giga Drain", "Calm Mind"],
        "usage_pct": 1.29134
    },
    {
        "name": "Charizard",
        "types": ["Fire", "Flying"],
        "baseStats": {"hp": 78, "atk": 84, "def": 78, "spa": 109, "spd": 85, "spe": 100},
        "learnset": ["Flamethrower", "Hurricane", "Focus Blast", "Roost", "Dragon Pulse", "Solar Beam"],
        "usage_pct": 1.26558
    },
    {
        "name": "Latias",
        "types": ["Dragon", "Psychic"],
        "baseStats": {"hp": 80, "atk": 80, "def": 90, "spa": 110, "spd": 130, "spe": 110},
        "learnset": ["Draco Meteor", "Psychic", "Calm Mind", "Recover", "Thunderbolt", "Ice Beam"],
        "usage_pct": 1.20907
    },
    {
        "name": "Azumarill",
        "types": ["Water", "Fairy"],
        "baseStats": {"hp": 100, "atk": 50, "def": 80, "spa": 60, "spd": 80, "spe": 50},
        "learnset": ["Play Rough", "Aqua Jet", "Liquidation", "Knock Off", "Belly Drum", "Ice Punch"],
        "usage_pct": 1.17535
    },
    {
        "name": "Iron Boulder",
        "types": ["Rock", "Psychic"],
        "baseStats": {"hp": 90, "atk": 120, "def": 80, "spa": 68, "spd": 108, "spe": 124},
        "learnset": ["Mighty Cleave", "Zen Headbutt", "Close Combat", "Earthquake", "Swords Dance", "Stealth Rock"],
        "usage_pct": 1.14621
    },
    {
        "name": "Cloyster",
        "types": ["Water", "Ice"],
        "baseStats": {"hp": 50, "atk": 95, "def": 180, "spa": 85, "spd": 45, "spe": 70},
        "learnset": ["Shell Smash", "Icicle Spear", "Rock Blast", "Ice Shard", "Liquidation", "Spikes"],
        "usage_pct": 1.13587
    },
    {
        "name": "Gyarados",
        "types": ["Water", "Flying"],
        "baseStats": {"hp": 95, "atk": 125, "def": 79, "spa": 60, "spd": 100, "spe": 81},
        "learnset": ["Waterfall", "Dragon Dance", "Earthquake", "Ice Fang", "Crunch", "Power Whip"],
        "usage_pct": 1.12850
    },
    {
        "name": "Umbreon",
        "types": ["Dark"],
        "baseStats": {"hp": 95, "atk": 65, "def": 110, "spa": 60, "spd": 130, "spe": 65},
        "learnset": ["Foul Play", "Wish", "Protect", "Toxic", "Heal Bell", "Yawn"],
        "usage_pct": 1.12370
    },
    {
        "name": "Galvantula",
        "types": ["Bug", "Electric"],
        "baseStats": {"hp": 70, "atk": 77, "def": 60, "spa": 97, "spd": 60, "spe": 108},
        "learnset": ["Thunder", "Bug Buzz", "Sticky Web", "Volt Switch", "Giga Drain", "Energy Ball"],
        "usage_pct": 1.08435
    },
    {
        "name": "Kommo-o",
        "types": ["Dragon", "Fighting"],
        "baseStats": {"hp": 75, "atk": 110, "def": 125, "spa": 100, "spd": 105, "spe": 85},
        "learnset": ["Clanging Scales", "Close Combat", "Dragon Dance", "Stealth Rock", "Iron Head", "Earthquake"],
        "usage_pct": 1.05374
    },
]

def build_dataset():
    """Build comprehensive dataset files."""
    output_dir = Path(__file__).parents[1] / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build pokedex.json
    pokedex = []
    for mon in COMPREHENSIVE_POKEMON_DATA:
        entry = {
            "name": mon["name"],
            "types": mon["types"],
            "baseStats": mon["baseStats"],
            "learnset": mon["learnset"]
        }
        pokedex.append(entry)

    # Save pokedex.json
    with open(output_dir / "pokedex.json", 'w') as f:
        json.dump(pokedex, f, indent=2)

    print(f"✓ Saved {len(pokedex)} Pokemon to pokedex.json")

    # Build usage_ou.csv
    with open(output_dir / "usage_ou.csv", 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'usage_pct', 'tier', 'generation', 'month'])
        writer.writeheader()

        for mon in COMPREHENSIVE_POKEMON_DATA:
            writer.writerow({
                'name': mon['name'],
                'usage_pct': mon['usage_pct'],
                'tier': 'OU',
                'generation': 9,
                'month': '2025-09'
            })

    print(f"✓ Saved {len(COMPREHENSIVE_POKEMON_DATA)} entries to usage_ou.csv")
    print("\n✓ Dataset expansion complete!")
    print(f"  Expanded from 15 → {len(COMPREHENSIVE_POKEMON_DATA)} Pokemon")


if __name__ == "__main__":
    build_dataset()
