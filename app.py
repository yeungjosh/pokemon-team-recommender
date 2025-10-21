"""
Pokemon Team Recommender - Gradio UI

Entry point for the Hugging Face Spaces deployment.
"""

import gradio as gr

from src.data.pokedex import Pokedex
from src.data.types import TypeChart
from src.data.usage import UsageStats
from src.search.ml_recommender import MLTeamRecommender

# Initialize data loaders (cached for performance)
print("Loading data...")
pokedex = Pokedex()
type_chart = TypeChart()
usage_stats = UsageStats()
recommender = MLTeamRecommender(pokedex, type_chart, usage_stats, use_ml=True)
print("Data loaded successfully!")

# Get list of available Pokemon for dropdown
AVAILABLE_POKEMON = sorted(pokedex.pokemon.keys())


def recommend_team(mon1: str, mon2: str, mon3: str, tier: str) -> str:
    """Generate team recommendations based on input Pokemon."""
    if not all([mon1, mon2, mon3]):
        return "❌ Please select all 3 Pokémon."

    input_team = [mon1.strip(), mon2.strip(), mon3.strip()]

    try:
        recommendations = recommender.recommend(input_team, top_k=5, candidate_pool_size=12)

        if not recommendations:
            return "No recommendations found. Try different Pokémon!"

        # Format results with sprites
        result = f"## Top {len(recommendations)} Recommendations\n\n"

        for i, rec in enumerate(recommendations, 1):
            result += f"### #{i} - Score: {rec.composite_score:.3f}\n\n"

            # Add sprites for the trio
            sprite_row = ""
            for mon_name in rec.pokemon_names:
                mon = pokedex.get(mon_name)
                if mon and mon.sprite:
                    sprite_row += f'<img src="{mon.sprite}" width="96" height="96" style="display:inline-block; vertical-align:middle;" alt="{mon_name}"> '

            if sprite_row:
                result += f'{sprite_row}\n\n'

            result += f"**Trio:** {', '.join(rec.pokemon_names)}\n\n"
            result += f"**Breakdown:**\n"
            result += f"- Type Coverage: {rec.type_score:.3f}\n"
            result += f"- Meta Matchup: {rec.meta_score:.3f}\n"
            result += f"- Role Diversity: {rec.role_score:.3f}\n\n"
            result += "---\n\n"

        return result

    except ValueError as e:
        error_msg = str(e)

        # Improve error message with helpful suggestions
        if "not found" in error_msg.lower():
            # Extract the Pokemon name from error if possible
            invalid_mon = error_msg.split(":")[-1].strip() if ":" in error_msg else ""

            suggestion = f"❌ {error_msg}\n\n"
            suggestion += "**Available Pokémon in Gen 9 OU:**\n"
            suggestion += ", ".join(AVAILABLE_POKEMON[:8]) + ", ..."
            suggestion += f"\n\n*({len(AVAILABLE_POKEMON)} total - use the dropdown to see all)*"
            return suggestion

        return f"❌ Error: {error_msg}"

    except Exception as e:
        return f"❌ Unexpected error: {str(e)}\n\nPlease check your selections and try again."


with gr.Blocks(title="Pokémon Team Recommender") as demo:
    gr.Markdown(
        """
        # ⚔️ Pokémon Team Recommender (ML-Powered)

        Complete your competitive team with **machine learning** recommendations.

        **How it works:** Select 3 Pokémon → ML model analyzes 7 features → Returns top 5 trios optimized for type coverage, meta threats, and role balance.
        """
    )

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Your Team")
            mon1 = gr.Dropdown(
                label="Pokémon 1",
                choices=AVAILABLE_POKEMON,
                value="Garchomp",
                allow_custom_value=True,
            )
            mon2 = gr.Dropdown(
                label="Pokémon 2",
                choices=AVAILABLE_POKEMON,
                value="Raging Bolt",
                allow_custom_value=True,
            )
            mon3 = gr.Dropdown(
                label="Pokémon 3",
                choices=AVAILABLE_POKEMON,
                value="Great Tusk",
                allow_custom_value=True,
            )

            tier = gr.Dropdown(
                label="Tier",
                choices=["Gen 9 OU", "Gen 9 Ubers", "Gen 9 UU"],
                value="Gen 9 OU",
            )

            submit = gr.Button("Get Recommendations", variant="primary")

        with gr.Column():
            gr.Markdown("### Recommendations")
            output = gr.Markdown()

    gr.Examples(
        examples=[
            ["Garchomp", "Raging Bolt", "Great Tusk", "Gen 9 OU"],
            ["Dragapult", "Kingambit", "Gholdengo", "Gen 9 OU"],
        ],
        inputs=[mon1, mon2, mon3, tier],
    )

    submit.click(fn=recommend_team, inputs=[mon1, mon2, mon3, tier], outputs=output)

    # Add "Show Available Pokémon" section
    with gr.Accordion("📋 Show Available Pokémon", open=False):
        available_list = "\n".join([f"- {mon}" for mon in AVAILABLE_POKEMON])
        gr.Markdown(
            f"""
            ### All {len(AVAILABLE_POKEMON)} Pokémon in Gen 9 OU dataset:

            {available_list}

            *Note: Only these Pokémon are available for team building and recommendations.*
            """
        )

    gr.Markdown(
        """
        ---
        **ML Model:** Gradient Boosting Regressor (100 trees) trained on 10,000 synthetic teams

        **Learned Weights:** 38.5% Meta • 32.4% Type • 24.7% Role • 4.4% Other (speed, balance, bulk)

        **Data Sources:** [Pokémon Showdown](https://github.com/smogon/pokemon-showdown) • [Smogon Stats](https://www.smogon.com/stats/) (Oct 2024)
        """
    )


if __name__ == "__main__":
    demo.launch()
