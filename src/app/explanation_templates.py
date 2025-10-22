"""
Text templates for generating layman-friendly explanations.

Templates are organized by scoring component:
- Type coverage (offensive, defensive, mixed)
- Meta matchup (popular threats)
- Role synergy (team composition)

All templates use simple language and avoid competitive jargon.
"""

# ===========================
# T024: Type Coverage Templates
# ===========================

# Templates for offensive type coverage
TYPE_OFFENSIVE_TEMPLATES = [
    "Provides {type_name} coverage to handle more opponents",
    "Adds {type_name} attacks to cover your team's gaps",
    "Can hit {type_name}-weak opponents effectively",
]

# Templates for defensive type coverage (covering weaknesses)
TYPE_DEFENSIVE_TEMPLATES = [
    "Covers your team's weakness to {type_name} attacks",
    "Protects against {type_name} moves that threaten your team",
    "Adds resistance to {type_name} damage",
]

# Templates for multiple types
TYPE_MULTIPLE_TEMPLATE = "Improves your team's type coverage against {types}"

# Template for general coverage improvement
TYPE_GENERAL_TEMPLATE = "Balances your team's type matchups"


# ===========================
# T025: Meta Matchup Templates
# ===========================

# Templates for handling specific threats
META_SINGLE_THREAT_TEMPLATES = [
    "Can handle the popular threat {threat_name}",
    "Provides an answer to {threat_name}",
    "Helps deal with {threat_name}",
]

# Template for handling multiple threats
META_MULTIPLE_THREATS_TEMPLATE = "Can handle popular threats like {threats}"

# Template for general meta coverage
META_GENERAL_TEMPLATE = "Improves matchups against commonly used opponents"


# ===========================
# T026: Role Synergy Templates
# ===========================

# Templates for specific roles
ROLE_TEMPLATES = {
    "Hazard Control": [
        "Provides hazard removal support",
        "Helps keep your side of the field clear",
    ],
    "Hazard Setter": [
        "Can set up hazards to wear down opponents",
        "Adds field control options",
    ],
    "Pivot": [
        "Adds pivoting ability to maintain momentum",
        "Helps switch safely to advantageous matchups",
    ],
    "Speed Control": [
        "Provides speed control for your team",
        "Helps manage turn order in battles",
    ],
}

# Template for general role addition
ROLE_GENERAL_TEMPLATE = "Adds {role_name} to your team composition"

# Template for multiple roles
ROLE_MULTIPLE_TEMPLATE = "Provides versatile support with multiple roles"


# ===========================
# Formatting Templates
# ===========================

# Template for the overall explanation header
EXPLANATION_HEADER = "**Why these Pokémon?**\n\n{pokemon_list}\n"

# Template for section headers
SECTION_TYPE = "\n**Type Coverage:**\n"
SECTION_META = "\n**Popular Threats:**\n"
SECTION_ROLE = "\n**Team Composition:**\n"
