"""
Pokemon Team Recommender - Gradio UI

Entry point for the Hugging Face Spaces deployment.
"""

import gradio as gr

from src.data.pokedex import Pokedex
from src.data.types import TypeChart
from src.data.usage import UsageStats
from src.search.recommender import TeamRecommender

# Initialize data loaders (cached for performance)
print("Loading data...")
pokedex = Pokedex()
type_chart = TypeChart()
usage_stats = UsageStats()
recommender = TeamRecommender(pokedex, type_chart, usage_stats)
print("Data loaded successfully!")


def recommend_team(mon1: str, mon2: str, mon3: str, tier: str) -> str:
    """Generate team recommendations based on input Pokemon."""
    if not all([mon1, mon2, mon3]):
        return "❌ Please enter all 3 Pokémon names."

    input_team = [mon1.strip(), mon2.strip(), mon3.strip()]

    try:
        recommendations = recommender.recommend(input_team, top_k=5, candidate_pool_size=12)

        if not recommendations:
            return "No recommendations found. Try different Pokémon!"

        # Format results
        result = f"## Top {len(recommendations)} Recommendations\n\n"

        for i, rec in enumerate(recommendations, 1):
            result += f"### #{i} - Score: {rec.composite_score:.3f}\n\n"
            result += f"**Trio:** {', '.join(rec.pokemon_names)}\n\n"
            result += f"**Breakdown:**\n"
            result += f"- Type Coverage: {rec.type_score:.3f}\n"
            result += f"- Meta Matchup: {rec.meta_score:.3f}\n"
            result += f"- Role Diversity: {rec.role_score:.3f}\n\n"
            result += "---\n\n"

        return result

    except ValueError as e:
        return f"❌ Error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}\n\nPlease check Pokémon names and try again."


with gr.Blocks(title="Pokémon Team Recommender") as demo:
    gr.Markdown(
        """
        # ⚔️ Pokémon Team Recommender

        Complete your competitive team with data-driven suggestions.

        **How it works:** Enter 3 Pokémon → Get 5 recommended trios based on type coverage, meta threats, and role balance.
        """
    )

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Your Team")
            mon1 = gr.Textbox(label="Pokémon 1", placeholder="Garchomp")
            mon2 = gr.Textbox(label="Pokémon 2", placeholder="Raging Bolt")
            mon3 = gr.Textbox(label="Pokémon 3", placeholder="Great Tusk")

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

    gr.Markdown(
        """
        ---
        **Scoring Formula:** `Score = 0.4×TypeCoverage + 0.4×MetaMatchup + 0.2×RoleDiversity`

        **Data Sources:** [Pokémon Showdown](https://github.com/smogon/pokemon-showdown) • [Smogon Stats](https://www.smogon.com/stats/) (Oct 2024)
        """
    )


if __name__ == "__main__":
    demo.launch()
