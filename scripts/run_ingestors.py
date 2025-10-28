#!/usr/bin/env python3
"""
Quick script to run all ingestors manually.
This will use fixtures (no live scraping).
"""
import sys
from pathlib import Path

# Add services/etl to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

print("🚀 Running News Ingestors...\n")
print("=" * 70)

try:
    # Import tasks
    from app.tasks.news.ingest_arxiv import ingest_arxiv_task
    from app.tasks.news.ingest_company_blogs import ingest_company_blogs_task
    from app.tasks.news.ingest_press_reuters_ap import ingest_press_reuters_ap_task
    from app.tasks.news.map_events_to_signposts import map_events_to_signposts_task
    
    # Run arXiv ingestor
    print("\n📚 STEP 1/4: Running arXiv ingestor (A-tier)...")
    print("-" * 70)
    arxiv_result = ingest_arxiv_task()
    print(f"✅ arXiv complete: {arxiv_result}")
    
    # Run company blogs ingestor
    print("\n📰 STEP 2/4: Running company blogs ingestor (B-tier)...")
    print("-" * 70)
    blogs_result = ingest_company_blogs_task()
    print(f"✅ Blogs complete: {blogs_result}")
    
    # Run press ingestor
    print("\n📰 STEP 3/4: Running press ingestor (C-tier)...")
    print("-" * 70)
    press_result = ingest_press_reuters_ap_task()
    print(f"✅ Press complete: {press_result}")
    
    # Run mapper
    print("\n🔗 STEP 4/4: Mapping events to signposts...")
    print("-" * 70)
    mapper_result = map_events_to_signposts_task()
    print(f"✅ Mapper complete: {mapper_result}")
    
    # Summary
    print("\n" + "=" * 70)
    print("🎉 ALL INGESTORS COMPLETE!")
    print("=" * 70)
    print(f"\nResults Summary:")
    print(f"  arXiv:  {arxiv_result}")
    print(f"  Blogs:  {blogs_result}")
    print(f"  Press:  {press_result}")
    print(f"  Mapper: {mapper_result}")
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print("\nMake sure you have DATABASE_URL set:")
    print("  export DATABASE_URL='postgresql://...'")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error running ingestors: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

