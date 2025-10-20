# Recommender Core Specification

## Overview
Implement the core recommendation engine that takes 3 user-provided Pokémon and recommends 3 additional team members based on type coverage, meta matchup, and role synergy using heuristic composite scoring and beam/greedy search.

## Problem Statement
Competitive Pokémon players often know 2-3 favorites or staple team members but struggle to complete a balanced 6-Pokémon team. They need data-driven recommendations that explain *why* certain Pokémon complete their team (type coverage gaps, meta threats, role diversity).

## User Stories

### As a Competitive Player
- I want to input my 3 favorite Pokémon and get 5 recommended trios so that I can see multiple viable team completion options
- I want each recommendation explained (type coverage, meta matchups, roles) so I understand why these Pokémon were suggested
- I want recommendations in under 2 seconds locally so the tool feels responsive

### As a Casual Player
- I want recommendations that make sense for the current competitive meta so my team is viable online
- I want to understand which threats my team can handle and which it struggles against

## Requirements

### Composite Scoring Algorithm

The recommendation score is a weighted sum of three components:

```
CompositeScore = α·TypeCoverage + β·MetaCoverage + γ·RoleDiversity
```

**Default Weights (MVP):**
- α (TypeCoverage) = 0.4
- β (MetaCoverage) = 0.4
- γ (RoleDiversity) = 0.2

(Phase 2: user-adjustable via Gradio sliders)

#### 1. TypeCoverage Score

**Offensive Coverage:**
- For each of the 18 defending types, check if the team has ≥1 Pokémon with STAB (Same Type Attack Bonus) super-effective move (2× multiplier)
- Score = (number of types covered) / 18
- Example: Team has Fire/Water/Electric types → covers Grass (Water), Steel (Fire), Flying (Electric), etc.

**Defensive Coverage:**
- For each of the 18 attacking types, penalize if the team has ≥2 weaknesses and 0 resists/immunities
- Penalty = (number of uncovered weaknesses) / 18
- Score = 1 - penalty
- Example: Team weak to Ground with no Ground resist → penalty increases

**Combined TypeCoverage:**
```
TypeCoverage = 0.6·OffensiveCoverage + 0.4·DefensiveCoverage
```

#### 2. MetaCoverage Score

**Definition:** Does the team have at least one check (counter or soft counter) to each top-K meta threat?

**Calculation:**
- For each of top-15 most-used Pokémon in the tier:
  - Check if any team member has type advantage + speed advantage OR bulk to survive
  - Use simplified heuristic: type matchup + speed threshold
- Weight each check by that meta Pokémon's usage percentage
- Score = Σ(usage_pct * has_check) / Σ(usage_pct)

**Example:**
- Top threat: Garchomp (15% usage, Ground/Dragon, 102 speed)
- Check: Team has Rillaboom (Grass type, resists Ground, STAB super-effective Grass move)
- Contribution: 0.15 * 1.0 = 0.15 to score

#### 3. RoleDiversity Score

**Key Roles (MVP):**
1. **Hazard Setter:** Learns Stealth Rock, Spikes, or Toxic Spikes
2. **Hazard Removal:** Learns Rapid Spin or Defog
3. **Pivot:** Learns U-turn, Volt Switch, or Flip Turn
4. **Speed Control:** Speed tier >120 OR learns priority moves OR learns Trick Room

**Calculation:**
- Score = (number of roles present) / 4
- Bonus: +0.1 if all 4 roles covered
- Example: Team has hazard setter + removal + pivot = 3/4 = 0.75

**Phase 2 Expansion:**
- Wallbreaker (high offensive stats)
- Cleric (learns Wish, Heal Bell, etc.)
- Status Absorber (immune to status or Guts/Magic Bounce ability)

### Search Strategy

