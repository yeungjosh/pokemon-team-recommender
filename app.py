"""
Pokemon Team Recommender - Gradio UI

Entry point for the Hugging Face Spaces deployment.
"""

import gradio as gr

from src.app.explanations import format_layman_explanation, generate_explanation
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


def get_pokemon_sprite(mon_name: str) -> str:
    """Get HTML for displaying a Pokemon sprite."""
    if not mon_name:
        return ""

    mon = pokedex.get(mon_name)
    if mon and mon.sprite:
        return f'<div style="text-align: center; margin: 10px 0;"><img src="{mon.sprite}" width="96" height="96" alt="{mon_name}"></div>'
    return ""


def recommend_team(mon1: str, mon2: str, mon3: str, tier: str) -> tuple[str, str]:
    """Generate team recommendations based on input Pokemon."""
    if not all([mon1, mon2, mon3]):
        return "❌ Please select all 3 Pokémon.", ""

    input_team = [mon1.strip(), mon2.strip(), mon3.strip()]

    try:
        recommendations = recommender.recommend(input_team, top_k=5, candidate_pool_size=12)

        if not recommendations:
            return "No recommendations found. Try different Pokémon!", ""

        # Format results with sprites
        result = f"## Top {len(recommendations)} Recommendations\n\n"

        # Generate explanation for the top recommendation
        top_rec = recommendations[0]
        explanation_data = generate_explanation(
            user_team=input_team,
            recommended_trio=top_rec.pokemon_names,
            scores={
                "composite_score": top_rec.composite_score,
                "type_score": top_rec.type_score,
                "meta_score": top_rec.meta_score,
                "role_score": top_rec.role_score,
                "weaknesses_covered": top_rec.weaknesses_covered,
                "threats_handled": top_rec.threats_handled,
                "roles_added": top_rec.roles_added,
            },
        )
        explanation_markdown = format_layman_explanation(explanation_data)

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
            result += "**Breakdown:**\n"
            result += f"- Type Coverage: {rec.type_score:.3f}\n"
            result += f"- Meta Matchup: {rec.meta_score:.3f}\n"
            result += f"- Role Diversity: {rec.role_score:.3f}\n\n"
            result += "---\n\n"

        return result, explanation_markdown

    except ValueError as e:
        error_msg = str(e)

        # Improve error message with helpful suggestions
        if "not found" in error_msg.lower():
            suggestion = f"❌ {error_msg}\n\n"
            suggestion += "**Available Pokémon in Gen 9 OU:**\n"
            suggestion += ", ".join(AVAILABLE_POKEMON[:8]) + ", ..."
            suggestion += f"\n\n*({len(AVAILABLE_POKEMON)} total - use the dropdown to see all)*"
            return suggestion, ""

        return f"❌ Error: {error_msg}", ""

    except Exception as e:
        return f"❌ Unexpected error: {str(e)}\n\nPlease check your selections and try again.", ""


