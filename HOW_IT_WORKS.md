# How the Pokémon Team Recommender Works 🎮

A beginner-friendly explanation for junior engineers.

---

## 🤔 The Problem We're Solving

You have 3 Pokémon on your competitive team. You need 3 more to complete your team of 6. But which 3 should you pick from the hundreds of options?

**Our solution**: Score every possible trio and recommend the best ones.

---

## 🧠 Is This Machine Learning?

**Short answer: No, this is not ML.**

This is a **rule-based recommendation system** using:
- ✅ Domain knowledge (Pokémon game mechanics)
- ✅ Hand-crafted scoring functions
- ✅ Exhaustive search over combinations
- ❌ No neural networks
- ❌ No training data
- ❌ No learned weights

Think of it like a really smart calculator that knows Pokémon game rules.

---

## 🔍 How It Works: Step by Step

### Step 1: Load the Data

```python
pokedex = Pokedex()           # 15 Pokémon with stats, types, moves
type_chart = TypeChart()      # 18×18 grid of type matchups
usage_stats = UsageStats()    # How popular each Pokémon is
```

**What's happening?**
- We read JSON/CSV files containing Pokémon data
- This is just loading reference data, like loading a dictionary

---

### Step 2: Generate All Possible Trios

```python
input_team = ["Garchomp", "Raging Bolt", "Great Tusk"]  # User's 3 Pokémon
candidate_pool = top_100_most_used_pokemon()             # Filter to viable options

# Generate all combinations of 3 from the pool
for trio in combinations(candidate_pool, 3):
    # Example trio: ["Kingambit", "Gliscor", "Corviknight"]
    score = evaluate_team(input_team + trio)
```

**Math moment:**
- If we have 100 candidates, there are C(100,3) = 161,700 possible trios
- We evaluate ALL of them (exhaustive search)
- This is fast because 161,700 is small for computers (<1 second)

---

### Step 3: Score Each Team

For each potential 6-Pokémon team, we calculate 3 scores:

#### 🎯 Score #1: Type Coverage (40% weight)

**Goal**: Can we hit all 18 types super-effectively? Do we have shared weaknesses?

```python
# Offensive coverage
team_types = ["Dragon", "Ground", "Electric", "Dragon", "Ground", "Fighting"]
stab_moves = get_all_stab_moves(team)  # Same-Type Attack Bonus moves

types_we_can_hit = []
for move_type in stab_moves:
    for defending_type in ALL_18_TYPES:
        if is_super_effective(move_type, defending_type):
            types_we_can_hit.append(defending_type)

offensive_score = len(set(types_we_can_hit)) / 18  # 0.0 to 1.0
```

**Example:**
- If your team can hit 15/18 types super-effectively → `offensive_score = 0.83`
- If you can only hit 8/18 types → `offensive_score = 0.44`

```python
# Defensive coverage
shared_weaknesses = find_shared_weaknesses(team)
defensive_score = 1.0 - (penalty_for_shared_weaknesses)
```

**Example:**
- If 3+ Pokémon are weak to Ice → big penalty (bad!)
- If weaknesses are spread out → high score (good!)

```python
type_score = (offensive_score + defensive_score) / 2
```

---

#### ⚔️ Score #2: Meta Matchup (40% weight)

**Goal**: Can we beat the most popular threats?

```python
top_threats = get_top_15_most_used_pokemon()  # ["Dragapult", "Kingambit", ...]

counters = 0
for threat in top_threats:
    if team_can_check_threat(team, threat):
        counters += 1

meta_score = counters / 15  # 0.0 to 1.0
```

**How do we check if a team can beat a threat?**

```python
def team_can_check_threat(team, threat):
    for pokemon in team:
        # Method 1: Type advantage
        if has_super_effective_stab(pokemon, threat):
            return True

        # Method 2: Speed advantage
        if pokemon.speed > threat.speed * 1.1:
            return True

    return False
```

