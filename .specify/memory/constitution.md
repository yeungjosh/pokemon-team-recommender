# Pokémon Team Recommender Constitution

## Core Principles

### I. Performance-First (NON-NEGOTIABLE)
All features must meet strict performance targets:
- **<150ms** feature build with caching enabled
- **<1.5s** total search on 60+ candidates
- **<2s** end-to-end on local development
- **<4s** end-to-end on Hugging Face Spaces CPU Basic tier

Performance degradation is a blocking issue. Profile before optimization, but never ship slow code.

### II. Tech Stack Constraints (LOCKED FOR MVP)
The technology stack is fixed and cannot be changed without explicit approval:
- **Language:** Python only
- **UI Framework:** Gradio v4.0+
- **Hosting:** Hugging Face Spaces (CPU Basic tier)
- **Data Formats:** JSON, CSV, Parquet (via PyArrow)
- **ML Tools:** pandas, numpy, scikit-learn, LightGBM (Phase 2), networkx

No backend services, no Node.js server, no alternative frameworks. Spaces runs a single Gradio process.

### III. Data-Driven & Transparent
All recommendations must be explainable and data-driven:
- Every trio recommendation includes score breakdown (Type + Meta + Role)
- Data sources are attributed and dated
- Usage stats labeled by month/generation/tier
- No black-box recommendations without reasoning

Users must understand *why* a Pokémon was recommended, not just *that* it was recommended.

### IV. Test-First Development (NON-NEGOTIABLE)
Testing is mandatory before implementation:
- **Unit tests:** Type multipliers, role detection, scoring math correctness
- **Property tests:** Invariants (e.g., resist addition never increases defensive penalty, idempotent caching)
- **Integration tests:** Fixed-seed recommendations stable across runs
- **Performance tests:** Validate latency targets

Tests written → User approved → Tests fail → Then implement. Red-Green-Refactor cycle strictly enforced.

### V. Public Data Only & Ethics
Data sourcing must respect licenses and privacy:
- Use only published, public data sources (Pokémon Showdown data files, Smogon monthly stats, @pkmn/smogon API)
- Never scrape private battle logs or redistribute protected data
- Respect upstream licenses and rate limits
- Include attribution and data cache dates in the UI
- No user accounts, no data collection beyond usage stats

Legal and ethical compliance is non-negotiable.

## Architecture Standards

### Data Flow Integrity
The data pipeline follows a strict unidirectional flow:
1. **Ingestion:** Fetch/copy usage stats, Showdown Pokédex, type effectiveness chart
2. **Processing:** Normalize into Parquet/JSON in `data/processed/`
3. **Feature Layer:** Calculate type coverage, role tags, meta matchup vs top-K
4. **Recommender:** Heuristic composite scoring + beam/greedy search
5. **UI:** Gradio interface delivering results with explanations

Never bypass this flow or skip normalization steps. Raw data stays in `data/raw/`, processed data in `data/processed/`.

### Scoring Algorithm Consistency
The composite score formula is canonical:

```
CompositeScore = α·TypeCoverage + β·MetaCoverage + γ·RoleDiversity
```

**TypeCoverage:**
- Offense: count defense types with ≥1 2× STAB hitter
- Defense: penalize attack types with ≥2 weaknesses, 0 resists/immunity

**MetaCoverage:**
- For each top-K used Pokémon: does team have ≥1 check?
- Weight by usage percentage

**RoleDiversity:**
- Reward presence of roles: hazards, removal, pivot, speed control
- Phase 2: wallbreaker, cleric, status absorber

Changes to this formula require offline evaluation validation and comparison against baseline metrics.

### Caching Strategy
Feature computation must be cached aggressively:
- Per-Pokémon features cached in `data/processed/mon_features.parquet`
- Top-K meta Pokémon cached in `data/processed/meta_topk.json`
- Type effectiveness chart loaded once at startup
- No redundant computation during search

Cold start handling on Spaces: vendor lightweight data or fetch-and-cache to `/home/user/.cache` on first run.

## Code Quality Standards

### Linting & Formatting
Code must pass quality gates before commit:
- **ruff** for linting (zero warnings policy)
- **black** for consistent formatting
- Pre-commit hooks enforce these checks automatically
- GitHub Actions CI validates on every push

### Code Organization
Follow the defined repository structure:
```
pokemon-team-recommender/
├── data/
│   ├── raw/              # type_chart.json, pokedex.json, usage_ou.csv
│   └── processed/        # mon_features.parquet, meta_topk.json
├── src/
│   ├── data/            # Loaders (dex, types, usage), caching
│   ├── features/        # Coverage, roles, meta matchup calculations
│   ├── search/          # Greedy/beam search algorithms
│   ├── models/          # Phase 2: CF + LTR (not MVP)
│   ├── eval/            # Metrics + offline evaluation
│   └── app/             # Glue for Gradio UI
├── app/                 # Gradio app entry point (app.py)
├── notebooks/           # Evaluation notebooks
├── tests/               # Unit, integration, property tests
├── requirements.txt
├── runtime.txt          # Python version for Spaces
├── README.md
└── LICENSE
```

