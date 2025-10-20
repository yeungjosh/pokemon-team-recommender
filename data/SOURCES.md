# Data Sources & Attribution

This file documents all data sources used in the Pokemon Team Recommender project.

## Pokémon Showdown Data

**Source:** https://github.com/smogon/pokemon-showdown

**License:** MIT License (https://github.com/smogon/pokemon-showdown/blob/master/LICENSE)

**Files Used:**
- `data/raw/pokedex.json` - Pokémon species data including types, base stats, and learnsets
- `data/raw/type_chart.json` - Type effectiveness chart (18×18 matchup matrix)

**Attribution:** Pokémon Showdown is a simulator developed by Smogon University (https://www.smogon.com)

**Update Frequency:** As needed when new generations/forms are released

**Last Updated:** [To be filled when data is fetched]

---

## Smogon Usage Statistics

**Source:** https://www.smogon.com/stats/

**API (if used):** @pkmn/smogon - https://github.com/pkmn/smogon

**Files Used:**
- `data/raw/usage_ou.csv` - Monthly usage statistics for Gen 9 OU tier

**Attribution:** Smogon University competitive Pokémon usage statistics

**Update Frequency:** Monthly (published around the 1st of each month)

**Format:** CSV with columns: `name, usage_pct, tier, generation, month`

**Last Updated:** [To be filled when data is fetched]

**Notes:**
- Usage percentages represent the proportion of teams that include each Pokémon
- Data is aggregated from Pokémon Showdown ladder battles (rating threshold: 1500+)
- We only use publicly published aggregate statistics, never individual battle logs

---

## Data Processing

**Processed Files (Generated):**
- `data/processed/mon_features.parquet` - Cached Pokémon features for fast lookup
- `data/processed/meta_topk.json` - Top-K most-used Pokémon by tier

**Processing Scripts:**
- `src/data/fetch_showdown_data.py` - Fetches Pokédex and type chart
- `src/data/fetch_usage_stats.py` - Downloads Smogon usage statistics
- `src/data/process_data.py` - Normalizes raw data into processed format

---

## Ethical Data Use

### Principles

1. **Public Data Only:** We use only publicly published, aggregate data sources
2. **No Private Data:** We never scrape or store private battle logs or individual player data
3. **Attribution:** All data sources are properly credited and linked
4. **License Compliance:** We respect upstream licenses and rate limits
5. **Transparency:** Data snapshot dates are displayed in the UI

### Privacy

- No user accounts or authentication required
- No collection of user inputs or recommendations
- No tracking or analytics beyond basic usage statistics
- All processing happens locally or on Hugging Face Spaces (no third-party data sharing)

### Upstream Respect

- We cache data locally to minimize load on upstream servers
- We include appropriate delay between API requests (if fetching programmatically)
- We document data snapshot dates and update frequency
- We provide clear attribution in the application UI and README

---

## Data Snapshot Information

**Current Data Version:** [To be filled]

**Data Freshness:**
- Pokédex: [Date]
- Type Chart: [Date]
- Usage Stats (Gen 9 OU): [Month/Year]

**Next Scheduled Update:** [Date]

---

## Additional Resources

- Pokémon Showdown Damage Calculator: https://calc.pokemonshowdown.com/
- Smogon Strategy Dex: https://www.smogon.com/dex/
- Smogon Forums: https://www.smogon.com/forums/
- @pkmn Project: https://pkmn.cc/

---

**Last Updated:** 2025-10-19
