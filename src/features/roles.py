"""Basic role tagging heuristics."""

from __future__ import annotations

from typing import Dict, Iterable, List, Set

ROLE_KEYWORDS: Dict[str, Set[str]] = {
    "hazard-setter": {"stealth-rock", "spikes", "toxic-spikes"},
    "hazard-removal": {"rapid-spin", "defog", "mortal-spin"},
    "pivot": {"u-turn", "volt-switch", "flip-turn"},
    "speed-control": {"thunder-wave", "icy-wind", "tailwind", "sticky-web"},
}


def infer_roles(learnset: Iterable[str]) -> List[str]:
    """Return a list of role tags inferred from a learnset."""

    moves = {move.lower() for move in learnset}
    roles: Set[str] = set()
    for role, keywords in ROLE_KEYWORDS.items():
        if moves & keywords:
            roles.add(role)
    return sorted(roles)


__all__ = ["infer_roles", "ROLE_KEYWORDS"]
