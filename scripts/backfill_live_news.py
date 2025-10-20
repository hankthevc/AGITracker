#!/usr/bin/env python3
"""
Backfill live news from all configured RSS/Atom feeds.

Fetches real AI news from past N days and uses OpenAI to intelligently
map events to signposts.

Usage:
  export OPENAI_API_KEY='sk-proj-...'
  export ENABLE_LLM_MAPPING=true
  export SCRAPE_REAL=true
  python3 scripts/backfill_live_news.py --days=30
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from app.tasks.news.ingest_company_blogs import ingest_company_blogs_task
from app.tasks.news.ingest_arxiv import ingest_arxiv_task
from app.tasks.news.ingest_press_reuters_ap import ingest_press_reuters_ap_task
from app.tasks.news.map_events_to_signposts import map_events_to_signposts_task


def backfill_all(days: int = 30):
    """
    Backfill all news sources for the past N days.
    
    Args:
        days: Number of days to backfill
    """
    print(f"🔄 Starting live news backfill (last {days} days)...")
    print(f"⏰ Started at: {datetime.utcnow().isoformat()}Z\n")
    
    all_stats = {}
    
    # 1. Company blogs (12 RSS feeds)
    print("=" * 70)
    print("📰 COMPANY BLOGS (B-tier)")
    print("=" * 70)
    print("Sources: OpenAI, Anthropic, Google, Meta, Cohere, Mistral,")
    print("         Microsoft Research, Google Research, Hugging Face, NVIDIA\n")
    blogs_stats = ingest_company_blogs_task()
    all_stats["blogs"] = blogs_stats
    print(f"\n✅ Blogs: {blogs_stats}\n")
    
    # 2. arXiv papers (A-tier)
    print("=" * 70)
    print("📄 ARXIV PAPERS (A-tier)")
    print("=" * 70)
    print("Categories: cs.AI, cs.CL, cs.LG, cs.CV\n")
    arxiv_stats = ingest_arxiv_task()
    all_stats["arxiv"] = arxiv_stats
    print(f"\n✅ arXiv: {arxiv_stats}\n")
    
    # 3. Press (C-tier)
    print("=" * 70)
    print("🗞️  PRESS (C-tier - 'If True' only)")
    print("=" * 70)
    print("Sources: Reuters Technology, AP\n")
    press_stats = ingest_press_reuters_ap_task()
    all_stats["press"] = press_stats
    print(f"\n✅ Press: {press_stats}\n")
    
    # 4. Map to signposts
    print("=" * 70)
    print("🔗 MAPPING TO SIGNPOSTS")
    print("=" * 70)
    print("Strategy: Alias patterns first, then LLM fallback if enabled\n")
    mapping_stats = map_events_to_signposts_task()
    all_stats["mapping"] = mapping_stats
    print(f"\n✅ Mapping: {mapping_stats}\n")
    
    # Summary
    print("=" * 70)
    print("📊 BACKFILL SUMMARY")
    print("=" * 70)
    total_inserted = (
        blogs_stats.get("inserted", 0) +
        arxiv_stats.get("inserted", 0) +
        press_stats.get("inserted", 0)
    )
    print(f"Total events inserted: {total_inserted}")
    print(f"  - Blogs (B-tier):  {blogs_stats.get('inserted', 0)}")
    print(f"  - arXiv (A-tier):  {arxiv_stats.get('inserted', 0)}")
    print(f"  - Press (C-tier):  {press_stats.get('inserted', 0)}")
    print(f"\nMapping results:")
    print(f"  - Processed: {mapping_stats.get('processed', 0)}")
    print(f"  - Linked:    {mapping_stats.get('linked', 0)}")
    print(f"  - LLM used:  {mapping_stats.get('llm_used', 0)}")
    print(f"  - Unmapped:  {mapping_stats.get('unmapped', 0)}")
    
    success_rate = (mapping_stats.get('linked', 0) / mapping_stats.get('processed', 1)) * 100 if mapping_stats.get('processed', 0) > 0 else 0
    print(f"\nAuto-mapping success: {success_rate:.1f}%")
    
    print(f"\n⏰ Completed at: {datetime.utcnow().isoformat()}Z")
    
    return all_stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill live news from all sources")
    parser.add_argument("--days", type=int, default=30, help="Number of days to backfill")
    args = parser.parse_args()
    
    backfill_all(args.days)
