"""Evaluate claim extraction and mapping against golden test set."""
import json
import sys
from pathlib import Path

# Add ETL to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from app.tasks.extract_claims import extract_with_regex
from app.tasks.link_entities import link_benchmark_by_name, link_signpost_by_metric


def load_golden_set():
    """Load golden test set."""
    path = Path(__file__).parent.parent / "infra" / "seeds" / "goldset.json"
    with open(path) as f:
        return json.load(f)


def evaluate_extraction(examples):
    """Evaluate claim extraction accuracy."""
    correct = 0
    total = len(examples)
    
    for example in examples:
        snippet = example["news_snippet"]
        expected = example["expected_claims"][0] if example["expected_claims"] else None
        
        if not expected:
            continue
        
        # Extract using regex (deterministic)
        extracted = extract_with_regex(snippet, "")
        
        if extracted:
            # Check if metric name and value match
            name_match = extracted.get("metric_name") == expected["metric_name"]
            value_match = abs(float(extracted.get("metric_value", 0)) - expected["metric_value"]) < 0.1
            
            if name_match and value_match:
                correct += 1
                print(f"✓ Example {example['id']}: Correct")
            else:
                print(f"✗ Example {example['id']}: Incorrect - Got {extracted}")
        else:
            print(f"✗ Example {example['id']}: No extraction")
    
    accuracy = correct / total if total > 0 else 0.0
    print(f"\n📊 Extraction Accuracy: {accuracy:.1%} ({correct}/{total})")
    return accuracy


def evaluate_mapping(examples):
    """Evaluate benchmark/signpost mapping accuracy."""
    # Note: This requires database access for full evaluation
    # For now, we'll just test the logic without DB
    
    print("\n🔗 Mapping Evaluation (Logic Test):")
    
    for example in examples:
        expected_benchmarks = example.get("expected_benchmarks", [])
        
        if not example["expected_claims"]:
            continue
        
        claim = example["expected_claims"][0]
        metric_name = claim["metric_name"]
        
        # Test benchmark linking (without DB)
        print(f"  Example {example['id']}: {metric_name}")
        print(f"    Expected benchmarks: {expected_benchmarks}")
    
    print("\n  ℹ️  Full mapping evaluation requires database access")
    print("     Run with initialized DB to compute F1 score")


def main():
    """Main evaluation function."""
    print("📋 Loading golden test set...\n")
    
    golden_set = load_golden_set()
    examples = golden_set["examples"]
    
    print(f"Loaded {len(examples)} test examples\n")
    print("=" * 60)
    
    # Evaluate extraction
    accuracy = evaluate_extraction(examples)
    
    # Evaluate mapping (requires DB)
    evaluate_mapping(examples)
    
    print("\n" + "=" * 60)
    
    # Check threshold
    THRESHOLD = 0.75
    if accuracy >= THRESHOLD:
        print(f"✅ PASS: Extraction accuracy {accuracy:.1%} >= {THRESHOLD:.1%}")
        return 0
    else:
        print(f"❌ FAIL: Extraction accuracy {accuracy:.1%} < {THRESHOLD:.1%}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

