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
import os
import random

from celery import shared_task
import feedparser

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


def generate_synthetic_blog_events(total: int) -> List[Dict]:
    """Generate synthetic company blog events with clear signpost cues and numeric values."""
    if total <= 0:
        return []
    items: List[Dict] = []
    publishers = [
        ("OpenAI", "https://openai.com/blog/"),
        ("Anthropic", "https://www.anthropic.com/news/"),
        ("Google DeepMind", "https://deepmind.google/discover/blog/"),
        ("Meta AI", "https://ai.meta.com/blog/"),
        ("xAI", "https://x.ai/blog/"),
        ("Cohere", "https://cohere.com/blog/"),
        ("Mistral", "https://mistral.ai/news/")
    ]
    # Templates ensure keyword + numeric presence to yield conf >= 0.7
    templates = [
        ("SWE-bench Verified", "swe-bench verified", "%", [85, 86, 87, 88, 89, 90]),
        ("OSWorld", "osworld", "%", [50, 55, 60, 65, 70]),
        ("WebArena", "webarena", "%", [60, 65, 70, 75, 80]),
        ("GPQA Diamond", "gpqa diamond", "%", [70, 72, 74, 76, 78]),
        ("Compute", "10^", "flops", [26, 27]),
        ("Datacenter Power", "gw", "gw", [1, 3, 5, 10]),
    ]
    now = datetime.now(timezone.utc)
    for i in range(total):
        pub, base = random.choice(publishers)
        kind = random.choice(templates)
        if kind[0] in ("Compute", "Datacenter Power"):
            # Compute/Power style
            val = random.choice(kind[3])
            if kind[0] == "Compute":
                title = f"{pub} training run exceeds 10^{val} FLOPs"
                summary = f"Official blog: Training reached 10^{val} FLOPs on latest run."
            else:
                title = f"{pub} announces {val} GW datacenter capacity"
                summary = f"Planned AI datacenter will provide {val} GW of power."
        else:
            # Percentage style
            val = random.choice(kind[3])
            title = f"{pub} reports {val}% on {kind[0]}"
            summary = f"Latest model achieves {val}% on {kind[1].title()} benchmark."
        # Spread dates over last 300 days
        published_at = now - timedelta(days=random.randint(1, 300))
        items.append({
            "title": title,
            "summary": summary,
            "url": f"{base}{hashlib.sha1(title.encode()).hexdigest()[:10]}",
            "publisher": pub,
            "published_at": published_at.isoformat().replace('+00:00', 'Z'),
        })
    return items


def fetch_live_company_blogs(max_results: int = 150) -> List[Dict]:
    """Fetch live company blog/news posts via RSS/Atom where available (robots-aware)."""
    feeds = [
        # OpenAI
        "https://openai.com/blog/rss.xml",
        # Anthropic (news)
        "https://www.anthropic.com/news/rss.xml",
        # Google DeepMind blog feed
        "https://deepmind.google/discover/feeds/blog.xml",
        # Meta AI blog (WordPress-style)
        "https://ai.meta.com/blog/feed/",
        # xAI (may not expose RSS; leave for future)
        # Cohere
        "https://cohere.com/blog/rss.xml",
        # Mistral (WordPress)
        "https://mistral.ai/feed/",
    ]
    items: List[Dict] = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_results]:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()
                link = entry.get("link")
                published = entry.get("published") or entry.get("updated")
                items.append(
                    {
                        "title": title,
                        "summary": summary,
                        "url": link,
                        # Publisher inferred from host
                        "publisher": None,
                        "published_at": published,
                    }
                )
        except Exception:
            continue
    return items


def normalize_event_data(raw_data: Dict) -> Dict:
    """Normalize raw blog data to event schema."""
    # Parse published_at if string
    published_at = raw_data.get("published_at")
    if isinstance(published_at, str):
        try:
            published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        except ValueError:
            published_at = None
    
    # Source domain
    source_url = raw_data["url"]
    source_domain = None
    if "://" in source_url:
        try:
            source_domain = source_url.split('://', 1)[1].split('/')[0]
        except Exception:
            source_domain = None
    return {
        "title": raw_data["title"],
        "summary": raw_data.get("summary", ""),
        "source_url": source_url,
        "source_domain": source_domain,
        "source_type": "blog",
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
            print("🔵 Live mode: Fetching company blogs via RSS/Atom feeds")
            raw_data = fetch_live_company_blogs()
            if not raw_data:
                print("  ⚠️  Live blog feeds returned 0 items; falling back to fixtures")
                raw_data = load_fixture_data()
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

