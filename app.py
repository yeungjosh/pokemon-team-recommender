"""
Pokemon Team Recommender - Gradio UI

Entry point for the Hugging Face Spaces deployment.
"""

import gradio as gr


def recommend_team(mon1: str, mon2: str, mon3: str, tier: str) -> str:
    """Generate team recommendations based on input Pokemon."""
    # TODO: Wire up to actual recommendation engine
    return f"""
    ## Work in Progress

    Input team:
    - {mon1}
    - {mon2}
    - {mon3}
    - Tier: {tier}

    Recommendation engine coming soon. Check back later!
    """


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

    submit.click(fn=recommend_team, inputs=[mon1, mon2, mon3, tier], outputs=output)

    gr.Markdown(
        """
        ---
        Data from [Pokémon Showdown](https://github.com/smogon/pokemon-showdown)
        and [Smogon Stats](https://www.smogon.com/stats/)
        """
    )


if __name__ == "__main__":
    demo.launch()
