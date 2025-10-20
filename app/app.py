"""Gradio entry point for the Pokémon Team Recommender MVP."""

from __future__ import annotations

import gradio as gr

from src.data.loaders import load_mon_features
from src.search.greedy import greedy_complete_team


def recommend(pokemon_one: str, pokemon_two: str, pokemon_three: str) -> list[dict[str, object]]:
    """Return placeholder recommendations while the scoring stack is built."""

    core = [pokemon_one, pokemon_two, pokemon_three]
    candidates = load_mon_features()
    return greedy_complete_team(core, candidates, top_k=5)


def build_demo() -> gr.Blocks:
    """Create the Gradio UI layout."""

    with gr.Blocks(title="Pokémon Team Recommender") as demo:
        gr.Markdown("## Complete my team")
        with gr.Row():
            pokemon_one = gr.Textbox(label="Pokémon 1", value="Garchomp")
            pokemon_two = gr.Textbox(label="Pokémon 2", value="Raging Bolt")
            pokemon_three = gr.Textbox(label="Pokémon 3", value="Great Tusk")
        recommend_button = gr.Button("Recommend")
        output = gr.JSON(label="Top trios (placeholder)")
        recommend_button.click(
            recommend,
            inputs=[pokemon_one, pokemon_two, pokemon_three],
            outputs=output,
        )
    return demo


def main() -> None:
    """Launch the demo when executed as a script."""

    build_demo().launch()


if __name__ == "__main__":
    main()
