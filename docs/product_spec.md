# Pokémon Team Recommender — Product Spec & Design Doc

## 1. Problem Statement & Goals
- **Problem:** Players often have 2–3 staples but struggle to complete a balanced team.
- **Goal:** Recommend three Pokémon that maximize coverage, meta matchup, and role synergy with transparent scoring explanations.
- **Success Criteria:**
  - Input three Pokémon → respond with top five trios, including score breakdowns, in <2 s locally / <4 s on Spaces CPU.
  - Trio cards show Type, Meta, Role scores, plus rationale.
  - Repository ships with tests, an evaluation notebook, and a live Hugging Face Space demo linked in the README.
- **Non-Goals:** Battle simulation, set inference, accounts, private log scraping.

## 2. User Stories & UX
- **Personas:** Ladder player, curious recruiter.
- **Flow:** Provide three names (or Showdown import) → click Recommend → see ranked trios. Optional sliders for weighting. Export final 6.
- **UI:** Gradio inputs (text fields with autocomplete, tier dropdown, sliders). Output cards include badges, coverage radar, meta heat strip.

## 3. Data Sources & Ethics
- **Data:** Pokémon Showdown dex snapshot, Smogon usage stats, optional Kaggle snapshots.
- **Ethics:** Use public data with attribution, avoid private logs, respect licenses, surface cache/date info in UI.

## 4. System Architecture (Spaces-Friendly)
```
Usage Stats  Dex/Moves     ┐
                 ├─> Ingestion → Processed Tables → Feature Layer → Scorer → Top-5 Trios
Kaggle (opt)     ┘                                          │
                                              Gradio UI on Spaces
```
- Single-process Gradio Space with vendored data + caching.

## 5. Data Model & Files
- `data/raw/`: `type_chart.json`, `pokedex.json`, `usage_ou.csv`.
- `data/processed/`: `mon_features.parquet` (future), `meta_topk.json`.

## 6. Scoring & Algorithms
- Composite score = α·TypeCoverage + β·MetaCoverage + γ·RoleDiversity.
- TypeCoverage: Offensive + defensive heuristics.
- MetaCoverage: Check coverage against top-K usage mons.
- RoleDiversity: Reward hazards, removal, pivoting, speed control.
- Search: Candidate pool top 100; greedy/beam search cached features.

## 7. Evaluation
- **Offline:** Hide 3 mons from completed teams → metrics (Recall@10, MRR, NDCG).
- **Qualitative:** Case studies, human ratings.

## 8. Repository Layout
```
pokemon-team-recommender/
├─ data/
│  ├─ raw/
│  └─ processed/
├─ src/
│  ├─ data/
│  ├─ features/
│  ├─ search/
│  ├─ models/
│  ├─ eval/
│  └─ app/
├─ app/
├─ notebooks/
├─ tests/
├─ requirements.txt
├─ runtime.txt
├─ README.md
└─ LICENSE
```

## 9. Deployment (Hugging Face Spaces)
- Gradio Space on CPU Basic, vendored data, optional persistent storage.
- Provide requirements.txt, runtime.txt, caching on startup.

## 10. Tooling & Workflow
- Preferred stack: ruff/black/pytest pre-commit, GitHub Actions CI, deterministic seeds.

## 11. Milestones
1. **M1 (MVP):** Seed data, coverage metrics, composite score, UI with top-5 trios, deploy to Spaces.
2. **M2:** Full dex + monthly usage ingestion, meta matchup expansion, caching, tests.
3. **M3:** Offline metrics, README polish, UI tuning.
4. **M4:** ML ranker (LightGBM), co-usage graph, UI toggle.

## 12. Testing & Performance Targets
- Unit tests for type multipliers, role detection, scoring math.
- Integration: deterministic recommendations.
- Performance: <150 ms feature build (cached), <1.5 s search over 60 candidates.

## 13. Risks & Mitigations
- Stale meta → month labeling + refresh script.
- Cold start → vendor data, cache processed artifacts.
- Name churn → autocomplete, fuzzy matching.

## 14. Acceptance Criteria (Demo-Ready)
- Example input `[Garchomp, Raging Bolt, Great Tusk]` returns five trios with scores, badges, coverage radar, meta strip, Showdown export.

## 15. License & Attribution
- MIT license, credit Pokémon Showdown, Smogon, @pkmn/smogon.

## 16. Next Steps
1. Scaffold repo.
2. Implement loaders, features, scorer.
3. Build Gradio UI.
4. Deploy to Spaces.
5. Replace seed data, add tests + caching.
