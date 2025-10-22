"""
Unit tests for explanation generation functions.

Tests cover:
- Jargon detection and validation
- Readability constraints (word count)
- Template rendering and explanation generation
- Score formatting (layman and technical)
"""

import pytest
from src.app.explanations import (
    ExplanationData,
    JargonTerm,
    contains_jargon,
    validate_explanation_jargon_free,
    validate_explanation_readability,
)


# T009: Write test_contains_jargon() (should fail initially)
def test_contains_jargon():
    """Test jargon detection in text strings."""
    # Should detect forbidden terms
    assert contains_jargon("This Pokemon has great STAB coverage") is True
    assert contains_jargon("Max out EVs and IVs") is True
    assert contains_jargon("Use Defog to clear hazards") is True
    assert contains_jargon("Sweeper with Choice Scarf") is True

    # Should allow simple terms
    assert contains_jargon("Covers your Fire weakness") is False
    assert contains_jargon("Provides hazard removal support") is False
    assert contains_jargon("Good type coverage") is False
    assert contains_jargon("Super effective against Water") is False

    # Case-insensitive detection
    assert contains_jargon("Great stab moves") is True  # lowercase "stab"
    assert contains_jargon("COVERS YOUR WEAKNESS") is False  # allowed term


# T012: Write test_validate_jargon_free() (should fail initially)
def test_validate_jargon_free():
    """Test explanation validation for jargon-free content."""
    # Valid explanation (no jargon)
    valid_explanation = ExplanationData(
        pokemon_names=["Rillaboom", "Iron Valiant", "Dragapult"],
        composite_score=0.82,
        type_score=0.85,
        meta_score=0.78,
        role_score=0.83,
        type_reasons=["Covers your team's weakness to Water attacks"],
        meta_reasons=["Can handle common threats like Garchomp"],
        role_reasons=["Provides hazard removal support"],
        weaknesses_covered=["Water"],
        threats_handled=["Garchomp"],
        roles_added=["Hazard Control"],
    )
    assert validate_explanation_jargon_free(valid_explanation) is True

    # Invalid explanation (contains jargon)
    invalid_explanation = ExplanationData(
        pokemon_names=["Toxapex"],
        composite_score=0.70,
        type_score=0.90,
        meta_score=0.65,
        role_score=0.55,
        type_reasons=["Provides great STAB coverage"],  # "STAB" is jargon
        meta_reasons=["Walls common threats"],  # "Walls" is jargon
        role_reasons=["Use Defog for hazard removal"],  # "Defog" is jargon
        weaknesses_covered=[],
        threats_handled=[],
        roles_added=[],
    )
    with pytest.raises(ValueError, match="Jargon detected"):
        validate_explanation_jargon_free(invalid_explanation)


# T015: Write test_validate_readability() (should fail initially)
def test_validate_readability():
    """Test explanation validation for readability constraints."""
    # Valid explanation (concise)
    valid_explanation = ExplanationData(
        pokemon_names=["Rillaboom"],
        composite_score=0.80,
        type_score=0.85,
        meta_score=0.75,
        role_score=0.80,
        type_reasons=["Covers Fire weakness", "Provides Grass coverage"],
        meta_reasons=["Handles Garchomp"],
        role_reasons=["Adds hazard control"],
        weaknesses_covered=["Fire"],
        threats_handled=["Garchomp"],
        roles_added=["Hazard Control"],
    )
    assert validate_explanation_readability(valid_explanation) is True

    # Invalid - single reason too long (>50 words)
    long_reason = " ".join(["word"] * 51)  # 51 words
    invalid_single = ExplanationData(
        pokemon_names=["Test"],
        composite_score=0.70,
        type_score=0.70,
        meta_score=0.70,
        role_score=0.70,
        type_reasons=[long_reason],  # Too long
        meta_reasons=["Short"],
        role_reasons=["Short"],
        weaknesses_covered=[],
        threats_handled=[],
        roles_added=[],
    )
    with pytest.raises(ValueError, match="Reason too long"):
        validate_explanation_readability(invalid_single)

    # Invalid - total explanation too long (>150 words)
    many_reasons = [" ".join(["word"] * 40) for _ in range(4)]  # 160 words total
    invalid_total = ExplanationData(
        pokemon_names=["Test"],
        composite_score=0.70,
        type_score=0.70,
        meta_score=0.70,
        role_score=0.70,
        type_reasons=many_reasons[:2],
        meta_reasons=many_reasons[2:3],
        role_reasons=many_reasons[3:4],
        weaknesses_covered=[],
        threats_handled=[],
        roles_added=[],
    )
    with pytest.raises(ValueError, match="Total explanation too long"):
        validate_explanation_readability(invalid_total)


# ===========================
# Phase 3: User Story 1 Tests
# ===========================