**Candidate Pool:**
- Top 100 Pokémon by usage in selected tier (after removing user's 3 inputs)
- Fallback: If fewer than 100, use all available minus inputs

**Search Algorithm (MVP: Greedy with Lookahead):**
1. For each candidate trio (C(100, 3) = ~161k combinations):
   - Compute composite score for full team (3 inputs + 3 candidates)
2. Rank all trios by composite score
3. Return top 5

**Optimization (Beam Search for Faster Results):**
- Beam width = 50
- Iteratively build trio by adding one Pokémon at a time
- At each step, keep top-50 partial teams
- Prune low-scoring branches early

**Performance Target:**
- Greedy search on 161k combinations: **<1.5s** on local machine
- Beam search (if needed): **<800ms** on local machine
- Feature caching critical: precompute per-Pokémon features once

### Explainability

Each recommended trio must include:

1. **Composite Score Breakdown**
   - Overall score (0-1 scale)
   - Component scores: TypeCoverage, MetaCoverage, RoleDiversity
   - Example: `Score: 0.82 (Type: 0.75, Meta: 0.88, Roles: 0.85)`

2. **Role Badges**
   - Display which roles each Pokémon fills
   - Example: "Garchomp: Speed Control, Hazards | Rillaboom: Pivot, Hazard Removal"

3. **Coverage Summary**
   - Offensive: "Covers 16/18 types (missing: Fairy, Poison)"
   - Defensive: "Weak to Ice (2 members), Electric (1 member)"

4. **Meta Matchup Heat Map**
   - Visual indicator (green/yellow/red) for checks against top-15 meta threats
   - Example: "✓ Garchomp, ✓ Dragapult, ✗ Iron Valiant, ✓ Great Tusk..."

### Functional Requirements

1. **Input Validation**
   - Verify all 3 input Pokémon exist in Pokédex
   - Handle aliases/nicknames via fuzzy matching (e.g., "Lando-T" → "Landorus-Therian")
   - Reject invalid/duplicate inputs with helpful error message

2. **Tier Selection**
   - Default: Gen 9 OU
   - Support dropdown for other tiers (Gen 9 Ubers, UU, etc.)
   - Filter candidate pool by selected tier

3. **Recommendation Output**
   - Return exactly 5 trios (or fewer if insufficient candidates)
   - Each trio includes: 3 Pokémon names, composite score, breakdown, explanations
   - Sort by composite score descending (highest first)

4. **Deterministic Results**
   - Fixed random seed for search (if stochastic elements used)
   - Same inputs always produce same output (critical for testing)

### Performance Requirements
- Feature computation (cached): **<150ms**
- Search over 161k combinations: **<1.5s**
- Total recommendation time: **<2s** local, **<4s** on Spaces CPU Basic

### Error Handling
- If no valid trios found (e.g., only 2 candidates available): return empty result with explanation
- If data not loaded: return error message "Data not initialized. Please restart app."
- If computation exceeds timeout: return partial results + warning

## Acceptance Criteria
- [ ] Composite scoring algorithm implemented with configurable weights
- [ ] TypeCoverage calculation (offensive + defensive) correct per type chart
- [ ] MetaCoverage checks each meta threat with type/speed heuristic
- [ ] RoleDiversity detects 4 core roles from learnsets
- [ ] Search returns top-5 trios ranked by composite score
- [ ] Each trio includes score breakdown and explainability (roles, coverage, meta matchups)
- [ ] Performance targets met: <2s local, <4s on Spaces
- [ ] Deterministic results (fixed seed, same inputs → same outputs)
- [ ] Unit tests for scoring components (type math, role detection, meta checks)
- [ ] Integration test: given `[Garchomp, Raging Bolt, Great Tusk]`, returns sensible top-5 trios

## Out of Scope (MVP)
- User-adjustable weight sliders (hardcoded α, β, γ for MVP)
- Custom set inference (use type-based heuristics only, not specific movesets)
- Full battle simulation (simplified type/speed checks only)
- Multi-objective optimization (single composite score only)

## Dependencies
- Data pipeline (Pokédex, type chart, usage stats, processed features)
- Feature extraction (type coverage, role tags, meta threat list)
- Python packages: `numpy`, `pandas` for efficient computation
