# Pokémon Team Recommender --- Product Spec & Design Doc (Gradio + Hugging Face Spaces)

**Tagline:** *"Complete my team."* Given three Pokémon, recommend three
additions that maximize type coverage, meta matchup, and role synergy.

**Owner:** You (ML Engineer)

**Status:** v1 --- Spaces/Gradio--focused

**Stack (locked for MVP):** Python (data + scoring) • **Gradio** UI •
**Hugging Face Spaces** hosting (Zero-backend glue, free tier). Optional
tiny Node script for data fetch.

------------------------------------------------------------------------

## 1) Problem Statement & Goals

**Problem:** Players often know 2--3 staples but struggle to complete a
balanced 6. Most tools stop at coverage calculators or static
analysis---not *data-driven completion*.

**Goal:** From a 3‑mon partial team, return top 3‑mon trios with
transparent reasoning: coverage deltas, role synergy, and basic meta
matchup.

**MVP Success Criteria** - Input 3 names → **Top‑5 trios** with scores &
explainability in \< 2s local / \< 4s on Spaces CPU. - Each trio shows
score breakdown: **Type, Meta, Roles** + brief rationale. - Clean repo
with tests, evaluation notebook, and a live Spaces demo linked in
README.

**Non‑Goals (MVP)** - Full battle simulation, custom set inference, user
accounts. - Scraping private battle logs. We use published usage +
Pokédex data only.

------------------------------------------------------------------------

## 2) User Stories & UX

**Personas** - *Ladder Player*: has 2--3 favorites; wants a competitive
full team quickly. - *Curious Recruiter*: opens demo; expects clarity,
speed, and a solid README.

**Core Flow** 1) Enter 3 Pokémon (or paste Showdown import).\
2) Click **Recommend** → returns **Top‑5** trios (ranked).\
3) Optional weight sliders (Type vs Meta vs Roles).\
4) Export the chosen 6 to Showdown format.

**UI (Gradio)** - **Inputs:** 3 text fields (with autocomplete), tier
dropdown (default **Gen 9 OU**), weight sliders.\
- **Outputs per trio:** composite score + breakdown; role badges
(hazards/removal/pivot/speed), a mini coverage radar, and a compact meta
heat strip vs top‑15 used mons.

------------------------------------------------------------------------

## 3) Data Sources & Ethics

**Data** - **Pokédex/types/learnsets:** Pokémon Showdown data files
(vendored snapshot).\
- **Usage & sample sets:** Smogon monthly stats (via @pkmn/smogon API or
stat dumps).\
- **(Optional)** Kaggle usage snapshots for prototyping.

**Ethics/Legal** - Use published & public sources with attribution.\
- Do **not** redistribute private battle logs; respect upstream licenses
and rate limits.\
- Include a cache and date labels in the UI.

------------------------------------------------------------------------

## 4) System Architecture (Spaces‑friendly)

**High Level** - **Data Ingestion (offline or startup):** fetch/copy
monthly usage, Showdown dex, type chart → save to `data/raw/` →
normalize into `data/processed/` (Parquet/JSON).\
- **Feature Layer:** type coverage (offense/defense), role tags (from
learnsets), meta matchup vs top‑K used mons.\
- **Recommender:** heuristic composite score + greedy/beam search over
top‑N candidates.\
- **UI:** Gradio app calling in‑memory Python functions.

**Spaces specifics** - **Space type:** Gradio • **Hardware:** CPU Basic
is fine.\
- **Build:** `requirements.txt` + optional `runtime.txt` (Python
version).\
- **Data:** commit lightweight JSON/CSV; for larger dumps, use `hf://`
dataset storage or on‑startup fetch with caching to `/home/user/.cache`.

    [Usage Stats]  [Dex/Moves]   ┐
                         ├──> Ingestion → Processed Tables → Feature Layer → Scorer → Top‑5 Trios
    [Kaggle (opt)]       ┘                                              │
                                                           Gradio UI on Spaces (single process)

------------------------------------------------------------------------

## 5) Data Model & Files

-   `data/raw/type_chart.json`: 18×18 effectiveness matrix.\
-   `data/raw/pokedex.json`: \[{ name, types, base_stats/speed,
    learnset\[\] }\].\
-   `data/raw/usage_ou.csv`: { name, usage_pct }.\
-   `data/processed/mon_features.parquet`: cached per‑mon features
    (types, roles, usage).\
-   `data/processed/meta_topk.json`: list of top‑K meta mons + usage
    weights.

------------------------------------------------------------------------

## 6) Scoring & Algorithms

**Composite Score**

    score = α·TypeCoverage + β·MetaCoverage + γ·RoleDiversity

**TypeCoverage (on the full 6)** - *Offense*: count defense‑types with
≥1 2× hitter via STAB (later: include top coverage moves from sample
sets).\
- *Defense*: penalize attack‑types where team has ≥2 weaknesses and 0
resist/immune.

**MetaCoverage** - For each top‑K used mon: does the team have ≥1 check?
(type interactions + speed threshold + common set proxy). Weight by
usage%.

**RoleDiversity** - Reward presence of hazards, removal, pivot, and
speed control (expand later to wallbreaker/cleric/status absorber).

