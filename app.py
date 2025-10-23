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

# Type colors matching Pokemon games
TYPE_COLORS = {
    "Normal": "#A8A878",
    "Fire": "#F08030",
    "Water": "#6890F0",
    "Electric": "#F8D030",
    "Grass": "#78C850",
    "Ice": "#98D8D8",
    "Fighting": "#C03028",
    "Poison": "#A040A0",
    "Ground": "#E0C068",
    "Flying": "#A890F0",
    "Psychic": "#F85888",
    "Bug": "#A8B820",
    "Rock": "#B8A038",
    "Ghost": "#705898",
    "Dragon": "#7038F8",
    "Dark": "#705848",
    "Steel": "#B8B8D0",
    "Fairy": "#EE99AC",
}


def get_type_badge(type_name: str) -> str:
    """Generate HTML for a Pokemon type badge (game-style)."""
    color = TYPE_COLORS.get(type_name, "#777")
    return f'<span style="display: inline-block; background-color: {color}; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold; font-size: 11px; margin: 0 2px; text-shadow: 1px 1px 1px rgba(0,0,0,0.3);">{type_name.upper()}</span>'


def get_pokemon_name_with_types(mon_name: str) -> str:
    """Get Pokemon name with type badges next to it."""
    mon = pokedex.get(mon_name)
    if not mon:
        return mon_name

    type_badges = "".join(get_type_badge(t) for t in mon.types)
    return f"{mon_name} {type_badges}"


def get_pokemon_sprite(mon_name: str) -> str:
    """Get HTML for displaying a Pokemon sprite with type badges."""
    if not mon_name:
        return ""

    mon = pokedex.get(mon_name)
    if mon and mon.sprite:
        type_badges = "".join(get_type_badge(t) for t in mon.types)
        return f'''<div style="text-align: center; margin: 10px 0;">
            <img src="{mon.sprite}" width="96" height="96" alt="{mon_name}">
            <div style="margin-top: 5px;">{type_badges}</div>
        </div>'''
    return ""


def recommend_moves(pokemon: "Pokemon") -> list[str]:
    """Recommend 4 moves for a Pokemon based on their learnset and role."""
    if not pokemon or not pokemon.learnset:
        return []

    # Priority order for move selection
    priority_moves = {"Sucker Punch", "Extreme Speed", "Aqua Jet", "Mach Punch", "Ice Shard", "Thunderclap"}
    setup_moves = {"Swords Dance", "Nasty Plot", "Calm Mind", "Dragon Dance"}
    utility_moves = {"Stealth Rock", "Spikes", "Toxic Spikes", "Rapid Spin", "Defog", "U-turn", "Volt Switch", "Flip Turn"}

    selected = []
    learnset = set(pokemon.learnset)

    # 1. Priority: Utility moves (hazards, removal, pivots)
    for move in utility_moves:
        if move in learnset and len(selected) < 4:
            selected.append(move)

    # 2. Priority: Setup moves
    for move in setup_moves:
        if move in learnset and len(selected) < 4:
            selected.append(move)

    # 3. Priority: Priority moves
    for move in priority_moves:
        if move in learnset and len(selected) < 4:
            selected.append(move)

    # 4. Fill remaining slots with strongest STAB/coverage moves
    remaining = [m for m in pokemon.learnset if m not in selected]
    for move in remaining:
        if len(selected) < 4:
            selected.append(move)

    return selected[:4]


