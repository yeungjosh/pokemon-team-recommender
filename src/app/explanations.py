"""
Explanation generation for Pokémon team recommendations.

This module provides functions to generate layman-friendly and technical
explanations for why specific Pokémon trios were recommended, enhancing
transparency and user trust.
"""

from dataclasses import dataclass


# T006: Define ExplanationData dataclass
@dataclass
class ExplanationData:
    """Complete explanation package for a single trio recommendation."""

    # Identification
    pokemon_names: list[str]
    composite_score: float

    # Component scores (for technical view)
    type_score: float
    meta_score: float
    role_score: float

    # Layman explanations
    type_reasons: list[str]  # e.g., ["Covers your Fire weakness"]
    meta_reasons: list[str]  # e.g., ["Handles Garchomp and Great Tusk"]
    role_reasons: list[str]  # e.g., ["Provides hazard removal"]

    # Context from scoring (used for template rendering)
    weaknesses_covered: list[str]  # Type names: ["Fire", "Ice"]
    threats_handled: list[str]  # Pokemon names: ["Garchomp", "Kingambit"]
    roles_added: list[str]  # Role names: ["Hazard Control", "Pivot"]


# T007: Define FormulaExplanation dataclass
@dataclass
class FormulaExplanation:
    """Metadata about the scoring formula for educational purposes."""

    # Weight values
    alpha: float = 0.4  # Type coverage weight
    beta: float = 0.4  # Meta coverage weight
    gamma: float = 0.2  # Role diversity weight

    # Component descriptions (layman terms)
    type_description: str = "Measures offensive and defensive type synergy"
    meta_description: str = "How well the team handles popular threats"
    role_description: str = "Balance of team roles (hazards, removal, pivots)"

    # Formula string (for display)
    formula_string: str = "Composite = 0.4×Type + 0.4×Meta + 0.2×Role"


# T008: Define JargonTerm class
class JargonTerm:
    """Competitive jargon terms to filter from layman explanations."""

    FORBIDDEN_TERMS = {
        # Competitive mechanics
        "STAB",
        "stab",
        "EV",
        "IV",
        "EVs",
        "IVs",
        "OU",
        "UU",
        "Ubers",  # Tier names
        # Battle mechanics
        "Choice Band",
        "Choice Scarf",
        "Choice Specs",
        "HDB",
        "Heavy-Duty Boots",
        "hazard stack",
        "hazard stacking",
        # Specific sets/strategies
        "Defog",
        "Rapid Spin",  # Use "hazard removal" instead
        "Stealth Rock",
        "Spikes",  # Use "hazards" instead
        "U-turn",
        "Volt Switch",  # Use "pivot move" instead
        # Stat terms
        "SpA",
        "SpD",
        "Atk",
        "Def",
        "Spe",
        "speed tier",
        "speed creep",
        # Roles (too technical)
        "wallbreaker",
        "wall",
        "sweeper",
        "revenge killer",
        "cleric",
        "status absorber",
    }

    ALLOWED_SIMPLE_TERMS = {
        # Simple battle concepts (OK for layman)
        "weakness",
        "resistance",
        "super effective",
        "type coverage",
        "popular",
        "common threat",
        "hazard control",
        "hazard removal",
        "speed control",
        "pivot",
        "pivoting",
    }


# T010: Implement contains_jargon()
def contains_jargon(text: str) -> bool:
    """
    Check if text contains forbidden competitive jargon.

    Args:
        text: String to validate

    Returns:
        True if jargon detected, False otherwise

    Example:
        >>> contains_jargon("Provides hazard removal")
        False
        >>> contains_jargon("Provides Defog support")
        True  # "Defog" is jargon
    """
    import re

    text_lower = text.lower()
    for term in JargonTerm.FORBIDDEN_TERMS:
        # Use word boundary matching to avoid false positives
        # \b matches word boundaries, so "wall" won't match "wallbreaker"
        pattern = r'\b' + re.escape(term.lower()) + r'\b'
        if re.search(pattern, text_lower):
            return True
    return False


# T013: Implement validate_explanation_jargon_free()
def validate_explanation_jargon_free(explanation: ExplanationData) -> bool:
    """
    Validate that all explanation reasons are jargon-free.

    Args:
        explanation: ExplanationData instance to validate

    Returns:
        True if all reasons are jargon-free

    Raises:
        ValueError: If jargon is detected in any reason

    Example:
        >>> explanation = ExplanationData(...)
        >>> validate_explanation_jargon_free(explanation)
        True
    """
    all_reasons = (
        explanation.type_reasons + explanation.meta_reasons + explanation.role_reasons
    )

    for reason in all_reasons:
        if contains_jargon(reason):
            raise ValueError(f"Jargon detected in reason: {reason}")

    return True


