"""
Press ingestion task for Reuters/AP (C-tier evidence).

Priority: 4 (lowest - after B, A, D)
Sources: Reuters, Associated Press (allowlist)
Evidence tier: C (reputable press, but NOT allowed to move gauges)
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from celery import shared_task

from app.database import SessionLocal
from app.models import Event, IngestRun
from app.config import settings
import os
from datetime import timedelta


ALLOWED_PRESS = {"Reuters", "Associated Press", "AP"}


def load_fixture_data() -> List[Dict]:
    """Load press fixture data for CI/testing."""
    fixture_path = Path(__file__).parent.parent.parent.parent / "fixtures" / "news" / "press.json"
    
    if not fixture_path.exists():
        return []
    
    with open(fixture_path) as f:
        return json.load(f)


def generate_synthetic_press(total: int) -> List[Dict]:
    if total <= 0:
        return []
    items: List[Dict] = []
    now = datetime.now(timezone.utc)
    for i in range(total):
        pct = 60 + (i % 30)
        title = f"Reuters: New model reaches {pct}% on WebArena"
        summary = f"Reuters reports {pct}% on WebArena benchmark."
        items.append({
            "title": title,
            "summary": summary,
            "url": f"https://reuters.com/tech/{pct}",
            "publisher": "Reuters",
            "published_at": (now - timedelta(days=i+5)).isoformat().replace('+00:00', 'Z')
        })
    return items


def fetch_live_press() -> List[Dict]:
    """Fetch live press articles (placeholder)."""
    # TODO: Implement Reuters/AP API/RSS fetching
    return []


def normalize_event_data(raw_data: Dict) -> Dict:
    """Normalize press data to event schema."""
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
        "publisher": raw_data.get("publisher", "Press"),
        "published_at": published_at,
        "evidence_tier": "C",  # Press is C-tier
        "provisional": True,  # C-tier NEVER moves gauges per policy
        "parsed": {},
        "needs_review": True  # C-tier always needs review for "if true" analysis
    }


def create_or_update_event(db, event_data: Dict) -> Event:
    """Idempotently create or update event."""
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


@shared_task(name="ingest_press_reuters_ap")
def ingest_press_reuters_ap_task():
    """
    Ingest Reuters/AP press articles (C-tier evidence).
    
    Priority: 4 (lowest)
    Evidence tier: C (displayed as unverified, NEVER moves gauges)
    
    Policy: C-tier shown as "if true" only, requires review
    """
    db = SessionLocal()
    stats = {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    
    # Create ingest run record
    run = IngestRun(
        connector_name="ingest_press_reuters_ap",
        started_at=datetime.now(timezone.utc),
        status="running",
    )
    db.add(run)
    db.commit()
    
    try:
        use_live = settings.scrape_real
        
        if use_live:
            print("🔴 Live mode: Fetching press (not implemented, using fixtures)")
            raw_data = load_fixture_data()
        else:
            print("🟢 Fixture mode: Loading press fixtures")
            raw_data = load_fixture_data()
            synth_total = int(os.getenv("PRESS_SYNTHETIC_COUNT", os.getenv("NEWS_SYNTHETIC_COUNT", "0")))
            if synth_total > 0:
                raw_data.extend(generate_synthetic_press(synth_total))
        
        print(f"📰 Processing {len(raw_data)} press articles (C-tier, for 'if true' analysis only)...")
        
        for item in raw_data:
            try:
                # Validate publisher
                if item.get("publisher") not in ALLOWED_PRESS:
                    stats["skipped"] += 1
                    continue
                
                event_data = normalize_event_data(item)
                event = create_or_update_event(db, event_data)
                
                if event.id and event.ingested_at.date() == datetime.now(timezone.utc).date():
                    stats["inserted"] += 1
                    print(f"  ✓ Inserted (C-tier): {event.title[:60]}...")
                else:
                    stats["updated"] += 1
                
            except Exception as e:
                stats["errors"] += 1
                continue
        
        db.commit()
        
        # Update ingest run
        run.finished_at = datetime.now(timezone.utc)
        run.status = "success"
        run.new_events_count = stats["inserted"]
        run.new_links_count = 0
        db.commit()
        
        print(f"\n✅ Press ingestion complete (C-tier: displayed but NEVER moves gauges)")
        print(f"   Inserted: {stats['inserted']}, Updated: {stats['updated']}")
        
        return stats
    
    except Exception as e:
        db.rollback()
        # Update ingest run on failure
        run.finished_at = datetime.now(timezone.utc)
        run.status = "fail"
        run.error = str(e)
        db.commit()
        print(f"❌ Fatal error: {e}")
        raise
    finally:
        db.close()

