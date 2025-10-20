"""
arXiv paper ingestion task (A-tier evidence).

Priority: 2 (after company blogs)
Sources: cs.AI, cs.CL, cs.LG, cs.CV categories
Evidence tier: A (peer-reviewed/archived papers)
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
import hashlib

from celery import shared_task
import feedparser

from app.database import SessionLocal
from app.models import Event, IngestRun
from app.config import settings
from app.utils.fetcher import compute_content_hash, canonicalize_url, normalize_title
import os


ARXIV_CATEGORIES = {"cs.AI", "cs.CL", "cs.LG", "cs.CV"}


def load_fixture_data() -> List[Dict]:
    """Load arXiv fixture data for CI/testing."""
    # Fixture path: repo_root/infra/fixtures/arxiv/cs_ai_sample.json
    fixture_path = Path(__file__).parent.parent.parent.parent.parent.parent / "infra" / "fixtures" / "arxiv" / "cs_ai_sample.json"
    
    if not fixture_path.exists():
        print(f"⚠️  Fixture not found: {fixture_path}")
        return []
    
    with open(fixture_path) as f:
        return json.load(f)


def fetch_live_arxiv(max_results: int = 50) -> List[Dict]:
    """Fetch recent arXiv entries for target categories via Atom feed (robots-friendly)."""
    base = (
        "http://export.arxiv.org/api/query?"
        "search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG+OR+cat:cs.CV"
        "&sortBy=submittedDate&sortOrder=descending"
        f"&max_results={max_results}"
    )
    feed = feedparser.parse(base)
    items: List[Dict] = []
    for entry in feed.entries:
        title = entry.get("title", "").strip()
        summary = entry.get("summary", "").strip()
        link = entry.get("link")
        published = entry.get("published") or entry.get("updated")
        authors = [a.get("name") for a in entry.get("authors", [])] if entry.get("authors") else []
        categories = [t.get("term") for t in entry.get("tags", [])] if entry.get("tags") else []
        items.append(
            {
                "title": title,
                "summary": summary,
                "link": link,
                "authors": authors,
                "published": published,
                "categories": categories,
            }
        )
    return items


def normalize_event_data(raw_data: Dict) -> Dict:
    """Normalize raw arXiv data to event schema."""
    # Parse published_at if string
    published_at = raw_data.get("published", raw_data.get("published_at"))
    if isinstance(published_at, str):
        try:
            published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        except ValueError:
            published_at = None
    
    # Use first author as publisher if available
    authors = raw_data.get("authors", [])
    publisher = authors[0] if authors else "arXiv"
    
    # Extract domain from URL
    source_url = raw_data.get("link", raw_data.get("url"))
    source_domain = "arxiv.org"
    
    # Compute content hash for deduplication
    content_hash = compute_content_hash(source_url, raw_data["title"])
    
    return {
        "title": raw_data["title"],
        "summary": raw_data.get("summary", ""),
        "source_url": source_url,
        "source_domain": source_domain,
        "source_type": "paper",  # v0.3 schema
        "publisher": publisher,
        "published_at": published_at,
        "evidence_tier": "A",  # arXiv papers are A-tier (peer-reviewed/archived)
        "provisional": False,  # A-tier is NOT provisional - moves gauges directly
        "content_hash": content_hash,  # Phase 0: deduplication
        "parsed": {
            "authors": raw_data.get("authors", []),
            "categories": raw_data.get("categories", [])
        },
        "needs_review": False  # Will be set by mapper based on confidence
    }


def create_or_update_event(db, event_data: Dict) -> tuple[Event, bool]:
    """
    Idempotently create or update an event using URL or content_hash.
    
    Args:
        db: Database session
        event_data: Normalized event data dict
        
    Returns:
        Tuple of (event, is_new) where is_new is True if event was just created
    """
    content_hash = event_data.get("content_hash")
    source_url = event_data["source_url"]
    
    # Check for duplicates by content_hash or URL
    existing = None
    if content_hash:
        existing = db.query(Event).filter(Event.content_hash == content_hash).first()
    
    if not existing:
        existing = db.query(Event).filter(Event.source_url == source_url).first()
    
    if existing:
        # Update existing event (e.g., if summary/title changed)
        for key, value in event_data.items():
            if value is not None:
                setattr(existing, key, value)
        return existing, False
    else:
        new_event = Event(**event_data)
        db.add(new_event)
        db.flush()
        return new_event, True


@shared_task(name="ingest_arxiv")
def ingest_arxiv_task():
    """
    Ingest arXiv papers (A-tier evidence).
    
    Priority: 2
    Evidence tier: A (peer-reviewed, NOT provisional)
    
    Returns:
        dict: Statistics about ingestion
    """
    db = SessionLocal()
    stats = {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    
    # Create ingest run record
    run = IngestRun(
        connector_name="ingest_arxiv",
        started_at=datetime.now(timezone.utc),
        status="running"
    )
    db.add(run)
    db.commit()
    
    try:
        use_live = settings.scrape_real
        
        if use_live:
            print("🔵 Live mode: Fetching recent arXiv entries via Atom API")
            raw_data = fetch_live_arxiv()
        else:
            print("🟢 Fixture mode: Loading arXiv fixtures")
            raw_data = load_fixture_data()
            # No synthetic for arXiv to keep A-tier tight
        
        print(f"📄 Processing {len(raw_data)} arXiv papers...")
        
        for item in raw_data:
            try:
                # Normalize to event schema
                event_data = normalize_event_data(item)
                
                # Create or update event (with deduplication)
                event, is_new = create_or_update_event(db, event_data)
                
                if is_new:
                    stats["inserted"] += 1
                    print(f"  ✓ Inserted: {event.title[:60]}...")
                else:
                    stats["skipped"] += 1
                    print(f"  ⊘ Skipped (duplicate): {event.title[:60]}...")
                
            except Exception as e:
                stats["errors"] += 1
                print(f"  ❌ Error processing item: {e}")
                continue
        
        db.commit()
        
        # Update ingest run
        run.finished_at = datetime.now(timezone.utc)
        run.status = "success"
        run.new_events_count = stats["inserted"]
        run.new_links_count = 0  # Mapper will update this
        db.commit()
        
        print(f"\n✅ arXiv ingestion complete!")
        print(f"   Inserted: {stats['inserted']}, Updated: {stats['updated']}, Skipped: {stats['skipped']}, Errors: {stats['errors']}")
        
        return stats
    
    except Exception as e:
        db.rollback()
        run.finished_at = datetime.now(timezone.utc)
        run.status = "fail"
        run.error = str(e)
        db.commit()
        print(f"❌ Fatal error in arXiv ingestion: {e}")
        raise
    
    finally:
        db.close()

