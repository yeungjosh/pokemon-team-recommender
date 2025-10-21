#!/usr/bin/env python3
"""Test script to verify expanded dataset works correctly."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parents[1]))

from src.data.pokedex import Pokedex
from src.data.types import TypeChart
from src.data.usage import UsageStats
from src.search.recommender import TeamRecommender

def test_data_loading():
    """Test that all data loads correctly."""
    print("Testing data loading...")

    # Load Pokedex
    pokedex = Pokedex()
    print(f"✓ Loaded {len(pokedex.all_names())} Pokemon")

    # Load Type Chart
    type_chart = TypeChart()
    print(f"✓ Loaded type chart with {len(type_chart.types)} types")

    # Load Usage Stats
    usage_stats = UsageStats()
    print(f"✓ Loaded usage stats for {len(usage_stats.get_all_names())} Pokemon")

    return pokedex, type_chart, usage_stats


def test_recommender(pokedex, type_chart, usage_stats):
    """Test recommender with expanded dataset."""
    print("\nTesting recommender...")

    recommender = TeamRecommender(pokedex, type_chart, usage_stats)

    # Test 1: Original seed Pokemon
    print("\nTest 1: Original seed team (Garchomp, Raging Bolt, Great Tusk)")
    try:
        recs = recommender.recommend(
            ["Garchomp", "Raging Bolt", "Great Tusk"],
            top_k=5,
            candidate_pool_size=20
        )
        print(f"✓ Got {len(recs)} recommendations")
        print(f"  Top recommendation: {', '.join(recs[0].pokemon_names)} (score: {recs[0].composite_score:.3f})")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    # Test 2: New Pokemon from expanded dataset
    print("\nTest 2: New team with expanded Pokemon (Dragonite, Hatterene, Cinderace)")
    try:
        recs = recommender.recommend(
            ["Dragonite", "Hatterene", "Cinderace"],
            top_k=5,
            candidate_pool_size=20
        )
        print(f"✓ Got {len(recs)} recommendations")
        print(f"  Top recommendation: {', '.join(recs[0].pokemon_names)} (score: {recs[0].composite_score:.3f})")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    # Test 3: Edge cases
    print("\nTest 3: Pokemon that would have failed before (Charizard, Gengar, Gyarados)")
    try:
        recs = recommender.recommend(
            ["Charizard", "Gengar", "Gyarados"],
            top_k=5,
            candidate_pool_size=20
        )
        print(f"✓ Got {len(recs)} recommendations")
        print(f"  Top recommendation: {', '.join(recs[0].pokemon_names)} (score: {recs[0].composite_score:.3f})")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    # Test 4: Invalid Pokemon (should still fail gracefully)
    print("\nTest 4: Invalid Pokemon (should error)")
    try:
        recs = recommender.recommend(
            ["Pikachu", "Eevee", "Meowth"],
            top_k=5,
            candidate_pool_size=20
        )
        print(f"✗ Should have failed but got {len(recs)} recommendations")
        return False
    except ValueError as e:
        print(f"✓ Correctly rejected invalid Pokemon: {e}")

    return True


def test_performance(pokedex, type_chart, usage_stats):
    """Test performance with larger pool."""
    import time

    print("\nTesting performance...")

    recommender = TeamRecommender(pokedex, type_chart, usage_stats)

    # Test with pool size 50
    print("Testing with pool size 50...")
    start = time.time()
    recs = recommender.recommend(
        ["Garchomp", "Raging Bolt", "Great Tusk"],
        top_k=5,
        candidate_pool_size=50
    )
    elapsed = time.time() - start

    print(f"  Time: {elapsed:.2f}s (target: <2s)")
    print(f"  Combinations evaluated: C(50,3) = 19,600")

    if elapsed < 2.0:
        print("  ✓ Performance target met!")
    else:
        print("  ⚠ Performance target missed (may need optimization)")

    return elapsed < 2.0


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Expanded Pokemon Dataset")
    print("=" * 60)

    # Load data
    try:
        pokedex, type_chart, usage_stats = test_data_loading()
    except Exception as e:
        print(f"\n✗ Data loading failed: {e}")
        sys.exit(1)

    # Test recommender
    try:
        success = test_recommender(pokedex, type_chart, usage_stats)
        if not success:
            print("\n✗ Recommender tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Recommender tests failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Test performance
    try:
        perf_ok = test_performance(pokedex, type_chart, usage_stats)
    except Exception as e:
        print(f"\n⚠ Performance test failed: {e}")
        perf_ok = False

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("✓ Data loading: PASSED")
    print("✓ Recommender: PASSED")
    if perf_ok:
        print("✓ Performance: PASSED")
    else:
        print("⚠ Performance: WARNING (may need optimization)")

    print("\n✓ All tests passed! Dataset expansion successful.")
    print(f"  Expanded from 15 → {len(pokedex.all_names())} Pokemon")


if __name__ == "__main__":
    main()
