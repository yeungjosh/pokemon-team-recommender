"""Placeholder greedy search for assembling Pokémon trios."""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence


def greedy_complete_team(
    core: Sequence[str],
    candidates: Sequence[Dict[str, object]],
    top_k: int = 5,
) -> List[Dict[str, object]]:
    """Return a mock ranking of trios until the full implementation lands."""

    seen = {name.lower() for name in core}
    filtered = [mon for mon in candidates if str(mon.get("name", "")).lower() not in seen]
    return filtered[:top_k]


__all__ = ["greedy_complete_team"]
