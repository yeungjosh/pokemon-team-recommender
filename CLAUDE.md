# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Pokémon Team Recommender** is a Gradio web application deployed on Hugging Face Spaces that recommends 3 Pokémon to complete a user's partial team based on type coverage, meta matchup, and role synergy.

**Tech Stack:** Python, Gradio v4.0+, Hugging Face Spaces (CPU Basic tier), pandas, numpy, scikit-learn

**Status:** Greenfield project with comprehensive spec-driven development setup

## Development Workflow with Spec-Kit

This project uses [GitHub Spec-Kit](https://github.com/github/spec-kit) for spec-driven development. The workflow follows this order:

1. **Constitution** → Defines non-negotiable principles (`.specify/memory/constitution.md`)
2. **Specification** → Describes features in natural language (`.specify/specs/`)
3. **Technical Plan** → Implementation details and technology choices
4. **Task Breakdown** → Small, testable units of work
5. **Implementation** → TDD cycle (test → fail → code → pass → refactor)

### Available Spec-Kit Commands

Run these slash commands in Claude Code:

- `/speckit.constitution` - Review or update project principles
- `/speckit.specify` - Create a new feature specification
- `/speckit.plan` - Generate technical implementation plan
- `/speckit.tasks` - Break down plan into actionable tasks
- `/speckit.implement` - Execute implementation with TDD
- `/speckit.analyze` - Validate spec-plan-task consistency
- `/speckit.checklist` - Generate quality checklists

### Existing Specifications

Located in `.specify/specs/`:

1. **01-data-pipeline.md** - Data ingestion and processing (Pokédex, type chart, usage stats)
2. **02-recommender-core.md** - Composite scoring algorithm and search strategy
3. **03-gradio-ui.md** - Web interface with autocomplete, visualizations, export
4. **04-evaluation-framework.md** - Offline metrics (Recall@K, MRR, NDCG), ablation studies
5. **05-deployment-hf-spaces.md** - Hugging Face Spaces deployment

## Architecture Overview

### Data Flow

```
[Usage Stats] [Pokédex] [Type Chart]
       ↓           ↓          ↓
   Ingestion → Processed Tables → Feature Layer → Recommender → Gradio UI
                                       ↓              ↓
                               [Type Coverage]  [Composite Score]
                               [Role Tags]      [Beam Search]
                               [Meta Matchup]
```

### Scoring Algorithm

```
CompositeScore = α·TypeCoverage + β·MetaCoverage + γ·RoleDiversity
```

**Default Weights (MVP):** α=0.4, β=0.4, γ=0.2

**TypeCoverage:**
- Offensive: count defense types with ≥1 2× STAB hitter
- Defensive: penalize attack types with ≥2 weaknesses, 0 resists/immunity

**MetaCoverage:**
- For each top-K meta Pokémon: does team have ≥1 check?
- Weight by usage percentage

**RoleDiversity:**
- Reward presence of: hazards, removal, pivot, speed control
- Score = (roles present) / 4

**Search Strategy:**
- Candidate pool: top 100 by usage (after removing user's 3 inputs)
- MVP: Greedy or beam search (beam≈50) over candidate trios
- Performance target: <1.5s search on 161k combinations

### Repository Structure

```
pokemon-team-recommender/
├── .specify/                 # Spec-kit configuration
│   ├── memory/
│   │   └── constitution.md   # Project principles (NON-NEGOTIABLE)
│   ├── specs/                # Feature specifications
│   ├── scripts/bash/         # Helper scripts
│   └── templates/            # Spec-kit templates
├── data/
│   ├── raw/                  # type_chart.json, pokedex.json, usage_ou.csv
│   └── processed/            # mon_features.parquet, meta_topk.json
├── src/
│   ├── data/                 # Loaders (dex, types, usage), caching
│   ├── features/             # Coverage, roles, meta matchup calculations
│   ├── search/               # Greedy/beam search algorithms
│   ├── models/               # Phase 2: CF + LTR (not MVP)
│   ├── eval/                 # Metrics + offline evaluation
│   └── app/                  # Glue for Gradio UI
├── app/                      # Gradio app entry point (app.py)
├── notebooks/                # Evaluation notebooks
├── tests/                    # Unit, integration, property tests
├── worktrees/                # Git worktrees for parallel development (gitignored)
├── requirements.txt
├── runtime.txt               # Python version for Spaces
├── README.md
└── LICENSE
```

## Git Worktrees for Parallel Development

This project uses git worktrees to enable parallel feature development in isolated directories:

```bash
# List all worktrees
git worktree list

# Available worktrees:
worktrees/data-pipeline     → feature/data-pipeline branch
worktrees/recommender-core  → feature/recommender-core branch
worktrees/gradio-ui         → feature/gradio-ui branch
worktrees/testing           → feature/testing branch
worktrees/deployment        → feature/deployment branch
```

**To switch worktrees:**
```bash
./.specify/scripts/bash/switch-worktree.sh data-pipeline
```

**To create a new worktree:**
```bash
git worktree add worktrees/<name> -b feature/<name>
```

## Common Development Commands

### Setup

```bash
# Initialize development environment (virtual env, dependencies, dev tools)
./.specify/scripts/bash/setup-dev.sh

# Manually activate virtual environment
source venv/bin/activate
```

### Running the Application

```bash
# Local development (Gradio app)
python app.py
# Access at http://localhost:7860
```

### Testing

```bash
# Run all tests
./.specify/scripts/bash/run-tests.sh

# Run tests with coverage
./.specify/scripts/bash/run-tests.sh --coverage

# Run specific test pattern
./.specify/scripts/bash/run-tests.sh --filter "test_type_coverage"

# Run tests verbosely
./.specify/scripts/bash/run-tests.sh --verbose

# Manual pytest
pytest tests/
pytest tests/test_features.py::test_type_coverage -v
pytest --cov=src --cov-report=term-missing
```

### Code Quality

```bash
# Format code with black
black .

# Lint code with ruff
ruff check .

# Fix linting issues automatically
ruff check --fix .

# Type checking (if added)
mypy src/
```

### Deployment

```bash
# Deploy to Hugging Face Spaces
./.specify/scripts/bash/deploy-spaces.sh

# Manually push to Spaces
git push hf main
```

### Data Pipeline

```bash
# Fetch latest Pokémon Showdown data
python src/data/fetch_showdown_data.py

# Download Smogon usage stats
python src/data/fetch_usage_stats.py --tier gen9ou --month 2025-10

# Process raw data into Parquet/JSON
python src/data/process_data.py
```

### Evaluation

```bash
# Run offline evaluation on test set
python src/eval/run_evaluation.py --test-set data/test_teams.json

# Run ablation studies
python src/eval/run_ablations.py --output results/ablations.json

# Generate evaluation report
python src/eval/generate_report.py --results results/ --output eval_report.md
```

## Performance Targets (NON-NEGOTIABLE)

- **Feature build (cached):** <150ms
- **Search (60+ candidates):** <1.5s
- **End-to-end local:** <2s
- **End-to-end Spaces CPU Basic:** <4s

If any change violates these targets, it's a blocking issue. Profile before merging.

## Testing Requirements (NON-NEGOTIABLE)

### Test Types

1. **Unit Tests:** Type multipliers, role detection, scoring math
2. **Property Tests:** Invariants (e.g., resist addition never increases defensive penalty)
3. **Integration Tests:** Fixed-seed recommendations stable across runs
4. **Performance Tests:** Validate latency targets

### TDD Workflow

**Always write tests first:**
1. Write test (expect failure)
2. Run test (verify it fails)
3. Implement feature
4. Run test (verify it passes)
5. Refactor (maintain passing tests)

### Coverage Requirements

- Minimum 80% code coverage for `src/` modules
- 100% coverage for scoring algorithms (critical path)
- All public functions must have tests

## Code Quality Standards (NON-NEGOTIABLE)

### Linting & Formatting

- **ruff:** Zero warnings policy
- **black:** Consistent formatting (line length 88)
- **Pre-commit hooks:** Enforce checks before commit
- **CI:** GitHub Actions validates on every push

### Documentation

- **Docstrings:** Google style for all public functions
- **Inline comments:** Explain "why", not "what"
- **Type hints:** Use for all function signatures (Python 3.11+)

### Commit Messages

Use conventional commits format:

```
feat: add type coverage calculation
fix: correct Ground type weakness handling
test: add property tests for defensive penalties
docs: update README with deployment instructions
refactor: extract role detection to separate module
```

## Data Sources & Attribution

- **Pokémon Showdown data:** https://github.com/smogon/pokemon-showdown
- **Smogon usage stats:** https://www.smogon.com/stats/
- **@pkmn/smogon API:** (if used) https://github.com/pkmn/smogon

**Ethics:**
- Use only public, published data
- Never scrape private battle logs
- Respect upstream licenses and rate limits
- Include data snapshot date in UI

## Hugging Face Spaces Specifics

### Deployment Flow

1. Push to `main` branch
2. Spaces auto-rebuilds from `requirements.txt`
3. Runs `app.py` (or `app/app.py`)
4. Accessible at `https://huggingface.co/spaces/<username>/pokemon-team-recommender`

### Cold Start Handling

- Vendor lightweight data (<5MB) in repo
- Larger data: fetch-and-cache to `/home/user/.cache/`
- Show progress indicators during first-run data processing
- Cache invalidation: check data version/date

### Space Metadata (in README.md frontmatter)

```yaml
---
title: Pokémon Team Recommender
emoji: ⚔️
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
license: mit
tags: [pokemon, recommender, ml, competitive, team-building]
---
```

## Key Constraints

### Tech Stack (LOCKED FOR MVP)

- **Language:** Python only
- **UI:** Gradio v4.0+ (no custom web server)
- **Hosting:** Hugging Face Spaces CPU Basic (no GPU)
- **Data:** JSON, CSV, Parquet (no databases)

### Out of Scope (MVP)

- Full battle simulation
- Custom set inference (EVs/IVs/moves)
- User accounts or authentication
- Real-time meta tracking (monthly snapshots sufficient)

### Phase 2 Features (Post-MVP)

- User-adjustable weight sliders (α, β, γ)
- LightGBM learn-to-rank model
- Co-usage graph for collaborative filtering
- Multi-tier simultaneous support
- Advanced visualizations (interactive charts)

## Troubleshooting

### Common Issues

**Import errors:**
- Ensure virtual environment activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Data not loading:**
- Check `data/raw/` contains `type_chart.json`, `pokedex.json`, `usage_ou.csv`
- Run data fetch scripts: `python src/data/fetch_showdown_data.py`

**Slow performance:**
- Verify caching enabled: check `data/processed/mon_features.parquet` exists
- Profile code: `python -m cProfile -o profile.stats app.py`
- Check for redundant type chart lookups (should load once)

**Tests failing:**
- Ensure deterministic random seed: `random.seed(42)`, `np.random.seed(42)`
- Check data fixtures: `tests/fixtures/` should have sample data
- Run single test with verbose output: `pytest tests/test_foo.py::test_bar -vv`

### Getting Help

- **Constitution:** `.specify/memory/constitution.md` (non-negotiable principles)
- **Specs:** `.specify/specs/` (detailed feature requirements)
- **Original Spec:** `pokemon_team_recommender_spec.md` (comprehensive product doc)
- **GitHub Issues:** (if public repo) https://github.com/<username>/pokemon-team-recommender/issues

## Special Notes for Claude Code

- **Always check constitution first:** `.specify/memory/constitution.md` gates all decisions
- **Use spec-kit workflow:** Don't skip steps (constitution → spec → plan → tasks → implement)
- **TDD is mandatory:** Write tests before implementation (Red-Green-Refactor)
- **Performance is non-negotiable:** Profile if changes risk violating targets (<2s local, <4s Spaces)
- **Git worktrees:** Use for parallel development, not for switching between features frequently
- **Helper scripts:** Use `.specify/scripts/bash/*.sh` for common tasks (setup, test, deploy, worktree switching)

## Current Project Status

- **Phase:** MVP (Milestone 1)
- **Implementation Status:** Spec-driven setup complete, no code implemented yet
- **Next Steps:** Follow execution plan in `pokemon_team_recommender_spec.md` section 16:
  1. Scaffold repo structure (folders, `requirements.txt`, `runtime.txt`)
  2. Implement loaders & features (type chart, dex, usage, coverage/roles)
  3. Implement scorer + search (beam or greedy)
  4. Build Gradio UI (`app/app.py`) and test locally
  5. Deploy to Spaces; add README badges + demo GIF
  6. Replace seed data with monthly usage + full dex; add tests and caching
