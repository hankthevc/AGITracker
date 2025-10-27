#!/usr/bin/env python3
"""
Test script for news ingestion pipeline (Phase A/B/C).

Tests:
1. Run ingestors with fixtures
2. Map events to signposts
3. Check B-tier corroboration
4. Verify database state

Usage:
    python3 scripts/test_ingestion_pipeline.py
"""
import sys
from pathlib import Path

# Add services/etl to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from app.database import SessionLocal
from app.models import Event, EventSignpostLink, IngestRun
from app.tasks.news.ingest_arxiv import ingest_arxiv_task
from app.tasks.news.ingest_company_blogs import ingest_company_blogs_task
from app.tasks.news.ingest_press_reuters_ap import ingest_press_reuters_ap_task
from app.tasks.news.map_events_to_signposts import map_events_to_signposts_task
from app.tasks.mapping.check_b_tier_corroboration import check_b_tier_corroboration_task


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_ingestion():
    """Test all ingestors."""
    print_section("Phase B: Testing Ingestors")
    
    # Test arXiv ingestor (A-tier)
    print("📚 Running arXiv ingestor...")
    arxiv_stats = ingest_arxiv_task()
    print(f"   Result: {arxiv_stats}")
    
    # Test company blogs ingestor (B-tier)
    print("\n📰 Running company blogs ingestor...")
    blogs_stats = ingest_company_blogs_task()
    print(f"   Result: {blogs_stats}")
    
    # Test press ingestor (C-tier)
    print("\n📰 Running press ingestor...")
    press_stats = ingest_press_reuters_ap_task()
    print(f"   Result: {press_stats}")
    
    return {
        "arxiv": arxiv_stats,
        "blogs": blogs_stats,
        "press": press_stats
    }


def test_mapping():
    """Test event→signpost mapping."""
    print_section("Phase C: Testing Event Mapping")
    
    print("🔗 Running event mapper...")
    mapping_stats = map_events_to_signposts_task()
    print(f"   Result: {mapping_stats}")
    
    return mapping_stats


def test_corroboration():
    """Test B-tier corroboration."""
    print_section("Phase C: Testing B-tier Corroboration")
    
    print("🔗 Running B-tier corroboration check...")
    corr_stats = check_b_tier_corroboration_task()
    print(f"   Result: {corr_stats}")
    
    return corr_stats


