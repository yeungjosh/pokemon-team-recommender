"""Hybrid ML+Rules recommendation model.

Uses rule-based scoring as features and learns optimal weights via ML.
"""

import json
from pathlib import Path
from typing import List, Tuple

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split

from src.data.pokedex import Pokedex, Pokemon
from src.data.types import TypeChart
from src.data.usage import UsageStats
from src.features.coverage import CoverageAnalyzer
from src.features.meta import MetaAnalyzer
from src.features.roles import RoleDetector


class HybridRanker:
    """ML model that learns to rank teams using rule-based features."""

    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=4,
            random_state=42,
        )
        self.is_trained = False

    def extract_features(
        self,
        team: List[Pokemon],
        coverage_analyzer: CoverageAnalyzer,
        meta_analyzer: MetaAnalyzer,
    ) -> np.ndarray:
        """Extract features from a team for ML model.

        Features:
        - type_score (offensive + defensive)
        - meta_score
        - role_score
        - Additional derived features:
          - avg_speed
          - type_diversity (unique types)
          - physical_special_balance
        """
        # Core rule-based scores
        type_score = coverage_analyzer.type_coverage_score(team)
        meta_score = meta_analyzer.meta_coverage_score(team)
        role_score = RoleDetector.role_diversity_score(team)

        # Derived features
        avg_speed = np.mean([p.speed for p in team])
        unique_types = len(set(t for p in team for t in p.types))
        type_diversity = unique_types / 18  # Normalize to 0-1

        # Physical/Special balance
        avg_atk = np.mean([p.base_stats["atk"] for p in team])
        avg_spa = np.mean([p.base_stats["spa"] for p in team])
        balance = 1.0 - abs(avg_atk - avg_spa) / max(avg_atk, avg_spa, 1)

        # Team bulk (defensive stats)
        avg_hp = np.mean([p.base_stats["hp"] for p in team])
        avg_def = np.mean([p.base_stats["def"] for p in team])
        avg_spd = np.mean([p.base_stats["spd"] for p in team])
        bulk = (avg_hp + avg_def + avg_spd) / 300  # Normalize

        return np.array([
            type_score,
            meta_score,
            role_score,
            avg_speed / 150,  # Normalize (max speed ~150)
            type_diversity,
            balance,
            bulk,
        ])

    def generate_training_data(
        self,
        pokedex: Pokedex,
        type_chart: TypeChart,
        usage_stats: UsageStats,
        n_samples: int = 5000,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data.

        Strategy:
        1. Sample random teams
        2. Use rule-based composite score as target
        3. Add noise to simulate real preferences
        4. Weight by usage stats (popular Pokemon = better teams)
        """
        coverage_analyzer = CoverageAnalyzer(type_chart)
        meta_analyzer = MetaAnalyzer(type_chart, pokedex, usage_stats)

        X = []
        y = []

        all_pokemon = list(pokedex.pokemon.values())
        np.random.seed(42)

        for _ in range(n_samples):
            # Sample 6 random Pokemon for a team
            team = list(np.random.choice(all_pokemon, size=6, replace=False))

            # Extract features
            features = self.extract_features(team, coverage_analyzer, meta_analyzer)
            X.append(features)

            # Compute target score (current rule-based composite)
            type_score = features[0]
            meta_score = features[1]
            role_score = features[2]

            # Original weights: 0.4, 0.4, 0.2
            base_score = 0.4 * type_score + 0.4 * meta_score + 0.2 * role_score

            # Add small noise to simulate preference variation
            noise = np.random.normal(0, 0.05)
            target_score = np.clip(base_score + noise, 0, 1)

            # Boost score if team uses popular Pokemon
            avg_usage = np.mean([usage_stats.get_usage(p.name) for p in team])
            usage_boost = avg_usage / 100 * 0.1  # Up to 10% boost
            target_score = min(target_score + usage_boost, 1.0)

            y.append(target_score)

        return np.array(X), np.array(y)

    def train(
        self,
        pokedex: Pokedex,
        type_chart: TypeChart,
        usage_stats: UsageStats,
        n_samples: int = 5000,
    ):
        """Train the ML model on synthetic data."""
        print(f"Generating {n_samples} training samples...")
        X, y = self.generate_training_data(pokedex, type_chart, usage_stats, n_samples)

        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        print(f"Training on {len(X_train)} samples...")
        self.model.fit(X_train, y_train)

        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        print(f"✓ Training R²: {train_score:.4f}")
        print(f"✓ Test R²: {test_score:.4f}")

        # Feature importance
        feature_names = [
            "type_score",
            "meta_score",
            "role_score",
            "avg_speed",
            "type_diversity",
            "balance",
            "bulk",
        ]
        importances = self.model.feature_importances_
        print("\nFeature Importances:")
        for name, imp in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
            print(f"  {name:20s}: {imp:.4f}")

        self.is_trained = True

    def predict(
        self,
        team: List[Pokemon],
        coverage_analyzer: CoverageAnalyzer,
        meta_analyzer: MetaAnalyzer,
    ) -> float:
        """Predict team quality score using trained ML model."""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        features = self.extract_features(team, coverage_analyzer, meta_analyzer)
        score = self.model.predict([features])[0]
        return float(np.clip(score, 0, 1))

    def save(self, path: Path):
        """Save trained model to disk."""
        joblib.dump(self.model, path, compress=3)
        print(f"Model saved to {path}")

    def load(self, path: Path):
        """Load trained model from disk."""
        self.model = joblib.load(path)
        self.is_trained = True
        print(f"Model loaded from {path}")
