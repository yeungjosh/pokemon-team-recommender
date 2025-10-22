"""Train the actual ML model."""
from src.data.pokedex import Pokedex
from src.data.types import TypeChart
from src.data.usage import UsageStats
from src.ml.hybrid_ranker import HybridRanker
from pathlib import Path

print("Loading data...")
pokedex = Pokedex()
type_chart = TypeChart()
usage_stats = UsageStats()

print("\nTraining model...")
ranker = HybridRanker()
ranker.train(pokedex, type_chart, usage_stats, n_samples=10000)

print("\nSaving model...")
model_path = Path("models/hybrid_ranker.pkl")
model_path.parent.mkdir(exist_ok=True)
ranker.save(model_path)

print("\n✅ Done! Model saved to models/hybrid_ranker.pkl")
print("\nFeature importances show the 'learned weights':")
print("Re-run to see if meta > type (as README claims)")
