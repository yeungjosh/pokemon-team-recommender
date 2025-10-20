"""
Pokemon Team Recommender - Gradio App Entry Point

This is the main entry point for the Hugging Face Spaces deployment.
Spaces automatically runs this file on startup.
"""

import gradio as gr

# TODO: Import recommendation engine once implemented
# from src.app.recommender import get_recommendations


def recommend_team(pokemon1: str, pokemon2: str, pokemon3: str, tier: str) -> str:
    """
    Generate team recommendations based on input Pokemon.

    Args:
        pokemon1: First Pokemon name
        pokemon2: Second Pokemon name
        pokemon3: Third Pokemon name
        tier: Competitive tier (e.g., "Gen 9 OU")

    Returns:
        HTML-formatted recommendation results
    """
    # TODO: Implement actual recommendation logic
    # For now, return a placeholder message
    return f"""
    ## 🚧 Under Development

    You entered:
    - {pokemon1}
    - {pokemon2}
    - {pokemon3}
    - Tier: {tier}

    **Status:** Recommendation engine not yet implemented.

    **Next Steps:**
    1. Implement data pipeline (fetch Pokédex, type chart, usage stats)
    2. Build feature extraction (type coverage, roles, meta matchup)
    3. Implement composite scoring algorithm
    4. Add beam/greedy search over candidate trios
    5. Generate top-5 recommendations with explanations

    See `CLAUDE.md` for development workflow and `pokemon_team_recommender_spec.md` for full specification.
    """


# Create Gradio interface
with gr.Blocks(title="Pokémon Team Recommender") as demo:
    gr.Markdown(
        """
        # ⚔️ Pokémon Team Recommender

        **Complete your team with data-driven recommendations**

        Enter 3 Pokémon and get 5 recommended trios based on:
        - 🎯 Type coverage (offensive + defensive)
        - 🏆 Meta matchup (checks against top threats)
        - 🛡️ Role synergy (hazards, removal, pivot, speed control)
        """
    )

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Input Your Team")
            pokemon1 = gr.Textbox(
                label="Pokémon 1",
                placeholder="Garchomp",
                info="Enter first Pokémon name",
            )
            pokemon2 = gr.Textbox(
                label="Pokémon 2",
                placeholder="Raging Bolt",
                info="Enter second Pokémon name",
            )
            pokemon3 = gr.Textbox(
                label="Pokémon 3",
                placeholder="Great Tusk",
                info="Enter third Pokémon name",
            )
            tier = gr.Dropdown(
                label="Competitive Tier",
                choices=["Gen 9 OU", "Gen 9 Ubers", "Gen 9 UU", "Gen 9 RU", "Gen 9 NU"],
                value="Gen 9 OU",
                info="Select competitive tier",
            )
            submit_btn = gr.Button("Get Recommendations", variant="primary")

        with gr.Column():
            gr.Markdown("### Recommendations")
            output = gr.Markdown()

    # TODO: Add examples once recommendation engine is implemented
    # gr.Examples(
    #     examples=[
    #         ["Garchomp", "Raging Bolt", "Great Tusk", "Gen 9 OU"],
    #         ["Kyogre", "Ferrothorn", "Toxapex", "Gen 9 Ubers"],
    #     ],
    #     inputs=[pokemon1, pokemon2, pokemon3, tier],
    # )

    submit_btn.click(
        fn=recommend_team,
        inputs=[pokemon1, pokemon2, pokemon3, tier],
        outputs=output,
    )

    gr.Markdown(
        """
        ---
        **Data Sources:**
        - Pokémon Showdown: [github.com/smogon/pokemon-showdown](https://github.com/smogon/pokemon-showdown)
        - Smogon Usage Stats: [smogon.com/stats](https://www.smogon.com/stats/)

        **License:** MIT | **Repository:** [GitHub](https://github.com/your-username/pokemon-team-recommender)
        """
    )

if __name__ == "__main__":
    # Launch with share=False for Spaces (Spaces handles public URL)
    # Use share=True for local development if you want a public link
    demo.launch()