**Example:**
- Threat: Dragapult (Dragon/Ghost, 142 speed)
- Garchomp has Dragon moves → super-effective against Dragapult ✅
- Kingambit has Sucker Punch (priority) → can outspeed ✅

---

#### 🎭 Score #3: Role Diversity (20% weight)

**Goal**: Does the team have all the roles we need?

```python
IMPORTANT_ROLES = [
    "hazard_setter",    # Can set Stealth Rock
    "hazard_removal",   # Can use Defog/Rapid Spin
    "pivot",            # Can use U-turn/Volt Switch
    "speed_control"     # Fast or has priority moves
]

def detect_roles(pokemon):
    roles = []
    if "Stealth Rock" in pokemon.learnset:
        roles.append("hazard_setter")
    if "Defog" in pokemon.learnset or "Rapid Spin" in pokemon.learnset:
        roles.append("hazard_removal")
    if "U-turn" in pokemon.learnset:
        roles.append("pivot")
    if pokemon.speed >= 110:
        roles.append("speed_control")
    return roles

all_team_roles = set()
for pokemon in team:
    all_team_roles.update(detect_roles(pokemon))

role_score = len(all_team_roles) / 4  # 0.0 to 1.0
```

**Example:**
- Team has all 4 roles → `role_score = 1.0` ✅
- Team only has 2 roles → `role_score = 0.5` ⚠️

---

### Step 4: Combine Scores

```python
composite_score = (
    0.4 * type_score +      # 40% weight
    0.4 * meta_score +      # 40% weight
    0.2 * role_score        # 20% weight
)
```

**Example calculation:**

| Component | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
| Type Coverage | 0.85 | 40% | 0.34 |
| Meta Matchup | 0.73 | 40% | 0.29 |
| Role Diversity | 0.75 | 20% | 0.15 |
| **TOTAL** | | | **0.78** |

---

### Step 5: Rank and Return Top K

```python
# We've scored all 161,700 trios
all_recommendations = [
    Recommendation(trio=["Kingambit", "Gliscor", "Corviknight"], score=0.812),
    Recommendation(trio=["Rillaboom", "Gholdengo", "Zamazenta"], score=0.798),
    # ... 161,698 more ...
]

# Sort by score (highest first)
all_recommendations.sort(key=lambda x: x.score, reverse=True)

# Return top 5
return all_recommendations[:5]
```

---

## 🎯 Key Design Decisions

### Why not use Machine Learning?

1. **Small dataset**: Only 15 Pokémon in our dataset
   - ML needs thousands/millions of examples
   - We have too little data to train anything meaningful

2. **Clear rules exist**: Pokémon has well-defined game mechanics
   - Type effectiveness chart is exact (Fire → Grass = 2.0× damage)
   - Speed comparisons are simple math
   - Why learn patterns when we know the rules?

3. **Explainability**: Users can see exactly why a team scored well
   - "This trio covers 16/18 types and counters 12/15 meta threats"
   - ML models are often black boxes

4. **No training data**: We don't have a dataset of "good teams" vs "bad teams"
   - Would need thousands of labeled examples
   - Much easier to encode expert knowledge as rules

---

## 🏗️ Code Architecture

```
app.py (Gradio UI)
    ↓
recommender.py (Orchestrator)
    ↓
    ├─ coverage.py  (Type scoring)
    ├─ meta.py      (Meta matchup scoring)
    ├─ roles.py     (Role detection scoring)
    └─ Data loaders:
         ├─ pokedex.py    (Pokémon stats)
         ├─ types.py      (Type chart)
         └─ usage.py      (Popularity data)
```

### Flow:

```python
# 1. User input
input_team = ["Garchomp", "Raging Bolt", "Great Tusk"]

# 2. Get candidates
candidates = usage_stats.get_top_k(100)

# 3. Generate all trios
from itertools import combinations
all_trios = combinations(candidates, 3)  # 161,700 trios

# 4. Score each
results = []
for trio in all_trios:
    full_team = input_team + list(trio)

    type_score = coverage.score_type_coverage(full_team)
    meta_score = meta.score_meta_matchup(full_team)
    role_score = roles.score_role_diversity(full_team)

    composite = 0.4*type_score + 0.4*meta_score + 0.2*role_score

    results.append(Recommendation(trio, composite))

# 5. Sort and return top 5
results.sort(key=lambda x: x.composite_score, reverse=True)
return results[:5]
```

