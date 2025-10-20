# Evaluation Framework Specification

## Overview
Build a comprehensive evaluation system to measure recommendation quality using offline metrics (Recall@K, MRR, NDCG), ablation studies, and qualitative validation to ensure the recommender produces competitive, sensible teams.

## Problem Statement
Without rigorous evaluation, we cannot validate that recommendations are genuinely helpful or identify which components (type coverage, meta matchup, role diversity) contribute most to quality. We need automated metrics and human validation to iterate confidently.

## User Stories

### As a Developer
- I want to run offline evaluation on a test set so I can measure recommendation accuracy before shipping
- I want ablation studies to understand which scoring components matter most so I can prioritize improvements
- I want deterministic, reproducible metrics so I can track progress across iterations

### As a Project Owner
- I want confidence that recommendations beat a random baseline so I know the system adds value
- I want to compare heuristic scoring vs ML ranker (Phase 2) so I can justify complexity
- I want case studies against known team archetypes so I can validate domain correctness

## Requirements

### Test Set Construction

#### 1. Ground Truth Teams
- **Source:** Curated complete 6-Pokémon teams from:
  - Smogon sample teams (OU tier)
  - Tournament-winning teams (VGC, Smogon tournaments)
  - Popular content creator teams (with permission/attribution)
- **Size:** Minimum 100 complete teams for MVP
- **Format:** JSON array: `[{name, tier, team: [mon1, mon2, mon3, mon4, mon5, mon6], archetype}]`
- **Archetypes:** Hyperoffense (HO), Balance, Stall, Rain, Sun, Trick Room, etc.

#### 2. Partial Team Generation
- For each complete team, create test cases by hiding the last 3 Pokémon
- **Input:** First 3 Pokémon from team
- **Ground Truth:** Last 3 Pokémon (the trio to recover)
- **Example:**
  - Complete: `[Garchomp, Great Tusk, Raging Bolt, Rillaboom, Iron Valiant, Dragapult]`
  - Input: `[Garchomp, Great Tusk, Raging Bolt]`
  - Ground Truth: `[Rillaboom, Iron Valiant, Dragapult]`

#### 3. Negative Sampling (Optional - Phase 2)
- Generate "bad" trios as negative examples for ranking evaluation
- Strategy: Random sampling from top-100 usage (likely poor type coverage/role balance)

### Evaluation Metrics

#### 1. Recall@K
**Definition:** Proportion of test cases where the ground truth trio appears in top-K recommendations.

**Calculation:**
```python
recall_at_k = (num_cases_with_ground_truth_in_top_k) / total_test_cases
```

**Target Metrics (MVP):**
- Recall@5: ≥ 0.20 (ground truth in top-5 for 20% of test cases)
- Recall@10: ≥ 0.35 (ground truth in top-10 for 35% of test cases)

**Interpretation:**
- Low recall → recommendations miss known good teams (tune scoring)
- High recall → recommendations align with competitive team building

#### 2. Mean Reciprocal Rank (MRR)
**Definition:** Average of reciprocal ranks of first correct recommendation.

**Calculation:**
```python
MRR = (1 / total_test_cases) * Σ(1 / rank_of_first_correct_recommendation)
```

**Example:**
- Case 1: Ground truth at rank 3 → 1/3 = 0.33
- Case 2: Ground truth at rank 1 → 1/1 = 1.0
- Case 3: Ground truth not in top-10 → 0.0
- MRR = (0.33 + 1.0 + 0.0) / 3 = 0.44

**Target Metric (MVP):** MRR ≥ 0.25

**Interpretation:**
- Higher MRR → ground truth teams rank higher on average
- Sensitive to ranking quality (not just presence in top-K)

#### 3. Normalized Discounted Cumulative Gain (NDCG@K)
**Definition:** Ranking quality metric that rewards correct recommendations appearing higher in the list.

**Calculation:**
```python
DCG@K = Σ(relevance_i / log2(i + 1)) for i in 1..K
NDCG@K = DCG@K / IDCG@K  (normalized by ideal DCG)
```

**Relevance Scoring:**
- Ground truth trio: relevance = 1.0
- Partial overlap (2/3 Pokémon match): relevance = 0.5
- No overlap: relevance = 0.0

**Target Metric (MVP):** NDCG@10 ≥ 0.30

**Interpretation:**
- NDCG = 1.0 → perfect ranking (ground truth always at rank 1)
- NDCG closer to 0 → poor ranking (ground truth buried or missing)

### Ablation Studies

**Purpose:** Isolate impact of each scoring component.

**Experiments:**
1. **Baseline (All Components):** α=0.4, β=0.4, γ=0.2
2. **No Meta Coverage:** α=0.5, β=0.0, γ=0.5 (remove meta matchup)
3. **No Role Diversity:** α=0.5, β=0.5, γ=0.0 (remove role bonuses)
4. **Type Only:** α=1.0, β=0.0, γ=0.0 (pure type coverage)
5. **Random Baseline:** Randomly sample trios from top-100 usage

**Comparison:**
- Compute Recall@10, MRR, NDCG@10 for each experiment
- Statistical significance test (paired t-test or Wilcoxon)
- Visualize results in bar chart (metric vs experiment)

