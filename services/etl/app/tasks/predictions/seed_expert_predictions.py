"""Seed expert predictions from various sources."""
from datetime import date
from typing import List, Dict

from app.database import SessionLocal
from app.models import ExpertPrediction, Signpost


def seed_ai2027_predictions() -> List[Dict]:
    """Seed predictions from AI2027 roadmap."""
    return [
        {
            "signpost_code": "swe_bench_85",
            "source": "AI2027",
            "predicted_date": date(2025, 12, 31),
            "predicted_value": 85.0,
            "confidence_lower": 80.0,
            "confidence_upper": 90.0,
            "rationale": "SWE-bench 85% by end of 2025 based on current LLM coding capabilities trajectory"
        },
        {
            "signpost_code": "swe_bench_90",
            "source": "AI2027",
            "predicted_date": date(2026, 6, 30),
            "predicted_value": 90.0,
            "confidence_lower": 85.0,
            "confidence_upper": 95.0,
            "rationale": "SWE-bench 90% by mid-2026 assuming continued scaling and code-specific training"
        },
        {
            "signpost_code": "osworld_80",
            "source": "AI2027",
            "predicted_date": date(2026, 12, 31),
            "predicted_value": 80.0,
            "confidence_lower": 75.0,
            "confidence_upper": 85.0,
            "rationale": "OSWorld 80% by end of 2026 as agents become more reliable at OS interactions"
        },
        {
            "signpost_code": "gpqa_diamond_85",
            "source": "AI2027",
            "predicted_date": date(2027, 6, 30),
            "predicted_value": 85.0,
            "confidence_lower": 80.0,
            "confidence_upper": 90.0,
            "rationale": "GPQA Diamond 85% by mid-2027 as models improve at graduate-level physics"
        }
    ]


def seed_aschenbrenner_predictions() -> List[Dict]:
    """Seed predictions from Aschenbrenner's timeline."""
    return [
        {
            "signpost_code": "swe_bench_85",
            "source": "Aschenbrenner",
            "predicted_date": date(2025, 8, 15),
            "predicted_value": 85.0,
            "confidence_lower": 80.0,
            "confidence_upper": 90.0,
            "rationale": "SWE-bench 85% by August 2025 based on scaling laws and current progress"
        },
        {
            "signpost_code": "swe_bench_90",
            "source": "Aschenbrenner",
            "predicted_date": date(2025, 12, 31),
            "predicted_value": 90.0,
            "confidence_lower": 85.0,
            "confidence_upper": 95.0,
            "rationale": "SWE-bench 90% by end of 2025, more aggressive timeline based on compute scaling"
        },
        {
            "signpost_code": "osworld_80",
            "source": "Aschenbrenner",
            "predicted_date": date(2026, 4, 15),
            "predicted_value": 80.0,
            "confidence_lower": 75.0,
            "confidence_upper": 85.0,
            "rationale": "OSWorld 80% by April 2026 as agents become more capable at system interactions"
        }
    ]


def seed_metaculus_predictions() -> List[Dict]:
    """Seed predictions from Metaculus forecasting platform."""
    return [
        {
            "signpost_code": "swe_bench_85",
            "source": "Metaculus",
            "predicted_date": date(2026, 3, 15),
            "predicted_value": 85.0,
            "confidence_lower": 80.0,
            "confidence_upper": 90.0,
            "rationale": "SWE-bench 85% by March 2026 based on community consensus and current trends"
        },
        {
            "signpost_code": "swe_bench_90",
            "source": "Metaculus",
            "predicted_date": date(2026, 9, 30),
            "predicted_value": 90.0,
            "confidence_lower": 85.0,
            "confidence_upper": 95.0,
            "rationale": "SWE-bench 90% by September 2026, more conservative estimate from crowd wisdom"
        },
        {
            "signpost_code": "gpqa_diamond_85",
            "source": "Metaculus",
            "predicted_date": date(2027, 12, 31),
            "predicted_value": 85.0,
            "confidence_lower": 80.0,
            "confidence_upper": 90.0,
            "rationale": "GPQA Diamond 85% by end of 2027, challenging benchmark requiring deep physics understanding"
        }
    ]


def seed_custom_predictions() -> List[Dict]:
    """Seed some custom predictions for demonstration."""
    return [
        {
            "signpost_code": "webarena_80",
            "source": "Custom Analysis",
            "predicted_date": date(2026, 8, 31),
            "predicted_value": 80.0,
            "confidence_lower": 75.0,
            "confidence_upper": 85.0,
            "rationale": "WebArena 80% by August 2026 as web automation becomes more reliable"
        },
        {
            "signpost_code": "compute_1e26",
            "source": "Custom Analysis",
            "predicted_date": date(2027, 6, 30),
            "predicted_value": 1e26,
            "confidence_lower": 8e25,
            "confidence_upper": 1.2e26,
            "rationale": "1e26 FLOP training runs by mid-2027 based on current scaling trends"
        }
    ]


def seed_all_predictions():
    """Seed all expert predictions into the database."""
    db = SessionLocal()
    try:
        # Get all predictions from all sources
        all_predictions = (
            seed_ai2027_predictions() +
            seed_aschenbrenner_predictions() +
            seed_metaculus_predictions() +
            seed_custom_predictions()
        )
        
        # Get signpost mapping by code
        signposts = db.query(Signpost).all()
        signpost_by_code = {sp.code: sp.id for sp in signposts}
        
        created_count = 0
        for pred_data in all_predictions:
            signpost_code = pred_data.pop("signpost_code")
            signpost_id = signpost_by_code.get(signpost_code)
            
            if not signpost_id:
                print(f"⚠️  Signpost {signpost_code} not found, skipping prediction")
                continue
            
            # Check if prediction already exists
            existing = db.query(ExpertPrediction).filter(
                ExpertPrediction.signpost_id == signpost_id,
                ExpertPrediction.source == pred_data["source"],
                ExpertPrediction.predicted_date == pred_data["predicted_date"]
            ).first()
            
            if existing:
                print(f"⚠️  Prediction already exists for {signpost_code} from {pred_data['source']}")
                continue
            
            # Create new prediction
            prediction = ExpertPrediction(
                signpost_id=signpost_id,
                **pred_data
            )
            db.add(prediction)
            created_count += 1
        
        db.commit()
        print(f"✅ Created {created_count} expert predictions")
        
        # Show summary
        sources = db.query(ExpertPrediction.source).distinct().all()
        print(f"📊 Predictions by source:")
        for source in sources:
            count = db.query(ExpertPrediction).filter(ExpertPrediction.source == source[0]).count()
            print(f"  {source[0]}: {count} predictions")
        
    except Exception as e:
        print(f"❌ Error seeding predictions: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_all_predictions()