---

## 💡 Key Concepts for Junior Engineers

### 1. **Exhaustive Search**
- Try EVERY possibility and pick the best
- Works when search space is small (<1 million)
- Alternative: Heuristic search (faster but may miss optimal)

### 2. **Weighted Scoring**
- Combine multiple metrics with different importance
- `final = 0.4*A + 0.4*B + 0.2*C`
- Weights sum to 1.0 (40% + 40% + 20% = 100%)

### 3. **Domain Knowledge > ML Sometimes**
- If you understand the rules, encode them directly
- ML is powerful when rules are unclear or too complex
- Pokémon battling has clear, codifiable rules

### 4. **Data Structures Matter**
```python
# Fast lookup by name
pokemon_dict = {"Garchomp": Pokemon(...)}
mon = pokemon_dict["Garchomp"]  # O(1) lookup

# vs slow linear search
pokemon_list = [Pokemon(...), Pokemon(...), ...]
mon = [p for p in pokemon_list if p.name == "Garchomp"][0]  # O(n)
```

### 5. **Normalization**
- Always scale scores to 0.0-1.0 range
- Makes them comparable and combinable
- Example: `score = count / max_possible`

---

## 🚀 Performance

- **Time complexity**: O(C(n,3) × m) where n=candidates, m=team_size
  - C(100,3) = 161,700 combinations
  - Evaluating each team: ~O(6) operations
  - Total: ~1 million operations
  - **Result: <1 second** ⚡

- **Space complexity**: O(n)
  - Store all recommendations in memory
  - ~161,700 objects × ~100 bytes = ~16MB
  - Totally fine for modern computers

---

## 🔧 How to Extend This

Want to add more features? Here's how:

### Add a new scoring component:

```python
# src/features/synergy.py
def score_synergy(team):
    """Check for combos like Rain + Swift Swim."""
    synergy_count = 0

    # Check for weather setters + weather abusers
    has_rain_setter = any("Rain Dance" in p.learnset for p in team)
    has_swift_swim = any("Swift Swim" in p.abilities for p in team)

    if has_rain_setter and has_swift_swim:
        synergy_count += 1

    return synergy_count / 3  # Normalize to 0-1
```

### Update the composite score:

```python
# src/search/recommender.py
composite_score = (
    0.3 * type_score +      # Reduced from 40%
    0.3 * meta_score +      # Reduced from 40%
    0.2 * role_score +      # Same
    0.2 * synergy_score     # NEW!
)
```

---

## 📚 Further Reading

- **Type Chart**: `src/data/types.py` - How type effectiveness works
- **Role Detection**: `src/features/roles.py` - How we detect roles from movesets
- **Full Algorithm**: `ARCHITECTURE.md` - Deep technical dive

---

## ❓ Common Questions

**Q: Why not use a genetic algorithm?**
A: Genetic algorithms are great for huge search spaces. Our space (161,700) is small enough for exhaustive search, which guarantees finding the optimal solution.

**Q: Could we use ML to learn better weights?**
A: Yes! You could collect user feedback ("was this recommendation good?") and use regression to learn optimal weights. But with only 15 Pokémon, you'd need a lot of feedback data.

**Q: Why hardcode weights at 0.4, 0.4, 0.2?**
A: Based on competitive Pokémon knowledge. Type coverage and meta matchups are most important. Could be tuned based on user preferences.

**Q: What if I have 1000 Pokémon?**
A: C(1000,3) = 166 million combinations. Too slow for exhaustive search. Would need:
- Heuristic search (simulated annealing, hill climbing)
- Pruning (eliminate bad candidates early)
- Caching (memoize repeated calculations)
- Or... switch to ML! 😄

---

Made with 💙 for junior engineers learning recommendation systems!
