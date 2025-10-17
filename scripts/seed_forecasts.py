#!/usr/bin/env python3
"""
Load multi-source forecast seeds into roadmap_predictions table.

Each JSON file in infra/seeds/forecasts/ becomes a roadmap source.
"""
import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

# Add services/etl to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from app.database import SessionLocal
from app.models import RoadmapPrediction, Signpost, Roadmap


def confidence_to_level(confidence: float) -> str:
    """Convert numeric confidence to categorical level."""
    if confidence >= 0.7:
        return "high"
    elif confidence >= 0.4:
        return "medium"
    else:
        return "low"


def ensure_roadmap_exists(db, slug, name):
    """Ensure a roadmap entry exists, creating if needed."""
    existing = db.query(Roadmap).filter(Roadmap.slug == slug).first()
    if not existing:
        new_roadmap = Roadmap(
            slug=slug,
            name=name,
            description=f"Forecast predictions from {name}",
            preset_weights={}  # Empty weights for forecast-only sources
        )
        db.add(new_roadmap)
        db.flush()  # Get ID without committing
        return new_roadmap
    return existing


def load_forecasts(dry_run=False):
    """Load forecast seeds from JSON files into database."""
    forecasts_dir = Path(__file__).parent.parent / "infra" / "seeds" / "forecasts"
    
    if not forecasts_dir.exists():
        print(f"❌ Forecasts directory not found: {forecasts_dir}")
        return 1
    
    db = SessionLocal()
    stats = {"total": 0, "created": 0, "updated": 0, "roadmaps_created": 0}
    
    # Friendly names for forecast sources
    roadmap_names = {
        "ai2027": "AI 2027 Project",
        "aschenbrenner": "Aschenbrenner's Situational Awareness",
        "epoch_ai": "Epoch AI Compute Database",
        "ajeya_bioanchors": "Ajeya Cotra Bio Anchors",
        "metaculus": "Metaculus Community",
        "miri_soares": "MIRI/Soares Short Timelines",
        "openai_preparedness": "OpenAI Preparedness Framework"
    }
    
    try:
        # Get all signpost codes for validation
        signpost_codes = {sp.code for sp in db.query(Signpost.code).all()}
        
        # Process each forecast JSON file
        for json_file in sorted(forecasts_dir.glob("*.json")):
            roadmap_slug = json_file.stem  # filename without .json
            roadmap_name = roadmap_names.get(roadmap_slug, roadmap_slug.replace("_", " ").title())
            
            print(f"\n📊 Loading {roadmap_slug}.json...")
            
            # Ensure roadmap entry exists
            if not dry_run:
                roadmap = ensure_roadmap_exists(db, roadmap_slug, roadmap_name)
                if roadmap.id is None:  # Just created
                    stats["roadmaps_created"] += 1
                    print(f"  ✓ Created roadmap: {roadmap_name}")
                roadmap_id = roadmap.id
            else:
                # In dry run, try to get existing or use 0 as placeholder
                existing_roadmap = db.query(Roadmap).filter(Roadmap.slug == roadmap_slug).first()
                roadmap_id = existing_roadmap.id if existing_roadmap else 0
            
            with open(json_file) as f:
                predictions = json.load(f)
            
            for pred in predictions:
                stats["total"] += 1
                
                # Validate signpost exists
                if pred["signpost_code"] not in signpost_codes:
                    print(f"  ⚠️  Unknown signpost: {pred['signpost_code']}, skipping")
                    continue
                
                # Parse target date
                target_date = None
                if pred.get("target_date"):
                    try:
                        target_date = datetime.strptime(pred["target_date"], "%Y-%m-%d").date()
                    except ValueError:
                        print(f"  ⚠️  Invalid date format: {pred['target_date']}")
                
                # Check if prediction already exists
                existing = db.query(RoadmapPrediction).filter(
                    RoadmapPrediction.roadmap_id == roadmap_id,
                    RoadmapPrediction.signpost_code == pred["signpost_code"]
                ).first()
                
                # Convert numeric confidence to categorical
                confidence_level = confidence_to_level(pred.get("confidence", 0.5))
                
                # Resolve signpost_id for faster joins in UI/API if available
                signpost = db.query(Signpost).filter(Signpost.code == pred["signpost_code"]).first()
                signpost_id = signpost.id if signpost else None

                if existing:
                    # Update existing prediction
                    if not dry_run:
                        existing.predicted_date = target_date
                        existing.prediction_text = pred.get("label", pred["signpost_code"])
                        existing.confidence_level = confidence_level
                        existing.notes = pred.get("rationale", "")
                        existing.signpost_id = signpost_id
                    stats["updated"] += 1
                    action = "UPDATE" if not dry_run else "WOULD UPDATE"
                else:
                    # Create new prediction
                    if not dry_run:
                        new_pred = RoadmapPrediction(
                            roadmap_id=roadmap_id,
                            signpost_id=signpost_id,
                            signpost_code=pred["signpost_code"],
                            predicted_date=target_date,
                            prediction_text=pred.get("label", pred["signpost_code"]),
                            confidence_level=confidence_level,
                            notes=pred.get("rationale", "")
                        )
                        db.add(new_pred)
                    stats["created"] += 1
                    action = "CREATE" if not dry_run else "WOULD CREATE"
                
                print(f"  ✓ {action}: {pred['signpost_code']} → {pred.get('target_date', 'TBD')}")
        
        if not dry_run:
            db.commit()
            print(f"\n✅ Forecast seeds loaded successfully!")
        else:
            print(f"\n🔍 Dry run complete (no changes made)")
        
        print(f"\n📈 Summary:")
        print(f"   Total predictions: {stats['total']}")
        print(f"   New roadmaps: {stats.get('roadmaps_created', 0)}")
        print(f"   Created: {stats['created']}")
        print(f"   Updated: {stats['updated']}")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error loading forecasts: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load forecast seeds into roadmap_predictions")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without committing")
    args = parser.parse_args()
    
    sys.exit(load_forecasts(dry_run=args.dry_run))