# T018: Write test_extract_explanation_context() (should fail initially)
def test_extract_explanation_context():
    """Test extraction of context from team analysis for explanations."""
    from src.app.explanations import extract_explanation_context

    # Mock team data and scoring results
    user_team = ["Garchomp", "Toxapex", "Clefable"]
    recommended_trio = ["Rillaboom", "Iron Valiant", "Dragapult"]
    scoring_data = {
        "weaknesses_covered": ["Fire", "Water"],
        "threats_handled": ["Great Tusk", "Kingambit"],
        "roles_added": ["Hazard Control", "Pivot"],
    }

    context = extract_explanation_context(user_team, recommended_trio, scoring_data)

    # Verify context structure
    assert "weaknesses_covered" in context
    assert "threats_handled" in context
    assert "roles_added" in context
    assert context["weaknesses_covered"] == ["Fire", "Water"]
    assert context["threats_handled"] == ["Great Tusk", "Kingambit"]
    assert context["roles_added"] == ["Hazard Control", "Pivot"]


# T019: Write test_generate_layman_reasons_type() (should fail initially)
def test_generate_layman_reasons_type():
    """Test generation of layman-friendly type coverage reasons."""
    from src.app.explanations import _generate_type_reasons

    context = {"weaknesses_covered": ["Fire", "Ice", "Water"]}
    reasons = _generate_type_reasons(context)

    # Should generate readable reasons
    assert isinstance(reasons, list)
    assert len(reasons) > 0

    # Should mention type coverage without jargon
    for reason in reasons:
        assert not contains_jargon(reason)
        # Should mention at least one type
        assert any(
            type_name in reason for type_name in ["Fire", "Ice", "Water", "coverage"]
        )


# T020: Write test_generate_layman_reasons_meta() (should fail initially)
def test_generate_layman_reasons_meta():
    """Test generation of layman-friendly meta matchup reasons."""
    from src.app.explanations import _generate_meta_reasons

    context = {"threats_handled": ["Garchomp", "Kingambit", "Great Tusk"]}
    reasons = _generate_meta_reasons(context)

    # Should generate readable reasons
    assert isinstance(reasons, list)
    assert len(reasons) > 0

    # Should mention specific threats without jargon
    for reason in reasons:
        assert not contains_jargon(reason)
        # Should mention at least one threat
        assert any(
            threat in reason for threat in ["Garchomp", "Kingambit", "Great Tusk"]
        )


# T021: Write test_generate_layman_reasons_role() (should fail initially)
def test_generate_layman_reasons_role():
    """Test generation of layman-friendly role synergy reasons."""
    from src.app.explanations import _generate_role_reasons

    context = {"roles_added": ["Hazard Control", "Pivot", "Speed Control"]}
    reasons = _generate_role_reasons(context)

    # Should generate readable reasons
    assert isinstance(reasons, list)
    assert len(reasons) > 0

    # Should mention roles without jargon
    for reason in reasons:
        assert not contains_jargon(reason)


# T022: Write test_generate_explanation_complete() (should fail initially)
def test_generate_explanation_complete():
    """Test complete explanation generation with all components."""
    from src.app.explanations import generate_explanation

    # Full scoring data
    user_team = ["Garchomp", "Toxapex", "Clefable"]
    recommended_trio = ["Rillaboom", "Iron Valiant", "Dragapult"]
    scores = {
        "composite_score": 0.82,
        "type_score": 0.85,
        "meta_score": 0.78,
        "role_score": 0.83,
        "weaknesses_covered": ["Fire", "Water"],
        "threats_handled": ["Great Tusk", "Kingambit"],
        "roles_added": ["Hazard Control", "Pivot"],
    }

    explanation = generate_explanation(user_team, recommended_trio, scores)

    # Verify structure
    assert isinstance(explanation, ExplanationData)
    assert explanation.pokemon_names == recommended_trio
    assert explanation.composite_score == 0.82
    assert explanation.type_score == 0.85
    assert explanation.meta_score == 0.78
    assert explanation.role_score == 0.83

    # Verify all reason lists exist
    assert isinstance(explanation.type_reasons, list)
    assert isinstance(explanation.meta_reasons, list)
    assert isinstance(explanation.role_reasons, list)

    # Verify jargon-free
    assert validate_explanation_jargon_free(explanation)

    # Verify readable
    assert validate_explanation_readability(explanation)


# T023: Write test_format_layman_explanation() (should fail initially)
def test_format_layman_explanation():
    """Test formatting of layman explanation as markdown."""
    from src.app.explanations import format_layman_explanation

    explanation = ExplanationData(
        pokemon_names=["Rillaboom", "Iron Valiant", "Dragapult"],
        composite_score=0.82,
        type_score=0.85,
        meta_score=0.78,
        role_score=0.83,
        type_reasons=["Covers your Fire weakness", "Provides Water resistance"],
        meta_reasons=["Can handle popular threats like Garchomp"],
        role_reasons=["Provides hazard removal support"],
        weaknesses_covered=["Fire"],
        threats_handled=["Garchomp"],
        roles_added=["Hazard Control"],
    )

    markdown = format_layman_explanation(explanation)

    # Should be formatted markdown string
    assert isinstance(markdown, str)
    assert len(markdown) > 0

    # Should include Pokemon names
    assert "Rillaboom" in markdown
    assert "Iron Valiant" in markdown
    assert "Dragapult" in markdown

    # Should include reasons
    assert "Covers your Fire weakness" in markdown
    assert "Can handle popular threats like Garchomp" in markdown
    assert "Provides hazard removal support" in markdown

    # Should use markdown formatting (bullets or checkmarks)
    assert any(marker in markdown for marker in ["✓", "✅", "•", "-", "*"])
