# Data Pipeline Specification

## Overview
Build a robust data ingestion and processing pipeline that fetches Pokémon metadata, type effectiveness data, and competitive usage statistics, then normalizes them into efficient formats for fast feature computation.

## Problem Statement
The recommender needs comprehensive, up-to-date Pokémon data to make informed suggestions. This data comes from multiple sources (Pokémon Showdown, Smogon usage stats) in various formats and must be normalized for performant access during recommendation generation.

## User Stories

### As a Developer
- I want to fetch the latest Pokémon Showdown Pokédex data so that the recommender has accurate type, stats, and learnset information
- I want to download monthly usage statistics from Smogon so that recommendations reflect current competitive meta
- I want data cached and normalized so that the Gradio app starts quickly and meets performance targets

### As a Hugging Face Spaces User
- I want the app to load in under 4 seconds so that I can start getting recommendations immediately
- I want to know which meta snapshot the recommendations are based on so I understand if they're current

## Requirements

### Data Sources
1. **Pokémon Showdown Pokédex** (`data/raw/pokedex.json`)
   - Schema: `[{name, types[], baseStats{hp, atk, def, spa, spd, spe}, learnset{move: [sources]}}]`
   - Contains: All Pokémon with their types, base stats, and available moves
   - Update frequency: Monthly or as new generations release

2. **Type Effectiveness Chart** (`data/raw/type_chart.json`)
   - Schema: `{attacking_type: {defending_type: multiplier}}`
   - Contains: 18×18 type matchup matrix
   - Static data (rarely changes)

3. **Usage Statistics** (`data/raw/usage_ou.csv`)
   - Schema: `name,usage_pct,tier,generation,month`
   - Contains: Competitive usage percentages for each Pokémon
   - Update frequency: Monthly from Smogon stats

### Processed Outputs
1. **Pokémon Features Table** (`data/processed/mon_features.parquet`)
   - Cached per-Pokémon features for fast lookup
   - Columns: `name, type1, type2, speed, usage_pct, roles[], offensive_coverage[], defensive_weaknesses[]`
   - Format: Parquet for columnar access and compression

2. **Meta Top-K Cache** (`data/processed/meta_topk.json`)
   - List of top 15-100 most-used Pokémon by tier
   - Format: `{tier: [{name, usage_pct, types, common_sets}]}`
   - Used for meta matchup scoring

### Functional Requirements
1. **Data Fetching**
   - Fetch Pokémon Showdown data from public GitHub repo or vendored snapshot
   - Download Smogon usage stats via @pkmn/smogon API or stat dumps
   - Support offline mode with vendored data for Spaces cold starts

2. **Data Validation**
   - Verify schema correctness (e.g., types are valid, usage percentages sum correctly)
   - Handle missing data gracefully (e.g., new Pokémon without full usage data)
   - Log warnings for anomalies (e.g., unexpected type combinations)

3. **Data Normalization**
   - Convert all Pokémon names to canonical form (e.g., "Landorus-Therian" not "Lando-T")
   - Normalize usage percentages to 0-1 range
   - Extract role tags from learnsets (e.g., learns Stealth Rock → hazard setter)

4. **Caching Strategy**
   - Cache processed data to avoid recomputation on every app restart
   - Include cache metadata (generation date, source version)
   - Invalidate cache when source data updates

### Performance Requirements
- Data loading from cache: **<100ms** on Spaces CPU Basic
- Full data processing (if cache miss): **<3s** on Spaces CPU Basic
- Processed Parquet file size: **<5MB** for fast I/O

### Error Handling
- If data fetch fails, fall back to vendored snapshot
- If processed cache is corrupted, regenerate from raw data
- Log all errors with context (which data source, what failed)

## Data Attribution & Ethics
- Include `data/raw/SOURCES.md` documenting:
  - Pokémon Showdown data license and source URL
  - Smogon usage stats source and update frequency
  - @pkmn/smogon API attribution if used
- Display data snapshot date in Gradio UI
- Never redistribute private battle logs or protected data

## Acceptance Criteria
- [ ] Data pipeline fetches Pokédex, type chart, and usage stats from public sources
- [ ] Processed data cached in Parquet and JSON formats
- [ ] Cache includes metadata (generation date, source version)
- [ ] Pipeline handles missing data gracefully (logs warnings, continues processing)
- [ ] Data loading meets performance targets (<100ms cached, <3s uncached)
- [ ] SOURCES.md documents all data attributions
- [ ] Pipeline tested with both vendored data (offline mode) and fresh fetches

## Out of Scope
- Real-time meta tracking (monthly snapshots sufficient for MVP)
- Multi-tier simultaneous support (focus on Gen 9 OU for MVP)
- Custom set inference (use aggregated stats, not individual sets)

## Dependencies
- Python packages: `pandas`, `pyarrow`, `requests` (for data fetching)
- External data: Pokémon Showdown GitHub repo, Smogon usage stats
