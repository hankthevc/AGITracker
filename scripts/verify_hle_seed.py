#!/usr/bin/env python3
"""
Verify HLE (Humanity's Last Exam) benchmark and signposts are properly seeded.

Prints DB rows for humanitys_last_exam_text benchmark and hle_text_* signposts.
Exit code 0 if all present, 1 if any missing.
"""
import sys
from pathlib import Path

# Add services/etl to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from app.database import SessionLocal
from app.models import Benchmark, Signpost


def verify_hle_seeds():
    """Verify HLE benchmark and signposts exist in database."""
    db = SessionLocal()
    
    print("═══ HLE Seed Verification ═══\n")
    
    # Check benchmark
    print("1. Benchmark:")
    benchmark = db.query(Benchmark).filter(
        Benchmark.code == "humanitys_last_exam_text"
    ).first()
    
    if benchmark:
        print(f"   ✓ {benchmark.code}")
        print(f"     Name: {benchmark.name}")
        print(f"     Family: {benchmark.family}")
        print(f"     URL: {benchmark.url}")
        benchmark_ok = True
    else:
        print("   ❌ humanitys_last_exam_text NOT FOUND")
        benchmark_ok = False
    
    # Check signposts
    print("\n2. Signposts:")
    signposts = db.query(Signpost).filter(
        Signpost.code.in_(["hle_text_50", "hle_text_70"])
    ).all()
    
    expected_codes = {"hle_text_50", "hle_text_70"}
    found_codes = {sp.code for sp in signposts}
    
    for sp in signposts:
        print(f"   ✓ {sp.code}")
        print(f"     Name: {sp.name}")
        print(f"     Category: {sp.category}")
        print(f"     First-class: {sp.first_class}")
        print(f"     Baseline: {sp.baseline_value}, Target: {sp.target_value}")
    
    missing = expected_codes - found_codes
    if missing:
        for code in missing:
            print(f"   ❌ {code} NOT FOUND")
        signposts_ok = False
    else:
        signposts_ok = True
    
    db.close()
    
    # Summary
    print("\n" + "─" * 40)
    if benchmark_ok and signposts_ok:
        print("✅ All HLE seeds present")
        return 0
    else:
        print("❌ Some HLE seeds missing")
        if not benchmark_ok:
            print("   - Benchmark: humanitys_last_exam_text")
        if not signposts_ok:
            print(f"   - Signposts: {', '.join(missing)}")
        return 1


if __name__ == "__main__":
    sys.exit(verify_hle_seeds())

