"""Data loading utilities for the Pokémon Team Recommender MVP."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"


def load_type_chart(path: Path | None = None) -> Dict[str, Dict[str, float]]:
    """Load the attacking → defending type effectiveness mapping."""

    path = path or DATA_RAW / "type_chart.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_pokedex(path: Path | None = None) -> List[Dict[str, Any]]:
    """Load the dex snapshot with base stats, typings, and learnsets."""

    path = path or DATA_RAW / "pokedex.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_usage(path: Path | None = None) -> List[Dict[str, Any]]:
    """Load the tier usage statistics as a list of dict rows."""

    path = path or DATA_RAW / "usage_ou.csv"
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def load_meta_topk(path: Path | None = None) -> Dict[str, Any]:
    """Load the cached top meta Pokémon payload."""

    path = path or DATA_PROCESSED / "meta_topk.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_mon_features(path: Path | None = None) -> List[Dict[str, Any]]:
    """Load pre-computed per-Pokémon feature rows."""

    path = path or DATA_PROCESSED / "mon_features.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


__all__ = [
    "load_type_chart",
    "load_pokedex",
    "load_usage",
    "load_meta_topk",
    "load_mon_features",
]
