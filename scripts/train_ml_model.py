"""Train the hybrid ML+Rules recommendation model."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[1]))

from src.data.pokedex import Pokedex
from src.data.types import TypeChart
from src.data.usage import UsageStats
from src.ml.hybrid_ranker import HybridRanker


def main():
    """Train and save the hybrid ML model."""
    print("=" * 60)
    print("Training Hybrid ML+Rules Team Recommender")
    print("=" * 60)

    # Load data
    print("\n1. Loading data...")
    pokedex = Pokedex()
    type_chart = TypeChart()
    usage_stats = UsageStats()
    print(f"   ✓ Loaded {len(pokedex.pokemon)} Pokémon")

    # Initialize and train model
    print("\n2. Initializing ML model...")
    ranker = HybridRanker()

    print("\n3. Training model...")
    ranker.train(
        pokedex=pokedex,
        type_chart=type_chart,
        usage_stats=usage_stats,
        n_samples=10000,  # Generate 10k synthetic teams
    )

    # Save model
    print("\n4. Saving model...")
    model_path = Path(__file__).parents[1] / "models" / "hybrid_ranker.pkl"
    model_path.parent.mkdir(exist_ok=True)
    ranker.save(model_path)

    print("\n" + "=" * 60)
    print("✓ Training complete!")
    print(f"✓ Model saved to: {model_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