with gr.Blocks(title="Pokémon Team Recommender") as demo:
    gr.Markdown(
        """
        # ⚔️ Pokémon Team Recommender (ML-Powered)

        Complete your competitive team with **machine learning** recommendations.

        **How it works:** Select 3 Pokémon → ML model analyzes 7 features → Returns top 5 trios optimized for type coverage, meta threats, and role balance.
        """
    )

    gr.Markdown(
        f"""
        > **Note:** This app currently supports **{len(AVAILABLE_POKEMON)} Pokémon** from the Gen 9 OU tier.
        > See the "Show Available Pokémon" section below for the full list.
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
            mon1_sprite = gr.HTML()

            mon2 = gr.Dropdown(
                label="Pokémon 2",
                choices=AVAILABLE_POKEMON,
                value="Raging Bolt",
                allow_custom_value=True,
            )
            mon2_sprite = gr.HTML()

            mon3 = gr.Dropdown(
                label="Pokémon 3",
                choices=AVAILABLE_POKEMON,
                value="Great Tusk",
                allow_custom_value=True,
            )
            mon3_sprite = gr.HTML()

            tier = gr.Dropdown(
                label="Tier",
                choices=["Gen 9 OU", "Gen 9 Ubers", "Gen 9 UU"],
                value="Gen 9 OU",
            )

            submit = gr.Button("Get Recommendations", variant="primary")

        with gr.Column():
            gr.Markdown("### Recommendations")
            output = gr.Markdown()

            # Explanation accordion (only visible after recommendations generated)
            explanation_accordion = gr.Accordion("❓ How did you choose these?", open=False, visible=False)
            with explanation_accordion:
                explanation_output = gr.Markdown()

    gr.Examples(
        examples=[
            ["Garchomp", "Raging Bolt", "Great Tusk", "Gen 9 OU"],
            ["Dragapult", "Kingambit", "Gholdengo", "Gen 9 OU"],
        ],
        inputs=[mon1, mon2, mon3, tier],
    )

    # Wire up recommendations and show accordion when results ready
    def recommend_and_show(mon1, mon2, mon3, tier):
        result, explanation = recommend_team(mon1, mon2, mon3, tier)
        # Show accordion only if we have explanation content
        show_accordion = bool(explanation.strip())
        return result, explanation, gr.update(visible=show_accordion)

    submit.click(
        fn=recommend_and_show,
        inputs=[mon1, mon2, mon3, tier],
        outputs=[output, explanation_output, explanation_accordion],
    )

    # Wire up sprite updates when Pokemon selections change
    mon1.change(fn=get_pokemon_sprite, inputs=[mon1], outputs=[mon1_sprite])
    mon2.change(fn=get_pokemon_sprite, inputs=[mon2], outputs=[mon2_sprite])
    mon3.change(fn=get_pokemon_sprite, inputs=[mon3], outputs=[mon3_sprite])

    # FAQ Section
    with gr.Accordion("❓ Frequently Asked Questions (FAQ)", open=False):
        gr.Markdown(
            f"""
            ### What is Type Coverage?
            Type coverage refers to how well your team can deal with different Pokémon types.

            - **Offensive Coverage:** Can your team hit many types super-effectively?
            - **Defensive Coverage:** Does your team have too many shared weaknesses?

            A balanced team should be able to threaten a wide variety of opponents while minimizing exploitable weaknesses.

            ### What are Meta Threats?
            Meta threats are the most popular and powerful Pokémon in competitive play. Our model uses Smogon usage stats
            to identify which Pokémon appear most frequently in battles.

            A good team should have answers to common threats like Garchomp, Kingambit, and Great Tusk - Pokémon that
            you're likely to face in many matches.

            ### What is Role Balance?
            Role balance ensures your team has the tools needed to control the game:

            - **Hazard Control:** Setting or removing entry hazards (Stealth Rock, Spikes)
            - **Pivoting:** Switching safely with moves like U-turn or Volt Switch
            - **Speed Control:** Fast Pokémon or priority moves to outspeed threats

            A well-rounded team covers multiple roles rather than having six Pokémon that do the same thing.

            ### What are Tiers?
            Tiers organize Pokémon by power level for fair competitive play:

            - **OU (OverUsed):** The standard competitive tier - balanced and diverse
            - **Ubers:** Legendary and extremely powerful Pokémon
            - **UU (UnderUsed):** Viable Pokémon that are less dominant than OU

            This app focuses on **Gen 9 OU**, which is the most popular competitive tier.

            ### Why aren't all Pokémon available?
            This app currently includes **{len(AVAILABLE_POKEMON)} Pokémon** from the Gen 9 OU tier because:

            - **Quality over Quantity:** These are the most competitively viable Pokémon
            - **Training Data:** The ML model was trained on real competitive teams using these Pokémon
            - **Performance:** A focused dataset allows faster, more accurate recommendations

            Pokémon outside this tier (like Legendaries or lower-tier options) aren't included because they have
            different balance considerations and usage patterns.
            """
        )

    # ML Algorithm Explanation
    with gr.Accordion("❓ How do you choose the best Pokémon?", open=False):
        gr.Markdown(
            """
            ### Machine Learning Approach

            Our recommender uses a **Gradient Boosting Regressor** - a machine learning model that learned patterns from
            10,000 synthetic competitive teams.

            #### The Process:

            1. **You select 3 Pokémon** → The system analyzes your partial team
            2. **Feature Extraction** → Calculates 7 key metrics:
               - Type coverage (offensive & defensive)
               - Meta matchup quality (vs. top threats)
               - Role diversity (hazards, pivots, speed control)
               - Team balance factors (speed tiers, bulk, etc.)
            3. **ML Prediction** → Model scores thousands of possible trios
            4. **Ranking** → Returns top 5 combinations optimized for all factors

            #### What the Model Learned:

            After analyzing thousands of successful teams, the model discovered that winning teams prioritize:

            - **38.5% Meta Coverage** - Handling popular threats matters most
            - **32.4% Type Coverage** - Balanced offensive/defensive typing is critical
            - **24.7% Role Balance** - Teams need diverse tools (hazards, pivots, etc.)
            - **4.4% Other Factors** - Speed control, bulk distribution, etc.

            #### Why Machine Learning?

            Traditional team builders use fixed formulas with hand-tuned weights. Our ML approach:

            ✅ **Learns from data** rather than relying on manual rules
            ✅ **Adapts to the meta** as usage patterns evolve
            ✅ **Balances multiple factors** automatically without guesswork
            ✅ **Discovers non-obvious synergies** that humans might miss

            The model doesn't just calculate math - it learned what makes teams successful in real competitive play.
            """
        )

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

    # Load initial sprites on page load
    demo.load(
        fn=lambda: (
            get_pokemon_sprite("Garchomp"),
            get_pokemon_sprite("Raging Bolt"),
            get_pokemon_sprite("Great Tusk"),
        ),
        outputs=[mon1_sprite, mon2_sprite, mon3_sprite],
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
