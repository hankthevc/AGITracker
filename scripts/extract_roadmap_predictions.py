"""Extract and structure roadmap predictions from Situational Awareness and AI 2027."""
import sys
from datetime import date
from pathlib import Path

# Add services/etl to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Roadmap, RoadmapPrediction, Signpost


def extract_predictions():
    """Extract and seed roadmap predictions."""
    
    predictions_data = [
        # Aschenbrenner - Situational Awareness Predictions
        {
            "roadmap_slug": "aschenbrenner",
            "signpost_code": "swe_bench_85",
            "prediction_text": "Near-human coding capability (~85-90% on verified tasks)",
            "predicted_date": date(2025, 12, 31),
            "confidence_level": "medium",
            "source_page": "Situational Awareness, Chapter 2: Algorithmic Progress",
            "notes": "Assumes continued unhobbling + scaling"
        },
        {
            "roadmap_slug": "aschenbrenner",
            "signpost_code": "swe_bench_90",
            "prediction_text": "Professional-grade automated software engineering",
            "predicted_date": date(2026, 6, 30),
            "confidence_level": "low",
            "source_page": "Situational Awareness, Chapter 2: Algorithmic Progress",
            "notes": "Requires additional breakthroughs beyond current trajectory"
        },
        {
            "roadmap_slug": "aschenbrenner",
            "signpost_code": None,  # General prediction
            "prediction_text": "10x effective compute every ~9 months through 2027",
            "predicted_date": date(2027, 1, 1),
            "confidence_level": "high",
            "source_page": "Situational Awareness, Chapter 1: Compute Scaling",
            "notes": "Core assumption underlying all capability predictions"
        },
        {
            "roadmap_slug": "aschenbrenner",
            "signpost_code": None,
            "prediction_text": "Algorithmic unhobbling gains equivalent to ~3 OOMs by 2027",
            "predicted_date": date(2027, 1, 1),
            "confidence_level": "medium",
            "source_page": "Situational Awareness, Chapter 2: Algorithmic Progress",
            "notes": "Assumes continued rapid progress in RL, reasoning, tool use"
        },
        {
            "roadmap_slug": "aschenbrenner",
            "signpost_code": None,
            "prediction_text": "Drop-in remote workers capable of most knowledge work tasks",
            "predicted_date": date(2027, 1, 1),
            "confidence_level": "medium",
            "source_page": "Situational Awareness, Chapter 3: AGI Timeline",
            "notes": "Combines capabilities + agents progress"
        },
        {
            "roadmap_slug": "aschenbrenner",
            "signpost_code": None,
            "prediction_text": "Securing model weights becomes national security priority",
            "predicted_date": date(2026, 1, 1),
            "confidence_level": "high",
            "source_page": "Situational Awareness, Chapter 5: Security",
            "notes": "Triggered by clear path to transformative AI"
        },
        
        # AI 2027 Scenario Predictions
        {
            "roadmap_slug": "ai2027",
            "signpost_code": "swe_bench_85",
            "prediction_text": "85% on SWE-bench Verified",
            "predicted_date": date(2026, 10, 1),
            "confidence_level": "medium",
            "source_page": "AI 2027 Scenarios, Baseline Track",
            "notes": "Milestone on path to autonomous coding"
        },
        {
            "roadmap_slug": "ai2027",
            "signpost_code": "swe_bench_70",
            "prediction_text": "70% on SWE-bench Verified - first major milestone",
            "predicted_date": date(2025, 6, 1),
            "confidence_level": "high",
            "source_page": "AI 2027 Scenarios, Early Indicators",
            "notes": "Already achieved by Claude 4.5 Sonnet (Oct 2024)"
        },
        {
            "roadmap_slug": "ai2027",
            "signpost_code": "osworld_50",
            "prediction_text": "50% on OSWorld - competent computer use",
            "predicted_date": date(2026, 1, 1),
            "confidence_level": "medium",
            "source_page": "AI 2027 Scenarios, Agent Capabilities",
            "notes": "Requires multi-step reasoning + tool use"
        },
        {
            "roadmap_slug": "ai2027",
            "signpost_code": "osworld_70",
            "prediction_text": "70% on OSWorld - advanced OS-level autonomy",
            "predicted_date": date(2027, 1, 1),
            "confidence_level": "low",
            "source_page": "AI 2027 Scenarios, Agent Capabilities",
            "notes": "Close to drop-in remote worker capability"
        },
        {
            "roadmap_slug": "ai2027",
            "signpost_code": "webarena_60",
            "prediction_text": "60% on WebArena - reliable web navigation",
            "predicted_date": date(2026, 1, 1),
            "confidence_level": "medium",
            "source_page": "AI 2027 Scenarios, Agent Capabilities",
            "notes": "Key for autonomous research and data gathering"
        },
        {
            "roadmap_slug": "ai2027",
            "signpost_code": "webarena_80",
            "prediction_text": "80% on WebArena - human-level web interaction",
            "predicted_date": date(2027, 1, 1),
            "confidence_level": "low",
            "source_page": "AI 2027 Scenarios, Agent Capabilities",
            "notes": "Enables fully autonomous web-based workflows"
        },
        {
            "roadmap_slug": "ai2027",
            "signpost_code": "gpqa_75",
            "prediction_text": "75% on GPQA Diamond - expert-level reasoning",
            "predicted_date": date(2026, 1, 1),
            "confidence_level": "medium",
            "source_page": "AI 2027 Scenarios, Reasoning Capabilities",
            "notes": "PhD-level scientific reasoning"
        },
        {
            "roadmap_slug": "ai2027",
            "signpost_code": "gpqa_85",
            "prediction_text": "85% on GPQA Diamond - superhuman scientific reasoning",
            "predicted_date": date(2027, 1, 1),
            "confidence_level": "low",
            "source_page": "AI 2027 Scenarios, Reasoning Capabilities",
            "notes": "Exceeds typical PhD performance"
        },
        {
            "roadmap_slug": "ai2027",
            "signpost_code": None,
            "prediction_text": "Training runs reach 10^26 FLOPs",
            "predicted_date": date(2025, 12, 1),
            "confidence_level": "high",
            "source_page": "AI 2027 Scenarios, Compute Track",
            "notes": "~100B parameter dense models or equivalent MoE"
        },
        {
            "roadmap_slug": "ai2027",
            "signpost_code": None,
            "prediction_text": "Training runs reach 10^27 FLOPs",
            "predicted_date": date(2027, 1, 1),
            "confidence_level": "medium",
            "source_page": "AI 2027 Scenarios, Compute Track",
            "notes": "Approaching 'transformative AI' threshold"
        },
        
        # Cotra - Bio Anchors / Epoch Compute
        {
            "roadmap_slug": "cotra",
            "signpost_code": None,
            "prediction_text": "Training compute reaches biological anchor threshold",
            "predicted_date": date(2026, 1, 1),
            "confidence_level": "medium",
            "source_page": "Cotra Bio Anchors, Median Estimate",
            "notes": "~10^28-10^29 FLOPs for transformative AI"
        },
        {
            "roadmap_slug": "cotra",
            "signpost_code": None,
            "prediction_text": "Algorithmic progress equivalent to 2-3 OOMs",
            "predicted_date": date(2027, 1, 1),
            "confidence_level": "low",
            "source_page": "Epoch Analysis, Historical Trends",
            "notes": "Extrapolating past rates of algorithmic improvement"
        },
    ]
    
    db = SessionLocal()
    try:
        # Get roadmap and signpost mappings
        roadmaps = {r.slug: r for r in db.query(Roadmap).all()}
        signposts = {s.code: s for s in db.query(Signpost).all()}
        
        inserted_count = 0
        for pred_data in predictions_data:
            roadmap = roadmaps.get(pred_data["roadmap_slug"])
            if not roadmap:
                print(f"Warning: Roadmap '{pred_data['roadmap_slug']}' not found")
                continue
            
            signpost = None
            if pred_data["signpost_code"]:
                signpost = signposts.get(pred_data["signpost_code"])
                if not signpost:
                    print(f"Warning: Signpost '{pred_data['signpost_code']}' not found")
            
            # Check if prediction already exists
            existing = db.query(RoadmapPrediction).filter_by(
                roadmap_id=roadmap.id,
                signpost_id=signpost.id if signpost else None,
                prediction_text=pred_data["prediction_text"]
            ).first()
            
            if not existing:
                prediction = RoadmapPrediction(
                    roadmap_id=roadmap.id,
                    signpost_id=signpost.id if signpost else None,
                    prediction_text=pred_data["prediction_text"],
                    predicted_date=pred_data["predicted_date"],
                    confidence_level=pred_data["confidence_level"],
                    source_page=pred_data["source_page"],
                    notes=pred_data["notes"]
                )
                db.add(prediction)
                inserted_count += 1
        
        db.commit()
        print(f"✓ Inserted {inserted_count} roadmap predictions")
        
    except Exception as e:
        print(f"Error seeding predictions: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    extract_predictions()