def verify_database_state():
    """Verify database state after pipeline."""
    print_section("Verification: Database State")
    
    db = SessionLocal()
    
    try:
        # Count events by tier
        print("📊 Events by tier:")
        for tier in ['A', 'B', 'C', 'D']:
            count = db.query(Event).filter(Event.evidence_tier == tier).count()
            print(f"   {tier}-tier: {count} events")
        
        # Count events by source_type
        print("\n📊 Events by source type:")
        for source_type in ['paper', 'blog', 'news', 'leaderboard', 'gov']:
            count = db.query(Event).filter(Event.source_type == source_type).count()
            if count > 0:
                print(f"   {source_type}: {count} events")
        
        # Count event→signpost links by tier
        print("\n🔗 Event→Signpost links by tier:")
        for tier in ['A', 'B', 'C', 'D']:
            total = db.query(EventSignpostLink).filter(EventSignpostLink.tier == tier).count()
            provisional = db.query(EventSignpostLink).filter(
                EventSignpostLink.tier == tier,
                EventSignpostLink.provisional == True
            ).count()
            non_provisional = total - provisional
            print(f"   {tier}-tier: {total} total ({non_provisional} non-provisional, {provisional} provisional)")
        
        # Sample A-tier event
        print("\n📄 Sample A-tier event:")
        a_event = db.query(Event).filter(Event.evidence_tier == 'A').first()
        if a_event:
            print(f"   Title: {a_event.title[:70]}...")
            print(f"   Source: {a_event.source_url}")
            print(f"   Publisher: {a_event.publisher}")
            print(f"   Provisional: {a_event.provisional}")
            print(f"   Dedup hash: {a_event.dedup_hash[:16] if a_event.dedup_hash else 'None'}...")
            
            # Show links
            links = db.query(EventSignpostLink).filter(EventSignpostLink.event_id == a_event.id).all()
            if links:
                print(f"   Links: {len(links)} signposts")
                for link in links[:2]:
                    print(f"      - Signpost #{link.signpost_id}: conf={link.confidence:.2f}, tier={link.tier}, provisional={link.provisional}")
        
        # Sample B-tier event
        print("\n📄 Sample B-tier event:")
        b_event = db.query(Event).filter(Event.evidence_tier == 'B').first()
        if b_event:
            print(f"   Title: {b_event.title[:70]}...")
            print(f"   Source: {b_event.source_url}")
            print(f"   Publisher: {b_event.publisher}")
            print(f"   Provisional: {b_event.provisional}")
            
            # Show links
            links = db.query(EventSignpostLink).filter(EventSignpostLink.event_id == b_event.id).all()
            if links:
                print(f"   Links: {len(links)} signposts")
                for link in links[:2]:
                    print(f"      - Signpost #{link.signpost_id}: conf={link.confidence:.2f}, tier={link.tier}, provisional={link.provisional}")
        
        # Ingest runs
        print("\n📊 Recent ingest runs:")
        runs = db.query(IngestRun).order_by(IngestRun.started_at.desc()).limit(5).all()
        for run in runs:
            status_emoji = "✅" if run.status == "success" else "❌"
            print(f"   {status_emoji} {run.connector_name}: {run.new_events_count} events ({run.status})")
        
        # Guardrails check
        print("\n🛡️  Guardrails verification:")
        
        # Check 1: C/D tier should all be provisional
        cd_non_provisional = db.query(EventSignpostLink).filter(
            EventSignpostLink.tier.in_(['C', 'D']),
            EventSignpostLink.provisional == False
        ).count()
        if cd_non_provisional > 0:
            print(f"   ❌ VIOLATION: {cd_non_provisional} C/D-tier links are non-provisional (should all be provisional)")
        else:
            print(f"   ✅ C/D-tier links are all provisional (NEVER move gauges)")
        
        # Check 2: A-tier should all be non-provisional
        a_provisional = db.query(EventSignpostLink).filter(
            EventSignpostLink.tier == 'A',
            EventSignpostLink.provisional == True
        ).count()
        if a_provisional > 0:
            print(f"   ⚠️  {a_provisional} A-tier links are still provisional (expected non-provisional)")
        else:
            print(f"   ✅ A-tier links are all non-provisional (can move gauges)")
        
        # Check 3: Events have dedup_hash
        events_without_dedup = db.query(Event).filter(Event.dedup_hash == None).count()
        total_events = db.query(Event).count()
        if events_without_dedup > 0:
            print(f"   ⚠️  {events_without_dedup}/{total_events} events missing dedup_hash")
        else:
            print(f"   ✅ All {total_events} events have dedup_hash")
        
        # Check 4: Links have tier field
        links_without_tier = db.query(EventSignpostLink).filter(EventSignpostLink.tier == None).count()
        total_links = db.query(EventSignpostLink).count()
        if links_without_tier > 0:
            print(f"   ❌ VIOLATION: {links_without_tier}/{total_links} links missing tier field")
        else:
            print(f"   ✅ All {total_links} links have tier field")
        
    finally:
        db.close()


def main():
    """Run full pipeline test."""
    print("\n" + "="*70)
    print("  AGI Tracker: News Ingestion Pipeline Test")
    print("  Phases A/B/C: Ingestors + Mapping + Corroboration")
    print("="*70)
    
    try:
        # Run pipeline
        ingest_stats = test_ingestion()
        mapping_stats = test_mapping()
        corr_stats = test_corroboration()
        
        # Verify state
        verify_database_state()
        
        # Final summary
        print_section("Pipeline Test Complete")
        print("✅ All phases completed successfully!")
        print("\nNext steps:")
        print("  - Review events in database")
        print("  - Check event→signpost links")
        print("  - Verify provisional status is correct")
        print("  - Run frontend to visualize results")
        
    except Exception as e:
        print(f"\n❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

