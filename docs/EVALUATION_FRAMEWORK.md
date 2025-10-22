# Evaluation Framework: How We Measure Success

## Table of Contents

- [Overview](#overview)
- [Why Evaluation is Critical](#why-evaluation-is-critical)
- [How We Evaluate](#how-we-evaluate)
- [Evaluation Metrics Explained](#evaluation-metrics-explained)
- [Test Data](#test-data)
- [Running Evaluations](#running-evaluations)
- [Interpreting Results](#interpreting-results)
- [Best Practices](#best-practices)

---

## Overview

The evaluation framework is a comprehensive testing system that scientifically measures how well the Pokémon Team Recommender performs. It answers the fundamental question: **"Is this recommender actually good?"**

Think of it as a **grading system** for your AI - without it, you're just guessing if your model works.

---

## Why Evaluation is Critical

### 1. Machine Learning Models Are Black Boxes

Unlike traditional code where you can read the logic, ML models are opaque systems with thousands of learned parameters. The **only way** to know if they work is to test them rigorously.

```python
# Traditional: You can see exactly what it does
def is_prime(n):
    if n < 2: return False
    return all(n % i != 0 for i in range(2, n))

# ML: 10,000 parameters - impossible to inspect
model = train_neural_network(data)
# Does it work? You MUST test to find out.
```

### 2. Preventing Overfitting

**Overfitting** is when a model "memorizes" training data instead of learning patterns:

| Scenario | Training Accuracy | Test Accuracy | Result |
|----------|-------------------|---------------|---------|
| **Bad Model (Overfitting)** | 99% | 35% | ❌ Memorized, doesn't generalize |
| **Good Model** | 85% | 82% | ✅ Actually learned patterns |

**Our solution:** Always evaluate on separate test data the model has never seen.

### 3. Objective Comparison

Without metrics, you can't compare approaches objectively:

**Before evaluation framework:**
- "I think the neural network is better!"
- "Based on what?"
- "Uh... it feels more sophisticated?"

**After evaluation framework:**

| Approach | Recall@3 | MRR | Speed | Winner? |
|----------|----------|-----|-------|---------|
| Rule-based | 0.65 | 0.52 | 50ms | |
| Neural Net | 0.71 | 0.59 | 200ms | |
| LightGBM | 0.73 | 0.61 | 80ms | ✅ Best balance |
| Hybrid | 0.72 | 0.60 | 150ms | |

Now you can make **data-driven decisions**.

### 4. Continuous Improvement

Evaluation enables the scientific method:

```
1. Build baseline model
2. Measure performance (Recall@3 = 0.65)
3. Make improvement
4. Measure again (Recall@3 = 0.71) ✅ +9%!
5. Repeat
```

Without step 2 and 4, you're just randomly changing things and hoping.

### 5. Catching Regressions

Code changes can accidentally make things worse:

**Without evaluation:**
```
Week 1: Deploy "improvement"
Week 2: Users complain
Week 3: Discover accuracy dropped from 75% → 40%
Week 4: No idea what caused it
```

**With evaluation:**
```
Before change: Recall@3 = 0.75
After change:  Recall@3 = 0.71 ⚠️
Alert: Regression detected! Don't deploy.
```

### 6. Understanding Failure Modes

Aggregate metrics hide important patterns:

**Shallow evaluation:**
- "Overall: 80% accuracy"
- "Ship it!" ❌

**Deep evaluation:**

| Archetype | Recall@3 | Analysis |
|-----------|----------|----------|
| Hyper Offense | 92% | ✅ Excellent |
| Balance | 85% | ✅ Good |
| **Stall** | **45%** | ❌ **Broken!** |
| Rain | 88% | ✅ Good |

**Insight:** Model fails at stall teams → collect more stall training data.

---

## How We Evaluate

### Step 1: Create Test Data

We curated **105 real competitive Pokémon teams** across 7 archetypes:

- **Balance** (20 teams): Mix of offense and defense
- **Hyper Offense** (20 teams): Aggressive sweepers
- **Stall** (15 teams): Ultra-defensive cores
- **Rain** (15 teams): Weather-based offense
- **Sun** (10 teams): Solar Power/Chlorophyll abuse
- **Bulky Offense** (15 teams): Tanky attackers
- **Screens** (10 teams): Light Screen/Reflect setup

Each team is split into:
- **Input:** First 3 Pokémon (what user provides)
- **Ground Truth:** Last 3 Pokémon (correct answer)

**Example:**
```json
{
  "input": ["Garchomp", "Great Tusk", "Raging Bolt"],
  "ground_truth": ["Rillaboom", "Iron Valiant", "Dragapult"]
}
```

### Step 2: Run Recommender

For each test case:
1. Feed the 3 input Pokémon to the recommender
2. Get back ranked list of recommendations
3. Compare recommendations to ground truth
4. Calculate metrics

### Step 3: Calculate Metrics

We compute multiple metrics to measure different aspects of quality:

- **Recall@K:** Did we find the right Pokémon?
- **MRR:** How high did we rank them?
- **NDCG@K:** Is the ranking order good?
- **Precision@K:** What fraction of our guesses were right?

### Step 4: Aggregate Results

Average metrics across all 105 test cases to get overall performance.

---

## Evaluation Metrics Explained

### Recall@K

**Definition:** Fraction of ground truth items found in top K recommendations.

**Formula:**
```
Recall@K = (# correct items in top K) / (# total correct items)
```

**Example:**
- Ground truth: [A, B, C]
- Predictions: [A, D, B, E, F]
- Recall@3: Found A and B in top 3 → 2/3 = **0.667**

**Why it matters:** Measures if you're finding the right Pokémon at all.

**Good score:** >0.60 for Recall@3

---

### Mean Reciprocal Rank (MRR)

**Definition:** Average of reciprocal ranks where correct items appear.

**Formula:**
```
MRR = (1/|ground_truth|) × Σ(1/rank_i) for each correct item
```

**Example:**
- Ground truth: [A, B]
- Predictions: [C, A, D, B]
- A appears at rank 2 → 1/2 = 0.5
- B appears at rank 4 → 1/4 = 0.25
- MRR = (0.5 + 0.25) / 2 = **0.375**

**Why it matters:** Rewards putting correct items at the top. Finding the right Pokémon at position #1 is way better than position #10.

**Good score:** >0.50 for MRR

---

### Normalized Discounted Cumulative Gain (NDCG@K)

**Definition:** Measures ranking quality with position-based discounting.

**How it works:**
- Items at top positions get more weight
- Correct item at position #1 is much more valuable than at position #5
- Normalized so perfect ranking = 1.0

**Example:**
- Ground truth: [A, B, C]
- Perfect ranking: [A, B, C, ...] → NDCG = 1.0
- Good ranking: [A, D, B, C] → NDCG = 0.93
- Bad ranking: [D, E, A, B, C] → NDCG = 0.52

**Why it matters:** Ranking order matters - users look at top results first.

**Good score:** >0.65 for NDCG@3

---

### Precision@K

**Definition:** Fraction of top K recommendations that are correct.

**Formula:**
```
Precision@K = (# correct items in top K) / K
```

**Example:**
- Ground truth: [A, B, C]
- Predictions: [A, D, B, E, F]
- Precision@3: 2 correct out of 3 shown → 2/3 = **0.667**

**Why it matters:** Measures accuracy of what you're showing users. High precision = fewer wrong suggestions.

**Good score:** >0.50 for Precision@3

---

### Exact Match@K

**Definition:** Binary metric - 1.0 if ALL ground truth items are in top K, else 0.0.

**Example:**
- Ground truth: [A, B, C]
- Predictions: [A, B, C, D, E] → Exact Match@3 = **1.0** ✅
- Predictions: [A, B, D, C, E] → Exact Match@3 = **0.0** ❌

**Why it matters:** Measures perfect recommendations. Strictest metric.

**Good score:** >0.20 for Exact Match@3 (this is hard!)

---

## Test Data

### Archetype Distribution

| Archetype | # Teams | Purpose |
|-----------|---------|---------|
| Balance | 20 | Test general competence |
| Hyper Offense | 20 | Test aggressive synergies |
| Stall | 15 | Test defensive understanding |
| Rain | 15 | Test weather team knowledge |
| Sun | 10 | Test weather team knowledge |
| Bulky Offense | 15 | Test tanky cores |
| Screens | 10 | Test setup strategies |
| **Total** | **105** | Comprehensive coverage |

### Why These Archetypes?

1. **Balance:** Most common archetype, tests core functionality
2. **Hyper Offense:** Tests if model understands offensive synergy
3. **Stall:** Tests if model handles defensive cores
4. **Weather teams:** Tests specialized strategy knowledge
5. **Bulky Offense:** Tests middle-ground between offense/defense
6. **Screens:** Tests setup sweeper understanding

### Data Quality

All teams are:
- ✅ Competitively viable (Gen 9 OU)
- ✅ Hand-curated by competitive players
- ✅ Diverse across archetypes
- ✅ Realistic team compositions

---

## Running Evaluations

### Quick Evaluation (Smoke Test)

Test on small subset for rapid iteration:

```bash
# Generate test data
python scripts/generate_partial_teams.py

# Run on 5 smoke tests (~2 minutes)
python -m src.eval.run_evaluation \
    --test-set data/test_sets/smoke_partial_teams.json \
    --output results/smoke_eval.json \
    --top-k 5
```

### Full Evaluation

Run on all 105 test cases for comprehensive results:

```bash
python -m src.eval.run_evaluation \
    --test-set data/test_sets/partial_teams.json \
    --output results/full_eval.json \
    --top-k 10
```

**Expected runtime:** ~10-15 minutes for 105 test cases

### Custom Weight Evaluation

Test specific scoring weights:

```bash
python -m src.eval.run_evaluation \
    --test-set data/test_sets/partial_teams.json \
    --type-weight 0.5 \
    --meta-weight 0.3 \
    --role-weight 0.2
```

### Ablation Studies

Test multiple weight configurations to find the best:

```bash
python -m src.eval.run_ablations \
    --test-set data/test_sets/partial_teams.json \
    --output results/ablations.json \
    --report results/ablation_report.md
```

This tests 8 configurations:
- Baseline (α=0.4, β=0.4, γ=0.2)
- Type-only, Meta-only, Role-only
- Type+Meta, Type+Role, Meta+Role
- Equal weights

### Generate Report

Create comprehensive markdown report:

```bash
python -m src.eval.generate_report \
    --results results/full_eval.json \
    --ablations results/ablations.json \
    --output results/evaluation_report.md
```

The report includes:
- Overall metrics
- Performance by archetype
- Challenging test cases
- Ablation study comparison
- Recommendations

---

## Interpreting Results

### What's a Good Score?

| Metric | Poor | Fair | Good | Excellent |
|--------|------|------|------|-----------|
| Recall@3 | <0.40 | 0.40-0.60 | 0.60-0.75 | >0.75 |
| MRR | <0.30 | 0.30-0.50 | 0.50-0.65 | >0.65 |
| NDCG@3 | <0.40 | 0.40-0.60 | 0.60-0.75 | >0.75 |
| Precision@3 | <0.30 | 0.30-0.50 | 0.50-0.70 | >0.70 |
| Exact Match@3 | <0.10 | 0.10-0.20 | 0.20-0.35 | >0.35 |

### Example Results

```
Aggregated Metrics (105 test cases):
  Avg MRR: 0.52
  Avg Recall@3: 0.65
  Avg NDCG@3: 0.61
  Avg Precision@3: 0.48
  Avg Exact Match@3: 0.15
```

**Interpretation:**
- ✅ **Recall@3 = 0.65:** Good! Finding 65% of correct Pokémon
- ✅ **MRR = 0.52:** Fair, correct items ranked moderately high
- ✅ **NDCG@3 = 0.61:** Good ranking quality
- ⚠️ **Precision@3 = 0.48:** Fair, some wrong suggestions
- ⚠️ **Exact Match@3 = 0.15:** Low, perfect recommendations are rare (this is normal)

### Red Flags

**⚠️ High training, low test:**
```
Training Recall: 0.95
Test Recall: 0.45
```
→ **Overfitting!** Model memorized training data.

**⚠️ Performance degrades:**
```
Last week: Recall@3 = 0.70
This week: Recall@3 = 0.55
```
→ **Regression!** Recent change broke something.

**⚠️ Unbalanced by archetype:**
```
Offense: 0.85
Stall:   0.30
```
→ **Bias!** Model doesn't understand defensive teams.

---

## Best Practices

### 1. Always Use Separate Test Data

❌ **Don't:**
```python
# Train and test on same data
train(data)
evaluate(data)  # Will report inflated scores!
```

✅ **Do:**
```python
# Split data
train_data, test_data = split(data, 0.8)
train(train_data)
evaluate(test_data)  # Honest scores
```

### 2. Evaluate Early and Often

- ✅ After every major change
- ✅ Before deploying to production
- ✅ When tuning hyperparameters
- ✅ When comparing approaches

### 3. Look Beyond Aggregate Metrics

Don't just check overall scores - dig into:
- Performance by archetype
- Hardest test cases
- Error patterns

### 4. Use Multiple Metrics

Each metric captures different aspects:
- **Recall:** Are we finding the right items?
- **MRR:** Are we ranking them well?
- **NDCG:** Is the order good?
- **Precision:** Are we avoiding bad suggestions?

Use all of them together for complete picture.

### 5. Set Minimum Thresholds

Before deploying:
```
Requirements:
- Recall@3 > 0.60
- MRR > 0.50
- No archetype < 0.40 recall
- Prediction time < 2000ms
```

### 6. Track Metrics Over Time

Keep history:
```
v1.0: Recall@3 = 0.55
v1.1: Recall@3 = 0.61 (+11%)
v1.2: Recall@3 = 0.65 (+6%)
v2.0: Recall@3 = 0.71 (+9%)
```

This shows you're making progress!

### 7. Test Edge Cases

Include challenging scenarios:
- Uncommon archetypes
- Weird type combinations
- Low usage Pokémon
- Niche strategies

---

## Summary

**Why we built this:**
- ML models are black boxes - testing is the only way to know they work
- Prevents overfitting and regressions
- Enables objective comparison and continuous improvement
- Builds trust through scientific rigor

**What we measure:**
- **Recall@K:** Finding the right Pokémon
- **MRR:** Ranking quality
- **NDCG@K:** Position-aware ranking
- **Precision@K:** Accuracy
- **Exact Match:** Perfect recommendations

**How to use it:**
1. Run evaluation on test set
2. Check metrics against thresholds
3. Identify weak areas
4. Make improvements
5. Evaluate again
6. Repeat

**Remember:** In ML, "what gets measured gets improved." The evaluation framework is your compass for building better recommenders scientifically! 🎯

---

## Further Reading

- [Information Retrieval Metrics](https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval))
- [NDCG Explained](https://en.wikipedia.org/wiki/Discounted_cumulative_gain)
- [Overfitting in Machine Learning](https://en.wikipedia.org/wiki/Overfitting)
- [Cross-Validation Techniques](https://en.wikipedia.org/wiki/Cross-validation_(statistics))
