# Task: Expand Pokemon Dataset

**Branch:** `feature/expand-pokemon-dataset`

**Priority:** High (Most Impactful)

## Objective

Expand the Pokemon dataset from 15 seed Pokemon to 100+ competitive Gen 9 OU Pokemon to make the recommender more useful and comprehensive.

## Current State

**Problem:**
- Only 15 Pokemon in `data/raw/pokedex.json`
- Only 15 entries in `data/raw/usage_ou.csv`
- Causes "Pokemon not found" errors for most user inputs
- Limited recommendation pool results in poor quality suggestions

**Example Error:**
```
❌ Error: Pokémon not found: Pikachu
```

## Root Cause

Started with minimal seed data for MVP testing. Need full competitive dataset for production use.

## Tasks

- [ ] Fetch latest Gen 9 OU usage statistics from Smogon (2025-09)
- [ ] Parse usage stats to get top 100 Pokemon by usage %
- [ ] Fetch Pokemon data from Pokemon Showdown repository
- [ ] Extract types, base stats, and key moves for each Pokemon
- [ ] Update `data/raw/pokedex.json` with 100+ Pokemon
- [ ] Update `data/raw/usage_ou.csv` with full usage stats
- [ ] Update `data/SOURCES.md` with snapshot dates
- [ ] Test data loaders with new dataset
- [ ] Test recommender with expanded pool
- [ ] Verify performance still meets targets (<2s local)
- [ ] Commit and push changes

## Data Sources

- **Usage Stats:** https://www.smogon.com/stats/2025-09/gen9ou-0.txt
- **Pokemon Data:** https://github.com/smogon/pokemon-showdown/blob/master/data/pokedex.ts
- **Move Data:** https://github.com/smogon/pokemon-showdown/blob/master/data/moves.ts
- **Type Chart:** Already have (no changes needed)

## Data Structure

Each Pokemon entry needs:
```json
{
  "name": "Pokemon-Name",
  "types": ["Type1", "Type2"],
  "baseStats": {
    "hp": 100, "atk": 100, "def": 100,
    "spa": 100, "spd": 100, "spe": 100
  },
  "learnset": [
    "Key Move 1",
    "Key Move 2",
    ...
  ]
}
```

**Learnset Selection Criteria:**
- Hazard moves: Stealth Rock, Spikes, Toxic Spikes
- Removal moves: Rapid Spin, Defog
- Pivot moves: U-turn, Volt Switch, Flip Turn
- Priority moves: Extreme Speed, Aqua Jet, Sucker Punch, etc.
- STAB moves for coverage calculation
- Common competitive moves (5-10 per Pokemon)

## Success Criteria

1. Dataset includes 100+ Pokemon (target: top 100 by usage)
2. All top 50 OU Pokemon are included
3. Each Pokemon has complete data (types, stats, key moves)
4. "Pokemon not found" errors reduced by 90%+
5. Usage CSV matches Pokemon in dex (no orphaned entries)
6. Data snapshot dates documented in SOURCES.md
7. Tests still pass
8. Performance remains <2s local, <4s Spaces

## Estimated Time

30-60 minutes

## Dependencies

None - standalone task

## Notes

- Focus on OU tier (most competitive relevance)
- Include some UU Pokemon for variety (50-75 total)
- Keep move lists concise (quality over quantity)
- Maintain JSON structure compatibility
- Consider Pokemon with form differences (e.g., Landorus-Therian, Ogerpon-Wellspring)
