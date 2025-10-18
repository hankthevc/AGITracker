#!/usr/bin/env python3
"""
Verify backfill results: counts of events, links, and confidence distribution.

Usage:
  python scripts/verify_backfill.py

Reads DATABASE_URL from environment.
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add services/etl to import path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Event, EventSignpostLink


def fmt(n):
    return f"{n:,}"


def main():
    db: Session = SessionLocal()
    try:
        total_events = db.query(func.count(Event.id)).scalar() or 0
        total_links = db.query(func.count(EventSignpostLink.event_id)).scalar() or 0

        # Confidence buckets
        ge07 = (
            db.query(func.count(EventSignpostLink.event_id))
            .filter(EventSignpostLink.confidence >= 0.7)
            .scalar()
            or 0
        )
        ge09 = (
            db.query(func.count(EventSignpostLink.event_id))
            .filter(EventSignpostLink.confidence >= 0.9)
            .scalar()
            or 0
        )

        # Distinct events with any link >= 0.7
        ev_ge07 = (
            db.query(func.count(func.distinct(EventSignpostLink.event_id)))
            .filter(EventSignpostLink.confidence >= 0.7)
            .scalar()
            or 0
        )

        pct_ev_ge07 = (ev_ge07 / total_events * 100.0) if total_events else 0.0

        print("\n=== Backfill Verification ===")
        print(f"Time: {datetime.utcnow().isoformat()}Z")
        print(f"Total events: {fmt(total_events)}")
        print(f"Total links:  {fmt(total_links)}")
        print(f"Events with ≥0.7 confidence: {fmt(ev_ge07)} ({pct_ev_ge07:.1f}%)")
        print(f"Links ≥0.7: {fmt(ge07)}; ≥0.9: {fmt(ge09)}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
