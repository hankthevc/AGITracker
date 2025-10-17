"""
Company blog ingestion task (B-tier evidence).

Priority: 1 (highest - runs first)
Sources: OpenAI, Anthropic, Google DeepMind, Meta AI, xAI, Cohere, Mistral (allowlist)
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
import hashlib

from celery import shared_task

from app.database import SessionLocal
from app.models import Event, IngestRun
from app.config import settings


ALLOWED_PUBLISHERS = {
    "OpenAI",
    "Anthropic", 
    "Google DeepMind",
    "Meta AI",
    "xAI",
    "Cohere",
    "Mistral"
}


def load_fixture_data() -> List[Dict]:
    """Load company blog fixture data for CI/testing."""
    fixture_path = Path(__file__).parent.parent.parent.parent / "fixtures" / "news" / "company_blogs.json"
    
    if not fixture_path.exists():
        return []
    
    with open(fixture_path) as f:
        return json.load(f)


def fetch_live_company_blogs() -> List[Dict]:
    """
    Fetch live company blog posts (placeholder for production).
    
    In production, this would:
    - Use RSS feeds or APIs for each company
    - Parse HTML/JSON responses
    - Extract title, summary, date, URL
    
    For now, returns empty to encourage fixture usage in CI.
    """
    # TODO: Implement RSS/API fetching for production
    # For now, encourage fixture mode
    return []


def normalize_event_data(raw_data: Dict) -> Dict:
    """Normalize raw blog data to event schema."""
    # Parse published_at if string
    published_at = raw_data.get("published_at")
    if isinstance(published_at, str):
        try:
            published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        except ValueError:
            published_at = None
    
    return {
        "title": raw_data["title"],
        "summary": raw_data.get("summary", ""),
        "source_url": raw_data["url"],
        "publisher": raw_data.get("publisher", "Unknown"),
        "published_at": published_at,
        "evidence_tier": "B",  # Company blogs are B-tier (official lab sources)
        "provisional": True,  # B-tier is provisional per policy
        "parsed": {},  # Will be populated by mapper
        "needs_review": False  # Will be set by mapper based on confidence
    }


def create_or_update_event(db, event_data: Dict) -> Event:
    """
    Idempotently create or update an event.
    
    Uses URL hash for idempotency.
    """
    url_hash = hashlib.sha256(event_data["source_url"].encode()).hexdigest()
    
    # Check if event exists
    existing = db.query(Event).filter(Event.source_url == event_data["source_url"]).first()
    
    if existing:
        # Update existing event
        for key, value in event_data.items():
            if value is not None:  # Only update non-null values
                setattr(existing, key, value)
        return existing
    else:
        # Create new event
        new_event = Event(**event_data)
        db.add(new_event)
        db.flush()
        return new_event


@shared_task(name="ingest_company_blogs")
def ingest_company_blogs_task():
    """
    Ingest company blog posts (B-tier evidence).
    
    Priority: 1 (highest)
    Evidence tier: B (official lab sources, provisional)
    
    Returns:
        dict: Statistics about ingestion
    """
    db = SessionLocal()
    stats = {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    
    # Create ingest run record
    run = IngestRun(
        connector_name="ingest_company_blogs",
        started_at=datetime.now(timezone.utc),
        status="running",
    )
    db.add(run)
    db.commit()
    
    try:
        # Determine if we should use live or fixture data
        use_live = settings.scrape_real
        
        if use_live:
            print("🔴 Live mode: Fetching from company blogs (not yet implemented, using fixtures)")
            raw_data = load_fixture_data()  # Fallback to fixtures for now
        else:
            print("🟢 Fixture mode: Loading company blog fixtures")
            raw_data = load_fixture_data()
        
        print(f"📰 Processing {len(raw_data)} company blog posts...")
        
        for item in raw_data:
            try:
                # Validate publisher is in allowlist
                if item.get("publisher") not in ALLOWED_PUBLISHERS:
                    print(f"  ⚠️  Skipping non-allowlisted publisher: {item.get('publisher')}")
                    stats["skipped"] += 1
                    continue
                
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
        
        # Update ingest run
        run.finished_at = datetime.now(timezone.utc)
        run.status = "success"
        run.new_events_count = stats["inserted"]
        run.new_links_count = 0  # mapper updates later
        db.commit()
        
        print(f"\n✅ Company blogs ingestion complete!")
        print(f"   Inserted: {stats['inserted']}, Updated: {stats['updated']}, Skipped: {stats['skipped']}, Errors: {stats['errors']}")
        
        return stats
    
    except Exception as e:
        db.rollback()
        # Update ingest run on failure
        run.finished_at = datetime.now(timezone.utc)
        run.status = "fail"
        run.error = str(e)
        db.commit()
        print(f"❌ Fatal error in company blogs ingestion: {e}")
        raise
    
    finally:
        db.close()

