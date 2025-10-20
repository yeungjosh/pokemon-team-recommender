# Gradio UI Specification

## Overview
Build an intuitive Gradio web interface that allows users to input 3 Pokémon, configure recommendation parameters, and view top-5 recommended trios with detailed explanations and visualizations.

## Problem Statement
The recommendation engine produces complex data (scores, type matchups, role distributions, meta checks). Users need a clean, responsive UI that makes this information accessible and actionable without overwhelming them.

## User Stories

### As a New User
- I want to see an example/placeholder input so I understand what format to use for Pokémon names
- I want autocomplete suggestions when typing Pokémon names so I don't have to remember exact spellings
- I want to see results load in under 4 seconds so the app feels responsive

### As a Competitive Player
- I want to see why each trio was recommended (type coverage, meta matchups, roles) so I can evaluate the suggestions
- I want to export recommended teams to Pokémon Showdown format so I can test them immediately
- I want to compare multiple recommendations side-by-side so I can choose the best fit

### As a Mobile User
- I want the UI to work on mobile devices so I can use it on the go
- I want clear, readable text and visualizations that adapt to small screens

## Requirements

### Input Section

#### 1. Pokémon Inputs (3 Text Fields)
- **Component:** `gr.Textbox` with autocomplete
- **Labels:** "Pokémon 1", "Pokémon 2", "Pokémon 3"
- **Placeholder Examples:**
  - Pokémon 1: "Garchomp"
  - Pokémon 2: "Raging Bolt"
  - Pokémon 3: "Great Tusk"
- **Autocomplete:** Dropdown suggestions from Pokédex (fuzzy matching)
- **Validation:**
  - Show error if Pokémon not found in Pokédex
  - Show warning if duplicate Pokémon entered
  - Clear invalid inputs with red border

#### 2. Tier Selection (Dropdown)
- **Component:** `gr.Dropdown`
- **Label:** "Competitive Tier"
- **Options:** Gen 9 OU (default), Gen 9 Ubers, Gen 9 UU, Gen 9 RU, Gen 9 NU
- **Info Text:** "Meta snapshot: [Month Year] (e.g., October 2024)"

#### 3. Advanced Options (Collapsible - Phase 2)
- **Weight Sliders (0.0 - 1.0):**
  - Type Coverage Weight (α): default 0.4
  - Meta Coverage Weight (β): default 0.4
  - Role Diversity Weight (γ): default 0.2
- **Normalization:** Weights auto-normalize to sum to 1.0
- **Reset Button:** Restore defaults

#### 4. Action Button
- **Component:** `gr.Button`
- **Label:** "Get Recommendations"
- **State Changes:**
  - Click → "Loading..." (disabled)
  - Complete → "Get Recommendations" (re-enabled)
- **Loading Indicator:** Spinner overlay during computation

### Output Section

#### 1. Recommendation Cards (Top-5 Trios)

Each card displays:

**Header:**
- **Rank:** #1, #2, #3, #4, #5
- **Composite Score:** 0.85 (large, prominent)
- **Component Breakdown:** Type: 0.82 | Meta: 0.88 | Roles: 0.85

**Pokémon Row:**
- Display 3 Pokémon names with sprite icons (if available)
- Example: "Garchomp | Rillaboom | Iron Valiant"

**Role Badges:**
- Color-coded badges for each role detected
- Example: 🛡️ Hazard Setter | 🌀 Pivot | ⚡ Speed Control | 🧹 Hazard Removal

**Type Coverage Summary:**
- **Offensive:** "Covers 16/18 types (Missing: Fairy, Poison)"
- **Defensive:** "Weak to: Ice ×2, Electric ×1 | Resists: Water, Fire, Ground"

**Meta Matchup Strip:**
- Compact visual: green ✓ for check, red ✗ for no check
- Hover tooltips: "✓ Garchomp (Rillaboom checks with Grass STAB)"
- Example: `✓ Garchomp | ✓ Dragapult | ✗ Iron Valiant | ✓ Great Tusk | ...`

**Export Button:**
- **Component:** `gr.Button` (per card)
- **Label:** "Export to Showdown"
- **Action:** Copy team in Pokémon Showdown import format to clipboard
- **Format:**
  ```
  Garchomp
  Raging Bolt
  Great Tusk
  Rillaboom
  Iron Valiant
  [Additional Pokémon]
  ```

#### 2. Overall Team Analysis (Optional Panel)
- **Type Coverage Radar Chart:** 18-point radar showing offensive coverage
- **Defensive Weakness Chart:** Bar chart showing weakness counts per type
- **Role Distribution:** Pie chart showing role balance