# T016: Implement validate_explanation_readability()
def validate_explanation_readability(explanation: ExplanationData) -> bool:
    """
    Ensure explanations are concise and readable.

    Args:
        explanation: ExplanationData instance to validate

    Returns:
        True if explanation meets readability constraints

    Raises:
        ValueError: If any reason is too long or total exceeds word limit

    Constraints:
        - Each reason: ≤50 words
        - Total explanation: ≤150 words (readable in <30 seconds)

    Example:
        >>> explanation = ExplanationData(...)
        >>> validate_explanation_readability(explanation)
        True
    """
    all_reasons = (
        explanation.type_reasons + explanation.meta_reasons + explanation.role_reasons
    )

    # Check individual reason length
    for reason in all_reasons:
        word_count = len(reason.split())
        if word_count > 50:
            raise ValueError(f"Reason too long ({word_count} words): {reason}")

    # Check total explanation length (SC-003: readable in <30 seconds)
    total_words = sum(len(r.split()) for r in all_reasons)
    if total_words > 150:
        raise ValueError(f"Total explanation too long ({total_words} words)")

    return True


# ===========================
# Phase 3: Explanation Generation
# ===========================


# T027: Implement extract_explanation_context()
def extract_explanation_context(
    user_team: list[str], recommended_trio: list[str], scoring_data: dict
) -> dict:
    """
    Extract explanation context from scoring data.

    Args:
        user_team: List of user's 3 Pokémon names
        recommended_trio: List of 3 recommended Pokémon names
        scoring_data: Dictionary with scoring results containing:
            - weaknesses_covered: List of type names
            - threats_handled: List of Pokémon names
            - roles_added: List of role names

    Returns:
        Dictionary with extracted context for template rendering

    Example:
        >>> context = extract_explanation_context(
        ...     ["Garchomp", "Toxapex"],
        ...     ["Rillaboom", "Iron Valiant"],
        ...     {"weaknesses_covered": ["Fire"], "threats_handled": ["Kingambit"]}
        ... )
        >>> context["weaknesses_covered"]
        ['Fire']
    """
    return {
        "weaknesses_covered": scoring_data.get("weaknesses_covered", []),
        "threats_handled": scoring_data.get("threats_handled", []),
        "roles_added": scoring_data.get("roles_added", []),
    }


# T029: Implement _generate_type_reasons()
def _generate_type_reasons(context: dict) -> list[str]:
    """
    Generate layman-friendly type coverage reasons.

    Args:
        context: Dictionary with weaknesses_covered list

    Returns:
        List of readable reason strings without jargon

    Example:
        >>> reasons = _generate_type_reasons({"weaknesses_covered": ["Fire", "Ice"]})
        >>> len(reasons) > 0
        True
    """
    import random

    from src.app.explanation_templates import (
        TYPE_DEFENSIVE_TEMPLATES,
        TYPE_MULTIPLE_TEMPLATE,
    )

    reasons = []
    weaknesses = context.get("weaknesses_covered", [])

    if len(weaknesses) == 0:
        return reasons

    if len(weaknesses) == 1:
        # Single weakness - use defensive template
        template = random.choice(TYPE_DEFENSIVE_TEMPLATES)
        reason = template.format(type_name=weaknesses[0])
        reasons.append(reason)
    elif len(weaknesses) <= 3:
        # Multiple weaknesses - mention each one
        for weakness in weaknesses[:3]:  # Limit to 3 for readability
            template = random.choice(TYPE_DEFENSIVE_TEMPLATES)
            reason = template.format(type_name=weakness)
            reasons.append(reason)
    else:
        # Many weaknesses - use summary template
        types_str = ", ".join(weaknesses[:3]) + ", and more"
        reason = TYPE_MULTIPLE_TEMPLATE.format(types=types_str)
        reasons.append(reason)

    return reasons


# T031: Implement _generate_meta_reasons()
def _generate_meta_reasons(context: dict) -> list[str]:
    """
    Generate layman-friendly meta matchup reasons.

    Args:
        context: Dictionary with threats_handled list

    Returns:
        List of readable reason strings without jargon

    Example:
        >>> reasons = _generate_meta_reasons({"threats_handled": ["Garchomp"]})
        >>> len(reasons) > 0
        True
    """
    import random

    from src.app.explanation_templates import (
        META_MULTIPLE_THREATS_TEMPLATE,
        META_SINGLE_THREAT_TEMPLATES,
    )

    reasons = []
    threats = context.get("threats_handled", [])

    if len(threats) == 0:
        return reasons

    if len(threats) == 1:
        # Single threat
        template = random.choice(META_SINGLE_THREAT_TEMPLATES)
        reason = template.format(threat_name=threats[0])
        reasons.append(reason)
    elif len(threats) <= 3:
        # Few threats - list them
        threats_str = ", ".join(threats[:2])
        if len(threats) == 3:
            threats_str = f"{threats[0]}, {threats[1]}, and {threats[2]}"
        reason = META_MULTIPLE_THREATS_TEMPLATE.format(threats=threats_str)
        reasons.append(reason)
    else:
        # Many threats - summarize
        threats_str = f"{threats[0]}, {threats[1]}, and others"
        reason = META_MULTIPLE_THREATS_TEMPLATE.format(threats=threats_str)
        reasons.append(reason)

    return reasons


