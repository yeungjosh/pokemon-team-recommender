# Pokémon Team Recommender

Pokémon Team Recommender is a Gradio + Hugging Face Spaces project that helps players finish a six-Pokémon roster from a three-Pokémon core. The MVP focuses on transparent heuristics for type coverage, meta matchup, and role diversity.

## Project Status
- **Owner:** You (ML Engineer)
- **Status:** v1 scaffolding
- **Stack:** Python (data + scoring), Gradio UI, Hugging Face Spaces deployment

## Quickstart
```bash
pip install -r requirements.txt
python -m app.app
```

## Repository Structure
```
pokemon-team-recommender/
├─ app/                # Gradio entry point
├─ data/               # Seed data snapshots (raw + processed)
├─ docs/               # Product spec and design notes
├─ notebooks/          # Exploration notebooks
├─ src/                # Library code (data loaders, features, search, etc.)
├─ tests/              # Pytest suite (coming soon)
├─ requirements.txt
├─ runtime.txt
└─ README.md
```

## Product Spec
The full product specification and design doc live in [`docs/product_spec.md`](docs/product_spec.md). It covers goals, user stories, system architecture, data modeling, scoring heuristics, evaluation plans, deployment, and milestones.

## License & Attribution
Released under the MIT License. Pokémon data is sourced from Pokémon Showdown and Smogon usage statistics; see the spec for details.
