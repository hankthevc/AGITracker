#!/usr/bin/env python3
"""
Verify deduplication is working correctly.

Checks for:
- Duplicate URLs
- Duplicate content hashes
- Duplicate dedup_hashes

Usage:
    python scripts/verify_dedup.py
"""
import sys
from pathlib import Path

# Add services/etl to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from app.database import SessionLocal
from app.models import Event
from sqlalchemy import func


def check_duplicates():
    """Check for various types of duplicates."""
    db = SessionLocal()
    
    print("="*60)
    print("🔍 DEDUPLICATION VERIFICATION")
    print("="*60)
    
    try:
        # Total events
        total_events = db.query(Event).count()
        print(f"\n📊 Total events in database: {total_events}")
        
        # Check for duplicate URLs
        print("\n" + "-"*60)
        print("1. Checking for duplicate URLs...")
        print("-"*60)
        
        duplicates_url = (
            db.query(Event.source_url, func.count(Event.id).label('count'))
            .group_by(Event.source_url)
            .having(func.count(Event.id) > 1)
            .all()
        )
        
        if duplicates_url:
            print(f"⚠️  Found {len(duplicates_url)} duplicate URLs:")
            for url, count in duplicates_url[:10]:  # Show first 10
                print(f"  - {url[:80]}... ({count} entries)")
                
                # Show the duplicate event IDs
                events = db.query(Event.id, Event.title).filter(Event.source_url == url).all()
                for event_id, title in events:
                    print(f"    ID {event_id}: {title[:60]}...")
            
            if len(duplicates_url) > 10:
                print(f"  ... and {len(duplicates_url) - 10} more")
        else:
            print("✅ No duplicate URLs found")
        
        # Check for duplicate content_hash
        print("\n" + "-"*60)
        print("2. Checking for duplicate content hashes...")
        print("-"*60)
        
        duplicates_content = (
            db.query(Event.content_hash, func.count(Event.id).label('count'))
            .filter(Event.content_hash.isnot(None))
            .group_by(Event.content_hash)
            .having(func.count(Event.id) > 1)
            .all()
        )
        
        if duplicates_content:
            print(f"⚠️  Found {len(duplicates_content)} duplicate content hashes:")
            for hash_val, count in duplicates_content[:10]:
                print(f"  - {hash_val[:16]}... ({count} entries)")
                
                # Show the duplicate event IDs
                events = db.query(Event.id, Event.title).filter(Event.content_hash == hash_val).all()
                for event_id, title in events:
                    print(f"    ID {event_id}: {title[:60]}...")
            
            if len(duplicates_content) > 10:
                print(f"  ... and {len(duplicates_content) - 10} more")
        else:
            print("✅ No duplicate content hashes found")
        
        # Check for duplicate dedup_hash (Phase A)
        print("\n" + "-"*60)
        print("3. Checking for duplicate dedup_hashes (Phase A)...")
        print("-"*60)
        
        duplicates_dedup = (
            db.query(Event.dedup_hash, func.count(Event.id).label('count'))
            .filter(Event.dedup_hash.isnot(None))
            .group_by(Event.dedup_hash)
            .having(func.count(Event.id) > 1)
            .all()
        )
        
        if duplicates_dedup:
            print(f"⚠️  Found {len(duplicates_dedup)} duplicate dedup_hashes:")
            for hash_val, count in duplicates_dedup[:10]:
                print(f"  - {hash_val[:16]}... ({count} entries)")
                
                # Show the duplicate event IDs
                events = db.query(Event.id, Event.title, Event.source_domain, Event.published_at).filter(Event.dedup_hash == hash_val).all()
                for event_id, title, domain, published in events:
                    print(f"    ID {event_id}: {title[:50]}...")
                    print(f"       Domain: {domain}, Published: {published}")
            
            if len(duplicates_dedup) > 10:
                print(f"  ... and {len(duplicates_dedup) - 10} more")
        else:
            print("✅ No duplicate dedup_hashes found")
        
        # Events breakdown by source type
        print("\n" + "-"*60)
        print("4. Events breakdown by source type...")
        print("-"*60)
        
        by_type = (
            db.query(Event.source_type, func.count(Event.id).label('count'))
            .group_by(Event.source_type)
            .order_by(func.count(Event.id).desc())
            .all()
        )
        
        for source_type, count in by_type:
            print(f"  {source_type or 'null'}: {count} events")
        
        # Events breakdown by evidence tier
        print("\n" + "-"*60)
        print("5. Events breakdown by evidence tier...")
        print("-"*60)
        
        by_tier = (
            db.query(Event.evidence_tier, func.count(Event.id).label('count'))
            .group_by(Event.evidence_tier)
            .order_by(Event.evidence_tier)
            .all()
        )
        
        for tier, count in by_tier:
            print(f"  Tier {tier or 'null'}: {count} events")
        
        # Summary
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        
        total_duplicates = len(duplicates_url) + len(duplicates_content) + len(duplicates_dedup)
        
        if total_duplicates == 0:
            print("✅ Deduplication is working correctly!")
            print(f"   {total_events} unique events in database")
        else:
            print(f"⚠️  Found {total_duplicates} duplicate entries")
            print("   This may indicate:")
            print("   - Deduplication logic needs improvement")
            print("   - Events were imported before dedup_hash was added")
            print("   - Different versions of same event (legitimate updates)")
        
        print("\nNext steps:")
        if total_duplicates > 0:
            print("  1. Review duplicate entries above")
            print("  2. Decide if they're legitimate or should be merged")
            print("  3. Consider running migration to consolidate duplicates")
        else:
            print("  1. Continue monitoring with each ingestion run")
            print("  2. Set up automated duplicate alerts")
        
        return total_duplicates
    
    finally:
        db.close()


if __name__ == "__main__":
    duplicate_count = check_duplicates()
    sys.exit(0 if duplicate_count == 0 else 1)

