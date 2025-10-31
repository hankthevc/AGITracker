#!/usr/bin/env python3
"""
Test LLM budget tracking and enforcement.

Usage:
    python scripts/test_llm_budget.py --scenario [normal|warning|blocked]
"""
import argparse
import sys
from pathlib import Path

# Add services/etl to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from app.utils.llm_budget import check_budget, record_spend, get_budget_status


def test_normal_usage():
    """Test normal usage within limits."""
    print("\n" + "="*60)
    print("TEST 1: Normal Usage (Under $20)")
    print("="*60)
    
    # Simulate 10 small LLM calls ($0.50 each = $5 total)
    print("\n📊 Simulating 10 LLM calls at $0.50 each...")
    for i in range(10):
        record_spend(0.50, "gpt-4o-mini")
        budget = check_budget()
        print(f"  Call {i+1}: ${budget['current_spend_usd']:.2f} / ${budget['hard_limit_usd']:.2f}")
    
    # Check final status
    budget = check_budget()
    status = get_budget_status()
    
    print(f"\n✅ Final Status:")
    print(f"  Total Spend: ${budget['current_spend_usd']:.2f}")
    print(f"  Warning: {budget['warning']}")
    print(f"  Blocked: {budget['blocked']}")
    print(f"  Status: {status['status']}")
    print(f"  Message: {status['message']}")
    
    assert budget['current_spend_usd'] == 5.0, "Spend should be $5.00"
    assert not budget['warning'], "Should not trigger warning"
    assert not budget['blocked'], "Should not be blocked"
    assert status['status'] == "OK", "Status should be OK"
    
    print("\n✅ Normal usage test PASSED")


def test_warning_threshold():
    """Test warning threshold at $20."""
    print("\n" + "="*60)
    print("TEST 2: Warning Threshold ($20)")
    print("="*60)
    
    # Simulate spending to just above warning threshold
    print("\n📊 Simulating LLM calls to reach $22...")
    
    # Add $17 more to reach $22 total (5 from previous test)
    record_spend(17.0, "gpt-4o-mini")
    budget = check_budget()
    
    print(f"\n⚠️  Final Status:")
    print(f"  Total Spend: ${budget['current_spend_usd']:.2f}")
    print(f"  Warning Threshold: ${budget['warning_threshold_usd']:.2f}")
    print(f"  Warning: {budget['warning']}")
    print(f"  Blocked: {budget['blocked']}")
    print(f"  Remaining: ${budget['remaining_usd']:.2f}")
    
    status = get_budget_status()
    print(f"  Status: {status['status']}")
    print(f"  Message: {status['message']}")
    
    assert budget['current_spend_usd'] >= 20.0, "Spend should be >= $20.00"
    assert budget['warning'], "Should trigger warning"
    assert not budget['blocked'], "Should not be blocked yet"
    assert status['status'] == "WARNING", "Status should be WARNING"
    
    print("\n⚠️  Warning threshold test PASSED")


def test_hard_limit():
    """Test hard limit at $50."""
    print("\n" + "="*60)
    print("TEST 3: Hard Limit ($50)")
    print("="*60)
    
    # Simulate spending to hard limit
    print("\n📊 Simulating LLM calls to reach $52...")
    
    # Add $30 more to reach $52 total (22 from previous tests)
    record_spend(30.0, "gpt-4o-mini")
    budget = check_budget()
    
    print(f"\n🛑 Final Status:")
    print(f"  Total Spend: ${budget['current_spend_usd']:.2f}")
    print(f"  Hard Limit: ${budget['hard_limit_usd']:.2f}")
    print(f"  Warning: {budget['warning']}")
    print(f"  Blocked: {budget['blocked']}")
    print(f"  Remaining: ${budget['remaining_usd']:.2f}")
    
    status = get_budget_status()
    print(f"  Status: {status['status']}")
    print(f"  Message: {status['message']}")
    
    assert budget['current_spend_usd'] >= 50.0, "Spend should be >= $50.00"
    assert budget['warning'], "Should trigger warning"
    assert budget['blocked'], "Should be BLOCKED"
    assert status['status'] == "BLOCKED", "Status should be BLOCKED"
    assert budget['remaining_usd'] == 0.0, "Remaining should be $0.00"
    
    print("\n🛑 Hard limit test PASSED")


def test_budget_check_only():
    """Just check current budget status without adding spend."""
    print("\n" + "="*60)
    print("CURRENT BUDGET STATUS")
    print("="*60)
    
    budget = check_budget()
    status = get_budget_status()
    
    print(f"\n📊 Budget Details:")
    print(f"  Date: {budget['date']}")
    print(f"  Current Spend: ${budget['current_spend_usd']:.2f}")
    print(f"  Warning Threshold: ${budget['warning_threshold_usd']:.2f}")
    print(f"  Hard Limit: ${budget['hard_limit_usd']:.2f}")
    print(f"  Remaining: ${budget['remaining_usd']:.2f}")
    print(f"\n🚦 Status:")
    print(f"  Warning: {budget['warning']}")
    print(f"  Blocked: {budget['blocked']}")
    print(f"  Status: {status['status']}")
    print(f"  Message: {status['message']}")
    
    if budget.get('redis_unavailable'):
        print(f"\n⚠️  WARNING: Redis is unavailable. Budget tracking disabled.")
        print(f"     Start Redis: brew services start redis")


def reset_budget():
    """Reset today's budget (for testing only)."""
    print("\n" + "="*60)
    print("RESET BUDGET")
    print("="*60)
    
    from app.utils.llm_budget import get_redis_client
    from datetime import UTC, datetime
    
    r = get_redis_client()
    if not r:
        print("⚠️  Redis unavailable, cannot reset budget")
        return
    
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    key = f"llm_budget:daily:{today}"
    
    old_value = r.get(key)
    r.delete(key)
    
    print(f"✅ Budget reset for {today}")
    print(f"   Previous value: ${old_value or '0.00'}")
    print(f"   New value: $0.00")


def main():
    parser = argparse.ArgumentParser(description="Test LLM budget tracking")
    parser.add_argument(
        "--scenario",
        choices=["check", "normal", "warning", "blocked", "full", "reset"],
        default="check",
        help="Which test scenario to run"
    )
    args = parser.parse_args()
    
    print("="*60)
    print("🧪 LLM BUDGET TESTING")
    print("="*60)
    
    try:
        if args.scenario == "check":
            test_budget_check_only()
        
        elif args.scenario == "reset":
            reset_budget()
        
        elif args.scenario == "normal":
            reset_budget()
            test_normal_usage()
        
        elif args.scenario == "warning":
            reset_budget()
            test_normal_usage()
            test_warning_threshold()
        
        elif args.scenario == "blocked":
            reset_budget()
            test_normal_usage()
            test_warning_threshold()
            test_hard_limit()
        
        elif args.scenario == "full":
            reset_budget()
            test_normal_usage()
            test_warning_threshold()
            test_hard_limit()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nNotes:")
        print("  - Budget resets daily (keyed by YYYY-MM-DD)")
        print("  - Warning threshold: $20/day")
        print("  - Hard limit: $50/day")
        print("  - Real LLM calls will use record_spend() automatically")
        print("\nProduction:")
        print("  - Monitor: curl -H 'x-api-key: YOUR_KEY' http://localhost:8000/v1/admin/llm-budget")
        print("  - Railway: railway run curl -H 'x-api-key: $ADMIN_API_KEY' $API_URL/v1/admin/llm-budget")
        
        return 0
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

