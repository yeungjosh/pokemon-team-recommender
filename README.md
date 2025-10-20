# ⚔️ Pokémon Team Recommender

**Complete your Pokémon team with data-driven recommendations**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> 🚧 **Status:** Under active development (MVP in progress)

## Overview

Given **3 Pokémon**, get **5 recommended trios** to complete your team based on:

- 🎯 **Type Coverage** - Offensive and defensive type synergy
- 🏆 **Meta Matchup** - Checks against top competitive threats
- 🛡️ **Role Diversity** - Hazards, removal, pivot, speed control

Built with [Gradio](https://gradio.app/) and deployed on [Hugging Face Spaces](https://huggingface.co/spaces).

## Features

- ✅ **Explainable Recommendations** - See score breakdowns and reasoning
- ✅ **Fast Performance** - <2s locally, <4s on Spaces CPU
- ✅ **Data-Driven** - Based on Smogon usage stats and Pokémon Showdown data
- ✅ **Export to Showdown** - Copy teams directly to Pokémon Showdown
- 🚧 **Multiple Tiers** - Gen 9 OU, Ubers, UU, RU, NU (MVP: OU only)

## Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/your-username/pokemon-team-recommender.git
cd pokemon-team-recommender

# Run setup script (creates venv, installs dependencies)
./.specify/scripts/bash/setup-dev.sh

# Activate virtual environment
source venv/bin/activate

# Run Gradio app
python app.py
```

Access at `http://localhost:7860`

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run app
python app.py
```

## Architecture

### High-Level Flow

```
[User Input: 3 Pokémon] → [Recommender Engine] → [Top-5 Trios with Explanations]
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
              Type Coverage    Meta Matchup    Role Diversity
                    ↓               ↓               ↓
              α·TypeScore + β·MetaScore + γ·RoleScore = Composite Score
```

### Composite Scoring Algorithm

```
CompositeScore = α·TypeCoverage + β·MetaCoverage + γ·RoleDiversity
```

**Default Weights:** α=0.4, β=0.4, γ=0.2

**Components:**

1. **TypeCoverage**
   - Offensive: Count defense types with ≥1 2× STAB hitter
   - Defensive: Penalize attack types with ≥2 weaknesses, 0 resists/immunity

2. **MetaCoverage**
   - Check if team has ≥1 counter to each top-K meta threat
   - Weight by usage percentage

3. **RoleDiversity**
   - Reward presence of: hazard setter, hazard removal, pivot, speed control
   - Score = (roles present) / 4

**Search Strategy:** Beam search (beam≈50) or greedy over top-100 usage candidates

### Repository Structure

```
pokemon-team-recommender/
├── .specify/              # Spec-kit (spec-driven development)
│   ├── memory/constitution.md   # Project principles
│   ├── specs/             # Feature specifications
│   └── scripts/bash/      # Helper scripts (setup, test, deploy)
├── data/
│   ├── raw/               # Pokédex, type chart, usage stats
│   └── processed/         # Cached features (Parquet/JSON)
├── src/
│   ├── data/              # Data loaders and processing
│   ├── features/          # Type coverage, roles, meta matchup
│   ├── search/            # Recommendation search algorithms
│   ├── eval/              # Evaluation metrics (Recall@K, MRR, NDCG)
│   └── app/               # Gradio UI components
├── app.py                 # Main Gradio app entry point
├── tests/                 # Unit, integration, property tests
├── requirements.txt       # Python dependencies
├── runtime.txt            # Python version (for Spaces)
├── pyproject.toml         # Project configuration
└── CLAUDE.md              # Development guide for Claude Code
```

## Development

### Helper Scripts

```bash
# Initialize development environment
./.specify/scripts/bash/setup-dev.sh

# Run tests
./.specify/scripts/bash/run-tests.sh

# Run tests with coverage
./.specify/scripts/bash/run-tests.sh --coverage

# Deploy to Hugging Face Spaces
./.specify/scripts/bash/deploy-spaces.sh

# Switch between git worktrees (parallel development)
./.specify/scripts/bash/switch-worktree.sh data-pipeline
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Fix linting issues
ruff check --fix .

# Run tests
pytest tests/

# Run tests with coverage
pytest --cov=src --cov-report=term-missing
```

### Git Worktrees (Parallel Development)

This project uses git worktrees for isolated feature development:

```bash
# List worktrees
git worktree list

# Available worktrees:
worktrees/data-pipeline     → feature/data-pipeline
worktrees/recommender-core  → feature/recommender-core
worktrees/gradio-ui         → feature/gradio-ui
worktrees/testing           → feature/testing
worktrees/deployment        → feature/deployment
```

### Spec-Driven Development

This project follows [GitHub Spec-Kit](https://github.com/github/spec-kit) methodology:

1. **Constitution** (`.specify/memory/constitution.md`) - Non-negotiable principles
2. **Specification** (`.specify/specs/`) - Feature descriptions
3. **Technical Plan** - Implementation details
4. **Task Breakdown** - Actionable units
5. **Implementation** - TDD cycle

**Slash Commands:**
- `/speckit.constitution` - Review project principles
- `/speckit.specify` - Create feature spec
- `/speckit.plan` - Generate technical plan
- `/speckit.tasks` - Break down into tasks
- `/speckit.implement` - Execute with TDD

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Feature Build (cached) | <150ms | 🚧 |
| Search (60+ candidates) | <1.5s | 🚧 |
| End-to-End (local) | <2s | 🚧 |
| End-to-End (Spaces CPU) | <4s | 🚧 |
| Recall@10 (evaluation) | ≥0.35 | 🚧 |

## Data Sources & Attribution

- **Pokémon Showdown Data:** [github.com/smogon/pokemon-showdown](https://github.com/smogon/pokemon-showdown) (MIT License)
- **Smogon Usage Stats:** [smogon.com/stats](https://www.smogon.com/stats/)
- **@pkmn/smogon API:** [github.com/pkmn/smogon](https://github.com/pkmn/smogon) (if used)

See [`data/SOURCES.md`](data/SOURCES.md) for detailed attribution and licensing information.

### Ethical Data Use

- ✅ Public data only (no private battle logs)
- ✅ Proper attribution and licensing compliance
- ✅ Data snapshot dates displayed in UI
- ✅ No user tracking or data collection

## Roadmap

### Milestone 1: MVP (Spaces-ready)
- [x] Spec-driven development setup
- [x] Git worktrees for parallel development
- [x] Project structure and tooling
- [ ] Data pipeline (Pokédex, type chart, usage stats)
- [ ] Feature extraction (type coverage, roles, meta matchup)
- [ ] Composite scoring algorithm
- [ ] Beam/greedy search
- [ ] Gradio UI with top-5 recommendations
- [ ] Deploy to Hugging Face Spaces

### Milestone 2: Data Completeness
- [ ] Full Pokémon Showdown Pokédex
- [ ] Monthly Smogon usage stats integration
- [ ] Meta matchup vs top-15 threats
- [ ] Feature caching and optimization
- [ ] Comprehensive test suite

### Milestone 3: Evaluation & Polish
- [ ] Offline evaluation (Recall@10, MRR, NDCG)
- [ ] Ablation studies (TypeCoverage, MetaCoverage, RoleDiversity)
- [ ] Demo GIF and architecture diagrams
- [ ] UI tuning (sliders, export to Showdown)

### Milestone 4: ML Ranker (Stretch Goal)
- [ ] Co-usage graph analysis
- [ ] LightGBM learn-to-rank model
- [ ] A/B toggle (heuristic vs ML)
- [ ] Feature importance analysis

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Guidelines:**
- Follow [Conventional Commits](https://www.conventionalcommits.org/)
- Write tests for new features (TDD required)
- Ensure code passes linting (`ruff check .`) and formatting (`black .`)
- Update documentation as needed

See [`CLAUDE.md`](CLAUDE.md) for detailed development workflow.

## License

[MIT License](LICENSE) - see LICENSE file for details.

## Acknowledgments

- **Pokémon Showdown** - Simulator and data source
- **Smogon University** - Competitive Pokémon community and usage stats
- **@pkmn Project** - Pokémon data tools and APIs
- **Gradio** - UI framework for ML demos
- **Hugging Face** - Hosting platform (Spaces)

---

**Built with ❤️ for the competitive Pokémon community**