def analyze_team_strength(user_team_names: list[str], recommended_names: list[str]) -> str:
    """Generate a brief analysis of why the complete 6-mon team is strong."""
    full_team = [pokedex.get(name) for name in user_team_names + recommended_names if pokedex.get(name)]

    if len(full_team) != 6:
        return ""

    # Analyze team composition
    all_types = set()
    roles = set()
    has_hazards = False
    has_removal = False
    has_pivot = False
    has_priority = False

    for mon in full_team:
        all_types.update(mon.types)
        mon_roles = set()

        for move in mon.learnset:
            if move in {"Stealth Rock", "Spikes", "Toxic Spikes"}:
                has_hazards = True
                mon_roles.add("hazard setter")
            if move in {"Rapid Spin", "Defog"}:
                has_removal = True
                mon_roles.add("hazard control")
            if move in {"U-turn", "Volt Switch", "Flip Turn"}:
                has_pivot = True
                mon_roles.add("pivot")
            if move in {"Sucker Punch", "Extreme Speed", "Aqua Jet", "Thunderclap", "Ice Shard"}:
                has_priority = True
                mon_roles.add("priority")

        roles.update(mon_roles)

    # Build analysis as a list
    analysis = "**Why this team is strong:**\n"
    strengths = []

    if has_hazards:
        strengths.append("- ✅ Hazard setting")
    if has_removal:
        strengths.append("- ✅ Hazard control")
    if has_pivot:
        strengths.append("- ✅ Momentum with pivots")
    if has_priority:
        strengths.append("- ✅ Priority revenge killing")

    type_count = len(all_types)
    strengths.append(f"- ✅ {type_count}-type coverage")

    return analysis + "\n".join(strengths) + "\n"


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

            # Display trio with type badges
            trio_with_types = [get_pokemon_name_with_types(name) for name in rec.pokemon_names]
            result += f"**Trio:** {', '.join(trio_with_types)}\n\n"

            # Add recommended moves for each Pokemon
            result += "**Recommended Moves:**\n"
            for mon_name in rec.pokemon_names:
                mon = pokedex.get(mon_name)
                if mon:
                    moves = recommend_moves(mon)
                    if moves:
                        name_with_types = get_pokemon_name_with_types(mon_name)
                        result += f"- **{name_with_types}:** {' / '.join(moves)}\n"

            result += "\n"

            # Add team strength analysis for all recommendations
            team_analysis = analyze_team_strength(input_team, rec.pokemon_names)
            if team_analysis:
                result += f"{team_analysis}\n"

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

            tier = gr.Dropdown(
                label="Tier",
                choices=["Gen 9 OU", "Gen 9 Ubers", "Gen 9 UU"],
                value="Gen 9 OU",
            )

            gr.Markdown("---")

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

            submit = gr.Button("Get Recommendations", variant="primary")

        with gr.Column():
            gr.Markdown("### Recommendations")
            output = gr.Markdown()

            # Explanation accordion (only visible after recommendations generated)
            explanation_accordion = gr.Accordion("❓ How did you choose these?", open=False, visible=False)
            with explanation_accordion:
                explanation_output = gr.Markdown()

    # Example Teams Section
    with gr.Accordion("📋 Example Team (Full 6-Mon)", open=False):
        gr.Markdown("### Balanced OU Team")

        gr.Markdown("**Your Core (Enter these 3):**")

        # Core 3 sprites
        gr.HTML("""
            <div style="display: flex; justify-content: center; gap: 20px; margin: 15px 0;">
                <div style="text-align: center;">
                    <img src="https://img.pokemondb.net/sprites/home/normal/great-tusk.png" width="96" height="96" alt="Great Tusk">
                    <p style="margin-top: 5px; font-weight: bold;">Great Tusk</p>
                </div>
                <div style="text-align: center;">
                    <img src="https://img.pokemondb.net/sprites/home/normal/raging-bolt.png" width="96" height="96" alt="Raging Bolt">
                    <p style="margin-top: 5px; font-weight: bold;">Raging Bolt</p>
                </div>
                <div style="text-align: center;">
                    <img src="https://img.pokemondb.net/sprites/home/normal/kingambit.png" width="96" height="96" alt="Kingambit">
                    <p style="margin-top: 5px; font-weight: bold;">Kingambit</p>
                </div>
            </div>
        """)

        gr.Button("Load This Core", variant="secondary").click(
            fn=lambda: ("Great Tusk", "Raging Bolt", "Kingambit"),
            outputs=[mon1, mon2, mon3],
        )

        gr.Markdown("---")
        gr.Markdown("**Complete 6-Pokemon Team:**")

        # Full 6-mon team sprites
        gr.HTML("""
            <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; margin: 15px 0;">
                <div style="text-align: center;">
                    <img src="https://img.pokemondb.net/sprites/home/normal/great-tusk.png" width="80" height="80" alt="Great Tusk">
                    <p style="margin-top: 5px; font-size: 0.9em; font-weight: bold;">Great Tusk</p>
                    <p style="margin: 0; font-size: 0.8em; color: #888;">Hazard Control</p>
                </div>
                <div style="text-align: center;">
                    <img src="https://img.pokemondb.net/sprites/home/normal/raging-bolt.png" width="80" height="80" alt="Raging Bolt">
                    <p style="margin-top: 5px; font-size: 0.9em; font-weight: bold;">Raging Bolt</p>
                    <p style="margin: 0; font-size: 0.8em; color: #888;">Special Attacker</p>
                </div>
                <div style="text-align: center;">
                    <img src="https://img.pokemondb.net/sprites/home/normal/kingambit.png" width="80" height="80" alt="Kingambit">
                    <p style="margin-top: 5px; font-size: 0.9em; font-weight: bold;">Kingambit</p>
                    <p style="margin: 0; font-size: 0.8em; color: #888;">Priority Revenge Killer</p>
                </div>
                <div style="text-align: center;">
                    <img src="https://img.pokemondb.net/sprites/home/normal/gholdengo.png" width="80" height="80" alt="Gholdengo">
                    <p style="margin-top: 5px; font-size: 0.9em; font-weight: bold;">Gholdengo</p>
                    <p style="margin: 0; font-size: 0.8em; color: #888;">Hazard Immunity</p>
                </div>
                <div style="text-align: center;">
                    <img src="https://img.pokemondb.net/sprites/home/normal/corviknight.png" width="80" height="80" alt="Corviknight">
                    <p style="margin-top: 5px; font-size: 0.9em; font-weight: bold;">Corviknight</p>
                    <p style="margin: 0; font-size: 0.8em; color: #888;">Physical Wall</p>
                </div>
                <div style="text-align: center;">
                    <img src="https://img.pokemondb.net/sprites/home/normal/slowking-galarian.png" width="80" height="80" alt="Slowking-Galar">
                    <p style="margin-top: 5px; font-size: 0.9em; font-weight: bold;">Slowking-Galar</p>
                    <p style="margin: 0; font-size: 0.8em; color: #888;">Special Wall + Pivot</p>
                </div>
            </div>
        """)

        gr.Markdown("""
            **Why this team works:**

            - **Great Tusk:** Rapid Spin removes hazards, provides Ground/Fighting coverage
            - **Raging Bolt:** Thunderclap priority, special attacking threat with Dragon/Electric STAB
            - **Kingambit:** Sucker Punch revenge killer, late-game sweeper with Swords Dance
            - **Gholdengo:** Good as Gold ability blocks status moves, immune to hazards
            - **Corviknight:** Physical wall with Defog, checks Fighting/Ground threats
            - **Slowking-Galar:** Special wall with Future Sight pivot, handles Water/Fire types

            This team has **hazard control** (Tusk/Corviknight), **pivots** (Corviknight), **priority** (Raging Bolt/Kingambit),
            **defensive balance** (physical + special walls), and **type coverage** across 13+ types.
        """)


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