# T033: Implement _generate_role_reasons()
def _generate_role_reasons(context: dict) -> list[str]:
    """
    Generate layman-friendly role synergy reasons.

    Args:
        context: Dictionary with roles_added list

    Returns:
        List of readable reason strings without jargon

    Example:
        >>> reasons = _generate_role_reasons({"roles_added": ["Hazard Control"]})
        >>> len(reasons) > 0
        True
    """
    import random

    from src.app.explanation_templates import ROLE_GENERAL_TEMPLATE, ROLE_TEMPLATES

    reasons = []
    roles = context.get("roles_added", [])

    if len(roles) == 0:
        return reasons

    for role in roles:
        if role in ROLE_TEMPLATES:
            # Use specific template for known role
            template = random.choice(ROLE_TEMPLATES[role])
            reasons.append(template)
        else:
            # Use general template for unknown role
            reason = ROLE_GENERAL_TEMPLATE.format(role_name=role)
            reasons.append(reason)

    return reasons


# T035: Implement generate_explanation()
def generate_explanation(
    user_team: list[str], recommended_trio: list[str], scores: dict
) -> ExplanationData:
    """
    Generate complete explanation for a recommendation.

    Args:
        user_team: List of user's Pokémon names
        recommended_trio: List of recommended Pokémon names
        scores: Dictionary with:
            - composite_score: float
            - type_score: float
            - meta_score: float
            - role_score: float
            - weaknesses_covered: List[str]
            - threats_handled: List[str]
            - roles_added: List[str]

    Returns:
        ExplanationData instance with all explanation components

    Example:
        >>> explanation = generate_explanation(
        ...     ["Garchomp"],
        ...     ["Rillaboom"],
        ...     {"composite_score": 0.8, "type_score": 0.85,
        ...      "meta_score": 0.75, "role_score": 0.8,
        ...      "weaknesses_covered": ["Fire"],
        ...      "threats_handled": ["Kingambit"],
        ...      "roles_added": ["Hazard Control"]}
        ... )
        >>> explanation.pokemon_names
        ['Rillaboom']
    """
    # Extract context
    context = extract_explanation_context(user_team, recommended_trio, scores)

    # Generate reasons for each component
    type_reasons = _generate_type_reasons(context)
    meta_reasons = _generate_meta_reasons(context)
    role_reasons = _generate_role_reasons(context)

    # Create explanation data
    explanation = ExplanationData(
        pokemon_names=recommended_trio,
        composite_score=scores.get("composite_score", 0.0),
        type_score=scores.get("type_score", 0.0),
        meta_score=scores.get("meta_score", 0.0),
        role_score=scores.get("role_score", 0.0),
        type_reasons=type_reasons,
        meta_reasons=meta_reasons,
        role_reasons=role_reasons,
        weaknesses_covered=context["weaknesses_covered"],
        threats_handled=context["threats_handled"],
        roles_added=context["roles_added"],
    )

    return explanation


# T037: Implement format_layman_explanation()
def format_layman_explanation(explanation: ExplanationData) -> str:
    """
    Format explanation as markdown for display.

    Args:
        explanation: ExplanationData instance

    Returns:
        Markdown-formatted string with checkmarks and sections

    Example:
        >>> explanation = ExplanationData(
        ...     pokemon_names=["Rillaboom"],
        ...     composite_score=0.8, type_score=0.85,
        ...     meta_score=0.75, role_score=0.8,
        ...     type_reasons=["Covers Fire weakness"],
        ...     meta_reasons=["Handles Kingambit"],
        ...     role_reasons=["Provides hazard removal"],
        ...     weaknesses_covered=["Fire"],
        ...     threats_handled=["Kingambit"],
        ...     roles_added=["Hazard Control"]
        ... )
        >>> md = format_layman_explanation(explanation)
        >>> "Rillaboom" in md
        True
    """
    from src.app.explanation_templates import (
        EXPLANATION_HEADER,
        SECTION_META,
        SECTION_ROLE,
        SECTION_TYPE,
    )

    # Build Pokemon list
    pokemon_list = ", ".join(explanation.pokemon_names)

    # Start with header
    markdown = EXPLANATION_HEADER.format(pokemon_list=pokemon_list)

    # Add type coverage section
    if explanation.type_reasons:
        markdown += SECTION_TYPE
        for reason in explanation.type_reasons:
            markdown += f"✓ {reason}\n"

    # Add meta matchup section
    if explanation.meta_reasons:
        markdown += SECTION_META
        for reason in explanation.meta_reasons:
            markdown += f"✓ {reason}\n"

    # Add role synergy section
    if explanation.role_reasons:
        markdown += SECTION_ROLE
        for reason in explanation.role_reasons:
            markdown += f"✓ {reason}\n"

    return markdown.strip()
