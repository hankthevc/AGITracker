#!/usr/bin/env python3
"""
Test live data ingestion from real sources.

Usage:
    python scripts/test_ingestion_live.py --source arxiv
    python scripts/test_ingestion_live.py --source blogs
    python scripts/test_ingestion_live.py --source all
"""
import argparse
import sys
from pathlib import Path

# Add services/etl to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from app.database import SessionLocal
from app.tasks.news.ingest_arxiv import fetch_live_arxiv, normalize_event_data as normalize_arxiv
from app.tasks.news.ingest_company_blogs import fetch_live_company_blogs, normalize_event_data as normalize_blog


def test_arxiv_live():
    """Test arXiv live fetching."""
    print("\n" + "="*60)
    print("🔍 TESTING ARXIV LIVE INGESTION")
    print("="*60)
    
    try:
        print("\n📡 Fetching arXiv papers via Atom API...")
        papers = fetch_live_arxiv(max_results=10)
        
        print(f"\n✅ Fetched {len(papers)} papers")
        
        if papers:
            print("\n📄 Sample papers:")
            for i, paper in enumerate(papers[:3], 1):
                print(f"\n  {i}. {paper['title'][:80]}...")
                print(f"     Authors: {', '.join(paper['authors'][:3])}")
                print(f"     Link: {paper['link']}")
                print(f"     Published: {paper['published']}")
                
                # Test normalization
                try:
                    normalized = normalize_arxiv(paper)
                    print(f"     ✓ Normalized: tier={normalized['evidence_tier']}, domain={normalized['source_domain']}")
                except Exception as e:
                    print(f"     ❌ Normalization failed: {e}")
        
        return len(papers)
    
    except Exception as e:
        print(f"\n❌ arXiv test failed: {e}")
        import traceback
        traceback.print_exc()
        return 0


def test_company_blogs_live():
    """Test company blog live fetching."""
    print("\n" + "="*60)
    print("🔍 TESTING COMPANY BLOGS LIVE INGESTION")
    print("="*60)
    
    try:
        print("\n📡 Fetching company blogs via RSS/Atom feeds...")
        print("   (This may take ~45 seconds due to rate limiting)")
        posts = fetch_live_company_blogs(max_results=10)
        
        print(f"\n✅ Fetched {len(posts)} blog posts")
        
        if posts:
            print("\n📰 Sample posts:")
            for i, post in enumerate(posts[:5], 1):
                print(f"\n  {i}. {post['title'][:80]}...")
                print(f"     Publisher: {post.get('publisher', 'Unknown')}")
                print(f"     URL: {post['url'][:60]}...")
                print(f"     Published: {post.get('published_at', 'N/A')}")
                
                # Test normalization
                try:
                    normalized = normalize_blog(post)
                    print(f"     ✓ Normalized: tier={normalized['evidence_tier']}, provisional={normalized['provisional']}")
                except Exception as e:
                    print(f"     ❌ Normalization failed: {e}")
        
        return len(posts)
    
    except Exception as e:
        print(f"\n❌ Company blogs test failed: {e}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    parser = argparse.ArgumentParser(description="Test live data ingestion")
    parser.add_argument(
        "--source",
        choices=["arxiv", "blogs", "all"],
        default="all",
        help="Which source to test"
    )
    args = parser.parse_args()
    
    total_items = 0
    
    if args.source in ["arxiv", "all"]:
        arxiv_count = test_arxiv_live()
        total_items += arxiv_count
    
    if args.source in ["blogs", "all"]:
        blogs_count = test_company_blogs_live()
        total_items += blogs_count
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Total items fetched: {total_items}")
    
    if total_items > 0:
        print("\n✅ Live ingestion is working!")
        print("\nNext steps:")
        print("  1. Run full ingestion: cd services/etl && celery -A app.celery_app call ingest_arxiv")
        print("  2. Verify in database: psql -c 'SELECT COUNT(*) FROM events WHERE source_type IN (\"paper\", \"blog\")'")
        print("  3. Check for duplicates: python scripts/verify_dedup.py")
    else:
        print("\n⚠️  No items fetched. Check:")
        print("  - Network connectivity")
        print("  - Feed URLs are still valid")
        print("  - Rate limiting not blocking requests")
    
    return 0 if total_items > 0 else 1


if __name__ == "__main__":
    sys.exit(main())