Do not deviate from this structure without explicit approval.

### Documentation Standards
- All public functions must have docstrings (Google style)
- Complex algorithms require inline comments explaining the "why"
- README must include: demo badge, architecture diagram, performance metrics
- Data sources must be attributed with links

## Hugging Face Spaces Specifics

### Deployment Requirements
- Space metadata tags: `pokemon`, `recommender`, `ml`, `gradio`
- LICENSE file (MIT) committed to repo
- README with embedded demo (Space badge + GIF)
- `requirements.txt` pinning major versions only (allow patch updates)
- Optional `runtime.txt` for Python version (e.g., `python-3.11`)

### Spaces Constraints
- Single-process Gradio app (no multi-worker scaling)
- CPU Basic tier only (no GPU dependencies)
- Handle cold starts gracefully (progress indicators for first-run data processing)
- Persistent storage optional (for caching) but not required

### Data Handling on Spaces
- Lightweight data (< 10MB) committed directly
- Larger datasets use `hf://` dataset storage or fetch-and-cache pattern
- Name/alias handling: autocomplete from Pokédex with fuzzy matching
- Meta staleness: label data by month, provide UI dropdown for tier/generation

## Evaluation & Quality Gates

### Offline Evaluation Metrics
Before shipping recommendation changes, validate against:
- **Recall@10**: Top-10 trio candidates contain ground truth
- **MRR (Mean Reciprocal Rank)**: Average position of first correct recommendation
- **NDCG (Normalized Discounted Cumulative Gain)**: Ranking quality metric

### Ablation Studies Required
When changing scoring logic, run ablations:
- Baseline (all components)
- -MetaCoverage (remove meta matching)
- -RoleDiversity (remove role bonuses)
- Heuristic vs Ranker (Phase 2: compare to LightGBM model)

### Qualitative Validation
- Case studies against known archetypes (HO, Balance, Stall, Weather teams)
- Human ratings (1-5 scale) for usefulness and clarity
- Smoke test: given `[Garchomp, Raging Bolt, Great Tusk]`, validate Top-5 trios are sensible

## Development Workflow

### Iteration Cycle
1. **Constitution** (this document) gates all implementation decisions
2. **Specification** describes features in natural language (what & why)
3. **Technical Plan** defines implementation details (how & technology choices)
4. **Task Breakdown** generates small, testable units of work
5. **Implementation** follows TDD cycle (test → fail → code → pass → refactor)

### Git Workflow
- **Main branch:** production-ready code only
- **Feature branches:** one per major feature (data-pipeline, recommender-core, gradio-ui, testing, deployment)
- **Git worktrees:** parallel development in isolated working directories
- **Commit messages:** conventional commits format (`feat:`, `fix:`, `test:`, `docs:`)

### Review & Merge Gates
- All tests pass (unit + property + integration)
- Code coverage maintained or improved
- Performance benchmarks meet targets
- Linting/formatting checks pass
- README updated if public API changes

## Risk Mitigation

### Known Risks & Countermeasures
1. **Stale meta data**
   - Mitigation: Label usage stats by month, add UI dropdown for generation/tier, provide refresh script

2. **Cold start latency on Spaces**
   - Mitigation: Vendor data files, cache processed artifacts, show progress indicators

3. **Name/alias ambiguity** (e.g., "Lando" → Landorus-Therian)
   - Mitigation: Ship autocomplete from Pokédex, fuzzy string matching, display canonical names

4. **Overfitting to current meta**
   - Mitigation: Evaluate across multiple months/tiers, ablation studies, hold-out test set

## Governance

### Amendment Process
This constitution supersedes all other development practices. To amend:
1. Document proposed change with rationale
2. Run impact analysis (affected code, tests, performance)
3. Gain approval from project owner
4. Update constitution version and "Last Amended" date
5. Create migration plan for existing code

### Compliance Verification
- All PRs must verify alignment with this constitution
- Any complexity that violates principles must be explicitly justified
- Spec-kit commands (`/speckit.analyze`, `/speckit.checklist`) validate cross-artifact consistency

### Scope Creep Prevention
Non-goals for MVP (explicitly out of scope):
- Full battle simulation
- Custom set inference (EVs/IVs/moves)
- User accounts or authentication
- Multi-tier simultaneous support
- Real-time meta tracking

Phase 2 features require updated specifications and constitutional amendments.

---

**Version**: 1.0.0 | **Ratified**: 2025-10-19 | **Last Amended**: 2025-10-19