#### 3. Error/Warning Messages
- **Component:** `gr.Markdown` or `gr.HTML`
- **Scenarios:**
  - No results found: "No valid recommendations found. Try different Pokémon or tier."
  - Invalid input: "Pokémon not found: [Name]. Did you mean [Suggestion]?"
  - Timeout: "Computation took too long. Showing partial results."
- **Style:** Clear, actionable messages (not technical stack traces)

### Layout

**Two-Column Layout:**
```
┌─────────────────────────────────────────┐
│          Header & Description           │
├───────────────┬─────────────────────────┤
│   Inputs      │   Outputs               │
│               │                         │
│ • Pokémon 1   │ 🏆 Recommendation #1    │
│ • Pokémon 2   │   Score: 0.87           │
│ • Pokémon 3   │   [Details...]          │
│ • Tier        │                         │
│ • [Button]    │ 🥈 Recommendation #2    │
│               │   Score: 0.84           │
│               │   [Details...]          │
│               │                         │
│               │ ... (up to #5)          │
└───────────────┴─────────────────────────┘
```

**Mobile Layout (Single Column):**
- Inputs stack above outputs
- Cards display in vertical list
- Charts responsive (shrink to fit)

### UX Enhancements

1. **Loading States:**
   - Disable inputs during computation
   - Show spinner + "Computing recommendations..." message
   - Estimated time: "~2 seconds"

2. **Animations (Subtle):**
   - Fade-in for recommendation cards
   - Smooth transitions between states

3. **Accessibility:**
   - ARIA labels for screen readers
   - Keyboard navigation support (tab through inputs, enter to submit)
   - High contrast mode compatible

4. **Mobile Responsiveness:**
   - Touch-friendly button sizes (min 44×44 px)
   - Readable font sizes (min 14px body text)
   - Horizontal scroll for wide tables (if any)

### Functional Requirements

1. **Data Validation:**
   - Validate Pokémon names against Pokédex before submission
   - Show inline errors immediately (don't wait for button click)
   - Fuzzy matching suggestions for misspellings

2. **State Management:**
   - Preserve inputs if user navigates away and returns
   - Clear outputs when inputs change (until new search triggered)
   - Cache last 3 searches for quick back navigation (Phase 2)

3. **Error Handling:**
   - Graceful degradation if data not loaded
   - User-friendly error messages (no stack traces)
   - Retry button if computation fails

4. **Performance:**
   - UI must remain responsive during computation (async processing)
   - Results display incrementally (show top result first, then rest)
   - Lazy load sprites/images (don't block initial render)

### Performance Requirements
- Initial page load: **<2s** on Spaces (HTML + CSS + data fetch)
- Recommendation computation: **<4s** on Spaces CPU Basic
- UI update after computation: **<200ms** (render 5 cards)
- Export to clipboard: **<50ms**

### Visual Design

**Color Scheme:**
- Primary: Blue (#3B82F6) for buttons, headers
- Success: Green (#10B981) for positive indicators (✓ checks)
- Warning: Yellow (#F59E0B) for warnings
- Error: Red (#EF4444) for errors, missing checks
- Neutral: Gray (#6B7280) for secondary text

**Typography:**
- Headings: Bold, 18-24px
- Body: Regular, 14-16px
- Scores: Bold, 20px (prominent)
- Monospace: For Showdown export format

**Spacing:**
- Card padding: 16px
- Section margins: 24px
- Input field spacing: 12px vertical

## Acceptance Criteria
- [ ] Three text input fields with autocomplete from Pokédex
- [ ] Tier selection dropdown with Gen 9 OU as default
- [ ] "Get Recommendations" button triggers search
- [ ] Loading spinner + disabled inputs during computation
- [ ] Top-5 recommendation cards displayed with score, breakdown, roles, coverage, meta matchups
- [ ] Each card has "Export to Showdown" button (copies to clipboard)
- [ ] Error messages clear and actionable (e.g., invalid Pokémon name)
- [ ] Mobile-responsive layout (single column on small screens)
- [ ] UI loads in <2s, recommendations display in <4s on Spaces
- [ ] Fuzzy matching suggests corrections for misspelled Pokémon names
- [ ] Accessibility: keyboard navigation, screen reader labels

## Out of Scope (MVP)
- User accounts or saved teams (stateless app)
- Real-time meta updates (monthly snapshot displayed)
- Advanced filtering (e.g., exclude specific roles, types)
- Dark mode toggle (use Gradio default theme)
- Interactive charts (static visualizations sufficient for MVP)

## Dependencies
- Gradio v4.0+ (`gr.Textbox`, `gr.Dropdown`, `gr.Button`, `gr.Markdown`, `gr.HTML`)
- Recommender core (for generating recommendations)
- Data pipeline (for Pokédex names, sprites if available)
- Optional: `plotly` or `matplotlib` for charts (if visualizations added)
