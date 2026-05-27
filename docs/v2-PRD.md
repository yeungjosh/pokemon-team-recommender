# PRD: Pokemon Team Recommender v2

**Status:** Draft
**Target:** Q3 2026

---

## Problem

v1 was trained on **10,000 synthetic teams** generated under hand-designed constraints (type coverage, role diversity, meta matchup heuristics). The [pokemon-real-data-experiment](https://github.com/yeungjosh/pokemon-real-data-experiment) validation study against **~5,000 real Pokémon Showdown battles** found a systematic bias:

| Feature | v1 weight | Real-data weight | Direction |
|---|---|---|---|
| Meta matchup | 53.3% | ~15% | **Overestimated by 38 pts** |
| Type coverage | 17.1% | ~17% | Roughly correct |
| Role diversity | 26.4% | ~8% | Overestimated |
| Raw stats (bulk + speed) | 3.2% | ~62% | **Underestimated by ~60 pts** |

In short: the synthetic generator over-rewarded strategic factors that *look* important to humans, and under-rewarded the brute-force statistical predictors (bulk + speed) that real ladder battles actually turn on. Users who follow v1's recommendations build teams that look meta-correct but underperform.

## Hypothesis

Retraining on real battle outcomes — not synthetic constraint satisfaction — will recalibrate feature weights toward what actually predicts wins. Expected: top-3 recommendation win rate on held-out real battles improves by ≥ 10 percentage points over v1.

## Goals

1. **Train on real data.** Source: 50,000+ Showdown replays in gen9ou and gen1ou. Label = battle outcome, not constraint satisfaction.
2. **Recalibrate feature weights.** Targets per the validation study: stats ~55–65%, type ~15–20%, meta ~10–15%, role ~5–10%.
3. **Add explainability.** Per-recommendation feature attribution (SHAP), surfaced in the Gradio UI. v1 only exposes global feature importance, post-hoc.
4. **Preserve the UX.** Same 3 → 6 completion flow, same < 2s inference budget, same Hugging Face Spaces deployment.

## Non-goals

- Real-time meta tracking (separate project)
- Move-set recommendation (current scope is team composition only)
- Mobile app, accounts, history — privacy-first stays

## Success metrics

| Metric | v1 baseline | v2 target |
|---|---|---|
| Top-3 recommendation win rate on held-out replays | ~52% (estimated) | ≥ 62% |
| Inference time | 1.5s | ≤ 1.5s |
| Model size | 76 KB | ≤ 500 KB |
| Feature importance drift vs. real-data study | 38pt overestimate on meta | ≤ 10pt drift |

## Approach

**Stage 1 — Data pipeline.** Pull 50K replays from Pokémon Showdown. Filter to gen9ou + gen1ou. Extract `(team_a, team_b, winner)` triples. Filter to mid-Elo bracket (1400–1800) for a defensible "average competitive" target audience.

**Stage 2 — Feature re-engineering.** Add explicit `bulk_score` (HP × min(Def, SpD)) and `speed_tier` features. Drop or down-weight constraint-derived meta features. Cross-check feature importances against `pokemon-real-data-experiment`.

**Stage 3 — Model.** Same LightGBM family for inference budget. Try XGBoost as a comparison; promote only if it materially improves AUC.

**Stage 4 — Validation.** Replay-level held-out test set (10K replays, time-disjoint from training). Compare top-3 recommendation win rate to v1.

**Stage 5 — Explainability.** SHAP values per recommendation. Surface the top 2–3 driving features in the Gradio UI alongside each suggested Pokémon.

## Risks

1. **Replay data quality.** Showdown replays are noisy — ladder Elo varies wildly across players. Mitigation: Elo filter (1400–1800), time-windowed sampling.
2. **Format drift.** Gen 9 OU meta shifts with bans/unbans. Mitigation: timestamp every replay, retrain on a rolling 6-month window.
3. **Scope drift into [pokechamp](https://github.com/yeungjosh/pokechamp) territory.** This is a *team builder*, not a battle agent. Recommendation only — no in-battle decisions.

## Open questions

- Ship gen1 + gen9 from day one, or gen9-only first?
- Deprecate v1 immediately, or run both in parallel for A/B?
- Move-set recommendation: spin out as v3, or fold in if cheap?

## Related work in this portfolio

- [pokemon-team-recommender (v1)](https://github.com/yeungjosh/pokemon-team-recommender) — the current model, this doc's subject
- [pokemon-real-data-experiment](https://github.com/yeungjosh/pokemon-real-data-experiment) — the validation study that motivated v2
- [pokemon-cf-recommender](https://github.com/yeungjosh/pokemon-cf-recommender) — alternative item-item CF approach, no domain knowledge required
- [pokechamp](https://github.com/yeungjosh/pokechamp) — battle-time agent (different scope, but shares the gen1/gen9 format coverage)
