---
title: Pokemon Team Recommender
emoji: ⚔️
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
license: mit
tags:
  - pokemon
  - recommender
  - competitive
  - team-building
---

# Pokémon Team Recommender

> Data-driven team completion for competitive Pokémon

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**Give me 3 Pokémon, I'll recommend 3 more to complete your team.**

## How It Works

Recommendations based on:
- 🎯 **Type Coverage** - Offensive and defensive synergy
- 🏆 **Meta Matchup** - Counters to top 15 threats
- 🛡️ **Role Balance** - Hazards, removal, pivots, speed control

### Scoring Algorithm

```
Score = 0.4×TypeCoverage + 0.4×MetaMatchup + 0.2×RoleDiversity
```

**Type Coverage:**
- Offensive: Can you hit all 18 types super-effectively?
- Defensive: Do you have shared weaknesses without resists?

**Meta Matchup:**
- Can your team handle Dragapult, Garchomp, Kingambit, etc.?
- Weighted by usage stats (Oct 2024 OU)

**Role Diversity:**
- Hazard setter (Stealth Rock, Spikes)
- Hazard removal (Defog, Rapid Spin)
- Pivot (U-turn, Volt Switch)
- Speed control (fast mons or priority)

## Example

**Input:** Garchomp, Raging Bolt, Great Tusk

**Top Recommendation (Score: 0.966):**
- Kingambit, Gliscor, Corviknight
- Type: 0.94 | Meta: 1.00 | Roles: 1.00

## Data Sources

- **Pokédex & Type Chart:** [Pokémon Showdown](https://github.com/smogon/pokemon-showdown) (MIT License)
- **Usage Stats:** [Smogon University](https://www.smogon.com/stats/) (Oct 2024 OU)

## Local Development

### Quick Setup

```bash
git clone https://github.com/your-username/pokemon-team-recommender.git
cd pokemon-team-recommender

# Use the setup script (recommended)
./scripts/setup.sh
```

### Manual Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install package in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Running the App

```bash
python app.py
```

Visit `http://localhost:7860`

## Testing

```bash
# Run all tests with coverage
pytest tests/unit/ -v

# 28 tests, 93% coverage
```

## Project Structure

```
.
├── src/
│   ├── data/         # Pokédex, type chart, usage loaders
│   ├── features/     # Type coverage, roles, meta analysis
│   └── search/       # Recommendation engine
├── app.py            # Gradio interface
├── tests/            # Unit tests
└── data/raw/         # Type chart, Pokédex, usage stats
```

## License

[MIT](LICENSE)

---

Built for the competitive Pokémon community 🎮
