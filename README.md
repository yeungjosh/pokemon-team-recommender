# Pokémon Team Recommender

> Data-driven team completion for competitive Pokémon

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**Status:** Early development

## What is this?

Give me 3 Pokémon, I'll recommend 3 more to complete your team.

Recommendations based on:
- Type coverage (offensive + defensive)
- Meta matchups (counters to common threats)
- Role balance (hazards, removal, pivots, speed control)

## Quick Start

```bash
git clone https://github.com/your-username/pokemon-team-recommender.git
cd pokemon-team-recommender

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

Visit `http://localhost:7860`

## How it Works

### Scoring Algorithm

Each recommendation gets a composite score:

```
Score = 0.4·TypeCoverage + 0.4·MetaMatchup + 0.2·RoleDiversity
```

**Type Coverage**
- Offensive: Can you hit all 18 types super-effectively?
- Defensive: Do you have too many shared weaknesses?

**Meta Matchup**
- Can your team handle the top 15 most-used Pokémon?
- Weighted by usage stats

**Role Diversity**
- Hazard setter (Stealth Rock, Spikes)
- Hazard removal (Defog, Rapid Spin)
- Pivot (U-turn, Volt Switch)
- Speed control (fast mons or priority)

### Search

Beam search over top 100 most-used Pokémon (by tier), excluding your input. Target: <2s locally, <4s on Hugging Face Spaces.

## Project Structure

```
.
├── src/
│   ├── data/         # Load Pokédex, type chart, usage stats
│   ├── features/     # Calculate coverage, roles, meta checks
│   ├── search/       # Beam search implementation
│   └── eval/         # Metrics (Recall@K, MRR, NDCG)
├── app.py            # Gradio interface
├── tests/
└── data/
    ├── raw/          # Pokédex, type effectiveness, usage CSVs
    └── processed/    # Cached features (Parquet)
```

## Development

### Testing

```bash
pytest tests/
pytest --cov=src --cov-report=term-missing
```

### Code Quality

```bash
black .
ruff check .
```

### Deployment

Push to `main` → auto-deploys to Hugging Face Spaces (once configured).

## Data Sources

- **Pokédex & Type Chart:** [Pokémon Showdown](https://github.com/smogon/pokemon-showdown) (MIT License)
- **Usage Stats:** [Smogon University](https://www.smogon.com/stats/)

See [data/SOURCES.md](data/SOURCES.md) for details.

## Roadmap

- [ ] Data pipeline (fetch Pokédex, stats)
- [ ] Feature extraction (type coverage, roles)
- [ ] Scoring algorithm
- [ ] Beam search
- [ ] Gradio UI
- [ ] Deploy to Spaces
- [ ] Evaluation framework (Recall@10, ablations)

## License

[MIT](LICENSE)

## Contributing

PRs welcome! Please:
- Write tests for new features
- Run `black` and `ruff` before committing
- Follow existing code style

---

Built for the competitive Pokémon community.
