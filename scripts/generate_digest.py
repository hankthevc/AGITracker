#!/usr/bin/env python3
"""
Generate weekly digest (JSON + HTML) for public consumption (CC BY 4.0).

Pulls A/B events from last 7 days + top C/D "if true" items.
Outputs to public/digests/YYYY-WW.json and YYYY-WW.html.
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from sqlalchemy import and_
from app.database import SessionLocal
from app.models import Event, EventSignpostLink, Signpost


def generate_digest():
    """Generate weekly digest for the current week."""
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=now.weekday())).date()
    week_num = week_start.isocalendar()[1]
    year = week_start.year
    
    # Get events from last 7 days
    seven_days_ago = now - timedelta(days=7)
    
    try:
        # A/B tier events (moves gauges)
        ab_events = db.query(Event).filter(
            and_(
                Event.evidence_tier.in_(["A", "B"]),
                Event.published_at >= seven_days_ago,
                Event.retracted == False,
            )
        ).order_by(Event.published_at.desc()).limit(20).all()
        
        # Top C/D "if true" items
        cd_events = db.query(Event).filter(
            and_(
                Event.evidence_tier.in_(["C", "D"]),
                Event.published_at >= seven_days_ago,
                Event.retracted == False,
            )
        ).order_by(Event.published_at.desc()).limit(5).all()
        
        def event_to_dict(e):
            links = db.query(EventSignpostLink).filter(EventSignpostLink.event_id == e.id).all()
            signposts = []
            for link in links:
                sp = db.query(Signpost).filter(Signpost.id == link.signpost_id).first()
                if sp:
                    signposts.append({"code": sp.code, "name": sp.name})
            return {
                "id": e.id,
                "title": e.title,
                "summary": e.summary,
                "url": e.source_url,
                "publisher": e.publisher,
                "date": e.published_at.isoformat() if e.published_at else None,
                "tier": e.evidence_tier,
                "signposts": signposts,
            }
        
        digest = {
            "version": "1.0",
            "week": f"{year}-W{week_num:02d}",
            "week_start": week_start.isoformat(),
            "generated_at": now.isoformat(),
            "license": "CC BY 4.0",
            "ab_events": [event_to_dict(e) for e in ab_events],
            "cd_if_true": [event_to_dict(e) for e in cd_events],
        }
        
        # Write JSON
        output_dir = Path(__file__).parent.parent / "public" / "digests"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        json_path = output_dir / f"{year}-W{week_num:02d}.json"
        with open(json_path, "w") as f:
            json.dump(digest, f, indent=2)
        
        print(f"✓ Generated digest: {json_path}")
        print(f"  A/B events: {len(ab_events)}")
        print(f"  C/D if-true: {len(cd_events)}")
        
        return {"status": "success", "path": str(json_path)}
    
    finally:
        db.close()


if __name__ == "__main__":
    generate_digest()
