"""Seed AI-2027 roadmap predictions from catalog JSON."""
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from app.database import SessionLocal
from app.models import Roadmap, RoadmapPrediction


def parse_date(date_str: str) -> datetime.date:
    """Parse YYYY-MM format to date."""
    year, month = date_str.split('-')
    return datetime(int(year), int(month), 1).date()


def seed_ai2027_predictions():
    """Load AI-2027 predictions from JSON catalog into database."""
    print("🔮 Seeding AI-2027 roadmap predictions...")
    print("="*60)
    
    # Load catalog
    catalog_path = Path(__file__).parent.parent / "infra" / "seeds" / "ai2027_catalog.json"
    
    with open(catalog_path, 'r') as f:
        catalog = json.load(f)
    
    predictions = catalog.get('predictions', [])
    print(f"📊 Loaded {len(predictions)} predictions from catalog")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Get AI-2027 roadmap (slug is 'ai2027')
        roadmap = db.query(Roadmap).filter(Roadmap.slug == 'ai2027').first()
        
        if not roadmap:
            print("❌ AI 2027 roadmap not found. Run seed.py first.")
            return
        
        print(f"✓ Found roadmap: {roadmap.name} (id={roadmap.id})")
        
        # Upsert predictions
        created = 0
        updated = 0
        
        for pred in predictions:
            # Check if exists
            existing = db.query(RoadmapPrediction).filter(
                RoadmapPrediction.roadmap_id == roadmap.id,
                RoadmapPrediction.signpost_code == pred['signpost_code']
            ).first()
            
            target_date = parse_date(pred['target_date'])
            
            if existing:
                # Update
                existing.prediction_text = pred['label']
                existing.predicted_date = target_date
                existing.confidence_level = 'high' if pred['confidence'] >= 0.7 else 'medium' if pred['confidence'] >= 0.5 else 'low'
                existing.notes = pred['rationale']
                updated += 1
                print(f"  ↻ Updated: {pred['id']} → {pred['signpost_code']}")
            else:
                # Create
                new_pred = RoadmapPrediction(
                    roadmap_id=roadmap.id,
                    signpost_code=pred['signpost_code'],
                    prediction_text=pred['label'],
                    predicted_date=target_date,
                    confidence_level='high' if pred['confidence'] >= 0.7 else 'medium' if pred['confidence'] >= 0.5 else 'low',
                    source_page='AI 2027 Report',
                    notes=pred['rationale']
                )
                db.add(new_pred)
                created += 1
                print(f"  ✓ Created: {pred['id']} → {pred['signpost_code']} (target: {pred['target_date']})")
        
        db.commit()
        
        print(f"\n✅ Done! Created: {created}, Updated: {updated}")
        print(f"📈 Total AI-2027 predictions in DB: {db.query(RoadmapPrediction).filter(RoadmapPrediction.roadmap_id == roadmap.id).count()}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_ai2027_predictions()

