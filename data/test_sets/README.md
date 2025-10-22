# Test Sets for Evaluation

This directory contains test sets for evaluating the Pokemon Team Recommender.

## Test Set Format

Each test set is a JSON file containing an array of complete competitive teams:

```json
[
  {
    "id": 1,
    "name": "Hyper Offense Sample",
    "tier": "gen9ou",
    "archetype": "hyperoffense",
    "source": "Smogon Sample Teams",
    "source_url": "https://www.smogon.com/...",
    "team": [
      "Garchomp",
      "Great Tusk",
      "Raging Bolt",
      "Rillaboom",
      "Iron Valiant",
      "Dragapult"
    ]
  }
]
```

### Fields

- `id`: Unique integer identifier for the team
- `name`: Human-readable name for the team
- `tier`: Competitive tier (e.g., "gen9ou")
- `archetype`: Team archetype (see below)
- `source`: Where the team came from
- `source_url`: URL to original team (for attribution)
- `team`: Array of exactly 6 Pokemon names (canonical forms)

### Archetypes

- `hyperoffense` (HO): 5-6 attackers, minimal defensive backbone
- `balance`: Mix of offensive and defensive Pokemon with good type synergy
- `stall`: Defensive core with hazards, recovery, and passive damage
- `rain`: Rain setter + Swift Swim abusers
- `sun`: Sun setter + Chlorophyll/Solar Power abusers
- `sand`: Sand setter + Sand Rush/Force abusers
- `snow`: Snow setter + Snow Cloak/Slush Rush abusers
- `trickroom`: Slow, powerful attackers under Trick Room
- `screens`: Dual screens support + setup sweepers
- `bulky-offense` (BO): Balanced offense with defensive pivots

### Test Case Generation

For evaluation, each complete team is split into:
- **Input**: First 3 Pokemon from the team
- **Ground Truth**: Last 3 Pokemon (the trio to recover)

This simulates a user who has 3 team members and needs recommendations for the remaining 3.

## Files

- `complete_teams.json`: Full test set of 100+ competitive teams
- `smoke_tests.json`: Small set of hand-crafted test cases for sanity checks
- `partial_teams.json`: Auto-generated input/ground-truth pairs (created by preprocessing script)

## Data Sources

Teams are curated from:
1. **Smogon Sample Teams**: https://www.smogon.com/dex/ss/formats/ou/
2. **Smogon Tournament Replays**: High-level tournament teams
3. **Pokemon Showdown Ladder**: Top-rated teams from public replays
4. **Content Creators**: With permission and attribution

All teams are from Gen 9 OU tier for MVP. Expansion to other tiers in Phase 2.

## Attribution

See individual team entries for source URLs and attribution.