**Search Strategy** - Candidate pool = top 100 by usage (after removing
inputs).\
- **MVP:** beam search (beam≈50) or greedy+lookahead; cache per‑mon
features.

**Phase 2 (ML Upgrades)** - Co‑usage graph + PMI/item‑item similarity.\
- Learn‑to‑rank (LightGBM) trained on sample teams and cores; negatives
by random sampling.\
- Metrics slice by archetype (rain/sun/balance/offense).

------------------------------------------------------------------------

## 7) Evaluation

**Offline** - Build a set of complete teams; create partials by hiding 3
members.\
- Metrics: Recall@10, MRR, NDCG.\
- Ablations: −MetaCoverage, −RoleDiversity, Heuristic vs Ranker.

**Qualitative** - Case studies vs known archetypes; human 1--5 ratings
for usefulness & clarity.

------------------------------------------------------------------------

## 8) Repository Layout

    pokemon-team-recommender/
    ├─ data/
    │  ├─ raw/
    │  └─ processed/
    ├─ src/
    │  ├─ data/          # loaders (dex, types, usage), caching
    │  ├─ features/      # coverage, roles, meta matchup
    │  ├─ search/        # greedy/beam search
    │  ├─ models/        # (phase 2) CF + LTR
    │  ├─ eval/          # metrics + offline eval
    │  └─ app/           # glue for Gradio UI
    ├─ app/              # gradio app entry point(s)
    ├─ notebooks/
    ├─ tests/
    ├─ requirements.txt
    ├─ runtime.txt       # optional (e.g., python-3.11)
    ├─ README.md
    └─ LICENSE

------------------------------------------------------------------------

## 9) Deployment (Hugging Face Spaces)

**Steps** 1) Create a **Gradio** Space.\
2) Push repo with `app/app.py`, `requirements.txt`, data files under
`data/`.\
3) Ensure startup caching (first run may download/normalize usage
stats).\
4) Turn on **"Persistent storage"** if using on‑disk caches (optional).\
5) Add **Space metadata**: tags (`pokemon`, `recommender`, `ml`),
license (MIT), README badge.

**Requirements example**

    gradio>=4.0
    pandas
    numpy
    scikit-learn
    lightgbm
    networkx
    pyarrow

**Secrets/Keys** - None needed for MVP. (Later: optional external data
fetch tokens.)

------------------------------------------------------------------------

## 10) Tooling & Dev Workflow

-   Vibe-code with Claude Code + Codex for scaffolds and refactors.\
-   `ruff`/`black`/`pytest` pre‑commit; GitHub Actions CI.\
-   Deterministic seeds for tests; small golden datasets committed.

------------------------------------------------------------------------

## 11) Milestones

**M1 --- MVP (Spaces‑ready)** - Seed data (dex, type chart, mini usage
CSV).\
- Coverage metrics, role tags, composite heuristic score.\
- Beam/greedy search over top‑60 candidates.\
- **Gradio UI** with Top‑5 trios + score breakdown + basic
explanations.\
- Deploy to **Spaces (CPU Basic)**.

**M2 --- Data Completeness** - Swap seed data for full Showdown dex +
monthly usage via @pkmn/smogon.\
- Meta matchup vs top‑15 mons; caching; tests.

**M3 --- Evaluation & Polish** - Offline Recall@10; ablations.\
- README: demo GIF, architecture diagram, metrics table.\
- UI tuning (sliders, export to Showdown).

**M4 --- ML Ranker (stretch)** - Co‑usage graph + LightGBM LTR; A/B
toggle in UI; ablation results.

------------------------------------------------------------------------

## 12) Testing & Performance

-   **Unit:** type multipliers, role detection, score math.\
-   **Property:** resist addition never increases defensive penalty;
    idempotent caching.\
-   **Integration:** fixed seed recommendations stable across runs.\
-   **Perf targets:** \<150 ms feature build (cached), \<1.5 s total
    search on 60 candidates.

------------------------------------------------------------------------

## 13) Risks & Mitigations

-   **Stale meta:** label month; add refresh script and UI dropdown.\
-   **Cold start in Spaces:** keep data vendored; cache processed
    artifacts.\
-   **Name/alias churn:** ship autocomplete from dex; fuzzy matching.

------------------------------------------------------------------------

## 14) Acceptance Criteria (Demo‑Ready)

-   Given `[Garchomp, Raging Bolt, Great Tusk]`, app returns **5 trios**
    with:
    -   Composite score + breakdown.\
    -   Role badges, coverage radar, meta heat strip.\
    -   "Export to Showdown" button.

------------------------------------------------------------------------

## 15) License & Attribution

-   MIT for code.\
-   Credits: Pokémon Showdown data, Smogon usage stats, @pkmn/smogon.

------------------------------------------------------------------------

## 16) Next Steps (Execution Plan)

1)  **Scaffold repo** with folders/files plus `requirements.txt`,
    `runtime.txt`.\
2)  **Implement loaders & features**: type chart, dex, usage;
    coverage/roles.\
3)  **Implement scorer + search** (beam or greedy).\
4)  **Build Gradio UI** (`app/app.py`) and test locally.\
5)  **Deploy to Spaces**; add README badges + demo GIF.\
6)  **Replace seed data** with monthly usage + full dex; add tests and
    caching.
