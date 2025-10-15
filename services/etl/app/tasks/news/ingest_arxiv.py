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

from app.database import SessionLocal
from app.models import Event
from app.config import settings


ARXIV_CATEGORIES = {"cs.AI", "cs.CL", "cs.LG", "cs.CV"}


def load_fixture_data() -> List[Dict]:
    """Load arXiv fixture data for CI/testing."""
    fixture_path = Path(__file__).parent.parent.parent.parent / "fixtures" / "news" / "arxiv.json"
    
    if not fixture_path.exists():
        return []
    
    with open(fixture_path) as f:
        return json.load(f)


def fetch_live_arxiv() -> List[Dict]:
    """
    Fetch live arXiv papers (placeholder for production).
    
    In production, this would:
    - Query arXiv API for recent papers in target categories
    - Parse XML/JSON responses
    - Extract title, abstract, authors, date, categories
    
    For now, returns empty to encourage fixture usage in CI.
    """
    # TODO: Implement arXiv API fetching for production
    return []


def normalize_event_data(raw_data: Dict) -> Dict:
    """Normalize raw arXiv data to event schema."""
    # Parse published_at if string
    published_at = raw_data.get("published_at")
    if isinstance(published_at, str):
        try:
            published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        except ValueError:
            published_at = None
    
    # Use first author as publisher if available
    authors = raw_data.get("authors", [])
    publisher = authors[0] if authors else "arXiv"
    
    return {
        "title": raw_data["title"],
        "summary": raw_data.get("summary", ""),
        "source_url": raw_data["url"],
        "publisher": publisher,
        "published_at": published_at,
        "evidence_tier": "A",  # arXiv papers are A-tier (peer-reviewed/archived)
        "provisional": False,  # A-tier is NOT provisional - moves gauges directly
        "parsed": {
            "authors": raw_data.get("authors", []),
            "categories": raw_data.get("categories", [])
        },
        "needs_review": False  # Will be set by mapper based on confidence
    }


def create_or_update_event(db, event_data: Dict) -> Event:
    """Idempotently create or update an event using URL."""
    existing = db.query(Event).filter(Event.source_url == event_data["source_url"]).first()
    
    if existing:
        for key, value in event_data.items():
            if value is not None:
                setattr(existing, key, value)
        return existing
    else:
        new_event = Event(**event_data)
        db.add(new_event)
        db.flush()
        return new_event


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
    
    try:
        use_live = settings.scrape_real
        
        if use_live:
            print("🔴 Live mode: Fetching from arXiv API (not yet implemented, using fixtures)")
            raw_data = load_fixture_data()
        else:
            print("🟢 Fixture mode: Loading arXiv fixtures")
            raw_data = load_fixture_data()
        
        print(f"📄 Processing {len(raw_data)} arXiv papers...")
        
        for item in raw_data:
            try:
                # Normalize to event schema
                event_data = normalize_event_data(item)
                
                # Create or update event
                event = create_or_update_event(db, event_data)
                
                if event.id and event.ingested_at.date() == datetime.now(timezone.utc).date():
                    stats["inserted"] += 1
                    print(f"  ✓ Inserted: {event.title[:60]}...")
                else:
                    stats["updated"] += 1
                    print(f"  ↻ Updated: {event.title[:60]}...")
                
            except Exception as e:
                stats["errors"] += 1
                print(f"  ❌ Error processing item: {e}")
                continue
        
        db.commit()
        
        print(f"\n✅ arXiv ingestion complete!")
        print(f"   Inserted: {stats['inserted']}, Updated: {stats['updated']}, Skipped: {stats['skipped']}, Errors: {stats['errors']}")
        
        return stats
    
    except Exception as e:
        db.rollback()
        print(f"❌ Fatal error in arXiv ingestion: {e}")
        raise
    
    finally:
        db.close()

