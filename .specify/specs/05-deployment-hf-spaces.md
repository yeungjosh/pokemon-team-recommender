# Hugging Face Spaces Deployment Specification

## Overview
Deploy the Pokémon Team Recommender as a public Gradio app on Hugging Face Spaces (CPU Basic tier), ensuring fast cold starts, proper data handling, and a polished user experience with demo assets.

## Problem Statement
Local development is straightforward, but deploying to Hugging Face Spaces introduces constraints: single-process runtime, CPU-only compute, cold start latency, and public visibility. The deployment must handle these gracefully while maintaining performance targets.

## User Stories

### As a Public User
- I want the app to load in under 4 seconds from a cold start so I don't abandon it
- I want to see a demo GIF or screenshot so I know what the app does before trying it
- I want clear instructions in the README so I can run it locally if needed

### As a Developer
- I want automated deployment via git push so I don't manually configure Spaces
- I want error logs accessible so I can debug issues without local reproduction
- I want dependencies pinned correctly so the app doesn't break on upstream updates

### As a Potential Contributor
- I want a clear README with architecture diagram and setup instructions so I can contribute
- I want a live demo link so I can try the app before cloning the repo

## Requirements

### Hugging Face Spaces Setup

#### 1. Space Configuration
- **Space Name:** `pokemon-team-recommender` (or `<username>/pokemon-team-recommender`)
- **SDK:** Gradio
- **Python Version:** 3.11 (specified in `runtime.txt`)
- **Hardware:** CPU Basic (free tier, sufficient for MVP)
- **Visibility:** Public

#### 2. Required Files

**`app.py` (or `app/app.py`):**
- Entry point for Gradio app
- Spaces auto-runs this file on startup
- Must call `demo.launch()` at the end

**`requirements.txt`:**
```
gradio>=4.0,<5.0
pandas>=2.0,<3.0
numpy>=1.24,<2.0
scikit-learn>=1.3,<2.0
pyarrow>=12.0,<14.0
networkx>=3.0,<4.0
```
- Pin major versions, allow minor/patch updates
- Keep dependencies minimal (no unnecessary packages)

**`runtime.txt` (optional but recommended):**
```
python-3.11
```
- Ensures consistent Python version
- Avoids breaking changes from Python 3.12+

**`README.md`:**
- See "README Requirements" section below

**`LICENSE`:**
- MIT License (per project spec)
- Include copyright notice

**`.gitignore`:**
- Exclude `.env`, `__pycache__`, `.DS_Store` (already created)

#### 3. Space Metadata (in README.md frontmatter)
```yaml
---
title: Pokémon Team Recommender
emoji: ⚔️
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
tags:
  - pokemon
  - recommender
  - machine-learning
  - competitive
  - team-building
---
```

### Data Handling on Spaces

#### 1. Data Files Strategy
**Small Data (< 5MB):** Commit directly to repo
- `data/raw/type_chart.json` (~10KB)
- `data/raw/pokedex.json` (~500KB)
- `data/raw/usage_ou.csv` (~100KB)

**Larger Data (5MB+):** Fetch-and-cache on first run
- Download from Hugging Face Datasets Hub (`hf://datasets/...`)
- Or fetch from public URL (Pokémon Showdown GitHub)
- Cache to `/home/user/.cache/pokemon_recommender/`
- Check cache on subsequent runs (avoid re-downloading)

#### 2. Cold Start Optimization
**Strategies:**
1. **Vendor Lightweight Data:** Commit processed Parquet files if under 5MB
2. **Progressive Loading:** Show UI immediately, fetch data in background
3. **Startup Progress Bar:** Display "Loading Pokédex... Loading usage stats... Ready!" messages
4. **Persistent Storage (Optional):** Enable Spaces persistent storage to survive rebuilds

**Target:** Cold start to interactive UI in **<4 seconds**

#### 3. Cache Management
```python
import os
from pathlib import Path

CACHE_DIR = Path("/home/user/.cache/pokemon_recommender")  # Spaces
if not CACHE_DIR.exists():
    CACHE_DIR = Path.home() / ".cache" / "pokemon_recommender"  # Local fallback
CACHE_DIR.mkdir(parents=True, exist_ok=True)
```

### README Requirements

**Sections to Include:**

#### 1. Header
- Project title with emoji
- Tagline: *"Complete your Pokémon team with data-driven recommendations"*
- Hugging Face Spaces badge: `[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/<username>/pokemon-team-recommender)`
- License badge: `[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)`

#### 2. Demo
- Embedded GIF or screenshot showing:
  - Input: 3 Pokémon entered
  - Output: Top-5 recommendations with scores
- Alt text for accessibility

#### 3. Features
- Bullet list:
  - Data-driven recommendations (type coverage, meta matchup, role synergy)
  - Explainable results (score breakdown, role badges)
  - Fast performance (<4s on Spaces)
  - Export to Pokémon Showdown format

#### 4. How to Use
- Step-by-step:
  1. Enter 3 Pokémon names
  2. Select competitive tier (default: Gen 9 OU)
  3. Click "Get Recommendations"
  4. View top-5 trios with explanations
  5. Export your favorite team to Pokémon Showdown

#### 5. Architecture
- High-level diagram (using Mermaid or ASCII art):
  ```
  [User Input] → [Data Pipeline] → [Feature Extraction] → [Recommender] → [Gradio UI]
                       ↓                   ↓                    ↓
                  [Pokédex]         [Type Coverage]      [Composite Score]
                  [Usage Stats]     [Role Tags]          [Beam Search]
  ```

