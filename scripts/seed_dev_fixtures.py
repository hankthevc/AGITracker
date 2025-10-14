#!/usr/bin/env python3
"""
Dev-only fixture seeding script.
Creates synthetic A-tier claims for categories with no real data yet.
This allows local development and E2E testing of the full UI without waiting for real data.

Usage:
  export DEV_FIXTURE_INPUTS=true
  python scripts/seed_dev_fixtures.py
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.etl.app.models import (
    Roadmap, Signpost, Benchmark, Source, Claim, ClaimSignpost, ClaimBenchmark
)

# Use environment variable or fallback to dev default
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg://postgres:postgres@localhost:5432/agi_signpost_tracker"
)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def seed_dev_fixtures():
    """Seed development fixtures for Inputs category."""
    
    # Check if dev fixtures are enabled
    if os.getenv("DEV_FIXTURE_INPUTS", "false").lower() != "true":
        print("DEV_FIXTURE_INPUTS not enabled. Skipping dev fixtures.")
        return
    
    print("🧪 Seeding development fixtures...")
    
    db = Session()
    try:
        # Get or create dev fixture source
        # Dev fixtures use a special domain "dev-fixture.local" for filtering
        source = db.query(Source).filter(Source.url == "https://dev-fixture.local/inputs").first()
        if not source:
            source = Source(
                url="https://dev-fixture.local/inputs",
                domain="dev-fixture.local",
                source_type="blog",  # Use existing type
                credibility="A",  # A-tier to ensure it moves gauges
            )
            db.add(source)
            db.flush()
            print(f"  ✓ Created dev fixture source (ID {source.id})")
        else:
            print(f"  ↻ Dev fixture source already exists (ID {source.id})")
        
        # Get Inputs signposts
        inputs_signposts = db.query(Signpost).filter(Signpost.category == "inputs").all()
        if not inputs_signposts:
            print("  ⚠️  No Inputs signposts found. Run seed.py first.")
            return
        
        # Create A-tier claim for Inputs: "Algorithmic efficiency improvement"
        claim_data = {
            "url_hash": "dev-fixture-inputs-algo-efficiency-2024",
            "source_id": source.id,
            "title": "[DEV FIXTURE] Algorithmic efficiency +1 OOM since 2023",
            "body": "Development fixture: Simulates a 10x improvement in algorithmic efficiency for training large language models. This is synthetic data for local testing only.",
            "observed_at": datetime.utcnow() - timedelta(days=7),  # 1 week ago
            "retracted": False,
        }
        
        existing_claim = db.query(Claim).filter(Claim.url_hash == claim_data["url_hash"]).first()
        
        if not existing_claim:
            claim = Claim(**claim_data)
            db.add(claim)
            db.flush()
            print(f"  ✓ Created dev fixture claim (ID {claim.id})")
            
            # Link to first Inputs signpost (algorithmic efficiency)
            algo_signpost = next((s for s in inputs_signposts if "algorithm" in s.name.lower()), inputs_signposts[0])
            
            claim_signpost = ClaimSignpost(
                claim_id=claim.id,
                signpost_id=algo_signpost.id,
                score_contribution=0.10,  # 10% progress
                mapped_via="dev_fixture",
            )
            db.add(claim_signpost)
            print(f"  ✓ Linked to signpost: {algo_signpost.name}")
            
            db.commit()
            print("✅ Dev fixtures seeded successfully!")
            print("   Note: Re-run snapshot computation to see this in the UI:")
            print("   curl -X POST http://localhost:8000/v1/recompute")
        else:
            print(f"  ↻ Dev fixture claim already exists (ID {existing_claim.id})")
    
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding dev fixtures: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_dev_fixtures()