**Expected Results:**
- Baseline should outperform all ablations
- Random baseline should have lowest metrics (validates system adds value)
- Meta coverage likely most important (based on competitive meta importance)

### Qualitative Validation

#### 1. Case Studies
**Archetypes to Test:**
- Hyperoffense (HO): 5-6 attackers, minimal defensive backbone
- Balance: Mix of offensive and defensive Pokémon, good type synergy
- Stall: Defensive core with hazards and recovery
- Weather (Rain/Sun): Weather setter + abusers
- Trick Room: Slow, powerful attackers

**Validation:**
- Given known archetype partials, check if recommendations align with archetype
- Example: HO partial → should recommend fast attackers, not defensive walls

#### 2. Human Ratings
**Process:**
- Sample 20 test cases
- For each, show top-3 recommendations to competitive players
- Rating scale: 1-5 (1 = nonsensical, 3 = viable, 5 = excellent)
- Collect ratings from ≥3 raters per case

**Target Metric:** Average rating ≥ 3.5 (above "viable" threshold)

**Qualitative Questions:**
- "Does this trio make sense with the given input Pokémon?"
- "Would you consider using this team competitively?"
- "Is the explanation (type coverage, meta, roles) accurate and helpful?"

#### 3. Smoke Tests
**Predefined Test Cases:**
- Input: `[Garchomp, Raging Bolt, Great Tusk]`
  - Expected: Recommendations include Pokémon with Grass/Water types (cover weaknesses), hazard removal (Raging Bolt and Great Tusk don't have it)
- Input: `[Kyogre, Ferrothorn, Toxapex]` (Rain Stall)
  - Expected: Recommendations include Swift Swim abusers, defensive backbone
- Input: `[Torkoal, Venusaur, Hatterene]` (Sun + Trick Room)
  - Expected: Slow, powerful attackers that benefit from Sun

**Pass Criteria:** Top-5 recommendations include at least 2 sensible trios per test case

### Functional Requirements

#### 1. Evaluation Pipeline
- **Script:** `src/eval/run_evaluation.py`
- **Inputs:** Test set (JSON), recommender model, metric configs
- **Outputs:** Metrics JSON file, ablation comparison chart, case study report

#### 2. Reproducibility
- Fixed random seed for all stochastic elements (sampling, shuffling)
- Version control for test set (commit ground truth teams to repo)
- Log all hyperparameters (α, β, γ, beam width, candidate pool size)

#### 3. Reporting
- **Console Output:** Summary metrics (Recall@5, Recall@10, MRR, NDCG@10)
- **JSON Export:** Detailed per-case results for error analysis
- **Markdown Report:** Ablation comparison table, case study summaries, human ratings
- **Visualizations:** Bar charts (ablation), scatter plots (score vs metric), confusion matrix (archetype classification)

#### 4. Error Analysis
- Identify failure cases (ground truth not in top-10)
- Categorize failures:
  - Type coverage mismatch
  - Meta threat oversight
  - Role imbalance
  - Archetype confusion (e.g., recommended HO for Stall input)
- Log failure cases to `eval/failures.json` for manual review

### Performance Requirements
- Evaluation on 100 test cases: **<5 minutes** on local machine
- Ablation studies (5 experiments): **<20 minutes** total
- Metrics computation: **<10ms per test case**

### Dependencies
- Test set: Curated complete teams (JSON)
- Recommender core: For generating candidate trios
- Python packages: `scikit-learn` (for NDCG), `pandas` (for data wrangling), `matplotlib` or `plotly` (for visualizations)

## Acceptance Criteria
- [ ] Test set of ≥100 complete teams constructed and committed to repo
- [ ] Partial team generation script creates input/ground-truth pairs
- [ ] Recall@K, MRR, NDCG@K metrics implemented and tested
- [ ] Ablation studies run 5 experiments (baseline, -meta, -roles, type-only, random)
- [ ] Metrics comparison chart generated (bar chart: metric vs experiment)
- [ ] Baseline outperforms random baseline with statistical significance (p < 0.05)
- [ ] Smoke tests pass: predefined cases return sensible top-5 trios
- [ ] Case studies validate archetype alignment (HO, Balance, Stall, Weather)
- [ ] Human ratings collected (≥20 cases, ≥3 raters) with average rating ≥3.5
- [ ] Evaluation report generated (Markdown) with metrics, ablations, failure analysis
- [ ] All evaluation code deterministic (fixed random seed, reproducible results)

## Out of Scope (MVP)
- Online A/B testing (no user accounts for MVP)
- Multi-tier simultaneous evaluation (focus on Gen 9 OU for MVP)
- Cross-generation comparison (Gen 8 vs Gen 9)
- Real-time meta drift monitoring (monthly snapshots sufficient)

## Phase 2 Enhancements
- Learn-to-rank (LightGBM) model evaluation vs heuristic baseline
- Feature importance analysis (which features drive ranking quality)
- User feedback loop (implicit signals: which recommendations clicked/exported)
- Archetype-specific metrics (evaluate HO recommendations separately from Stall)