#### 6. Local Development
- Setup instructions:
  ```bash
  git clone https://github.com/<username>/pokemon-team-recommender.git
  cd pokemon-team-recommender
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  python app.py
  ```

#### 7. Performance Metrics
- Table:
  | Metric | Target | Actual (MVP) |
  |--------|--------|-------------|
  | Cold Start | <4s | TBD |
  | Recommendation Time | <2s local, <4s Spaces | TBD |
  | Recall@10 | ≥0.35 | TBD |

#### 8. Data Attribution
- Pokémon Showdown: `https://github.com/smogon/pokemon-showdown`
- Smogon Usage Stats: `https://www.smogon.com/stats/`
- @pkmn/smogon API (if used)

#### 9. License
- MIT License with link to LICENSE file

#### 10. Contributing
- Brief guidelines:
  - Report bugs via GitHub Issues
  - Submit PRs with tests
  - Follow code quality standards (ruff, black, pytest)

### Deployment Process

#### 1. Create Hugging Face Space
- Go to `https://huggingface.co/new-space`
- Select Gradio SDK
- Name: `pokemon-team-recommender`
- Visibility: Public
- Initialize with README

#### 2. Connect Git Repository
```bash
# Add Hugging Face remote
git remote add hf https://huggingface.co/spaces/<username>/pokemon-team-recommender

# Push to Spaces
git push hf main
```

#### 3. Monitor Build Logs
- Check Spaces build logs for errors
- Common issues:
  - Missing dependencies in `requirements.txt`
  - Import errors (wrong Python version)
  - Data files not found (check paths)

#### 4. Test Deployed App
- Visit `https://huggingface.co/spaces/<username>/pokemon-team-recommender`
- Test all inputs:
  - Valid Pokémon: `[Garchomp, Raging Bolt, Great Tusk]`
  - Invalid Pokémon: `[Fakemon, ???, InvalidName]`
  - Edge cases: Duplicate Pokémon, empty inputs
- Verify performance meets targets (<4s cold start)

#### 5. Enable Persistent Storage (Optional)
- In Space settings, enable persistent storage
- Update cache path to `/data/cache/` (persistent across rebuilds)
- Benefit: Faster restarts (data survives Space sleep/rebuild)

### Error Handling & Logging

#### 1. Graceful Degradation
- If data fetch fails: Show error message "Data unavailable. Please try again later."
- If computation times out: Return partial results + warning
- If invalid input: Show specific error "Pokémon not found: [Name]. Did you mean [Suggestion]?"

#### 2. Logging
- Use Python `logging` module (not print statements)
- Log levels:
  - INFO: Data loaded, cache hit/miss, recommendation computed
  - WARNING: Slow computation, missing data, deprecated usage
  - ERROR: Data fetch failed, invalid state, computation crash
- Logs accessible in Spaces "Logs" tab

#### 3. User Feedback
- Add feedback mechanism (optional Phase 2):
  - Thumbs up/down on recommendations
  - Report issue button (links to GitHub Issues)

### Functional Requirements

1. **Automated Deployment:**
   - Push to `main` branch → Spaces auto-rebuilds
   - No manual configuration needed after initial setup

2. **Version Pinning:**
   - Pin major versions in `requirements.txt` to avoid breaking changes
   - Document tested versions in README

3. **Health Checks:**
   - Spaces auto-sleeps after inactivity → cold start expected
   - App must handle cold starts gracefully (don't assume warm state)

4. **Security:**
   - No secrets/API keys needed for MVP
   - If added (Phase 2), use Spaces Secrets (not hardcoded)

### Performance Requirements
- **Cold Start:** <4 seconds from Space wake to interactive UI
- **Warm Start:** <1 second to interactive UI (data already loaded)
- **Recommendation:** <4 seconds on Spaces CPU Basic
- **Page Load:** <2 seconds (HTML/CSS/JS assets)

### Acceptance Criteria
- [ ] Hugging Face Space created and configured (Gradio SDK, CPU Basic, Public)
- [ ] `app.py`, `requirements.txt`, `runtime.txt`, `LICENSE` committed to repo
- [ ] README includes demo GIF, architecture diagram, setup instructions, data attribution
- [ ] Space metadata in README frontmatter (title, emoji, tags, license)
- [ ] Git remote added: `hf` pointing to Spaces repo
- [ ] Push to `main` triggers automatic rebuild on Spaces
- [ ] Deployed app accessible at `https://huggingface.co/spaces/<username>/pokemon-team-recommender`
- [ ] Cold start completes in <4 seconds (verified by manual test)
- [ ] All test cases pass on deployed app (valid inputs, invalid inputs, edge cases)
- [ ] Logs show no errors during normal operation
- [ ] README includes live demo badge linking to deployed Space

## Out of Scope (MVP)
- Custom domain (use default `huggingface.co/spaces/...` URL)
- GPU support (CPU Basic sufficient for heuristic recommender)
- Multi-region deployment (Spaces runs in single region)
- A/B testing (no traffic splitting for MVP)
- Analytics/telemetry (no user tracking for MVP)

## Phase 2 Enhancements
- Persistent storage for faster restarts
- Analytics dashboard (user engagement metrics)
- Custom domain with branded URL
- Docker-based deployment (for advanced customization)
- GPU Space (if LightGBM model becomes expensive)
