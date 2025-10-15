"""FastAPI main application for AGI Signpost Tracker API."""
import hashlib
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

# Add scoring package to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages" / "scoring" / "python"))

from app.config import settings
from app.database import get_db
from app.models import (
    Benchmark,
    ChangelogEntry,
    Claim,
    ClaimSignpost,
    IndexSnapshot,
    PaceAnalysis,
    Roadmap,
    RoadmapPrediction,
    Signpost,
    SignpostContent,
    Source,
)

# Import scoring functions
try:
    from core import compute_confidence_bands, compute_index_from_categories
except ImportError:
    from packages.scoring.python.core import (
        compute_confidence_bands,
        compute_index_from_categories,
    )

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="AGI Signpost Tracker API",
    version="1.0.0",
    description="Evidence-first dashboard tracking proximity to AGI via measurable signposts",
)

# Add rate limit state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - configurable via CORS_ORIGINS env var
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup: Initialize cache
@app.on_event("startup")
async def startup():
    """Initialize FastAPI cache with Redis backend."""
    try:
        redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        print(f"✓ FastAPI cache initialized with Redis: {settings.redis_url}")
    except Exception as e:
        print(f"⚠️  Could not connect to Redis for caching: {e}")
        print("   API will work without caching")


def generate_etag(content: str, preset: str = "equal") -> str:
    """
    Generate ETag from response content + preset.
    
    Ensures cache key varies by preset parameter (Task 0e requirement).
    """
    hash_input = f"{content}:{preset}"
    return hashlib.md5(hash_input.encode()).hexdigest()


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "agi-tracker-api", "version": "1.0.0"}


@app.get("/health/full")
async def health_full():
    """
    Full health check with configuration details for debugging.
    Returns API configuration and status.
    """
    return {
        "status": "ok",
        "preset_default": "equal",
        "cors_origins": [origin.strip() for origin in settings.cors_origins.split(",")],
        "time": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/v1/index")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
@cache(expire=settings.index_cache_ttl_seconds)
async def get_index(
    request: Request,
    response: Response,
    date_param: Optional[str] = Query(None, alias="date"),
    preset: str = Query("equal", regex="^(equal|aschenbrenner|ai2027|custom)$"),
    db: Session = Depends(get_db),
):
    """
    Get AGI proximity index (overall + category scores).
    
    Query params:
    - date: Optional date (YYYY-MM-DD) for historical snapshot. Defaults to latest.
    - preset: Scoring preset (equal, aschenbrenner, ai2027). Default: equal.
    """
    # Parse date or use latest
    if date_param:
        try:
            target_date = datetime.strptime(date_param, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        target_date = date.today()
    
    # Get snapshot for date and preset
    snapshot = (
        db.query(IndexSnapshot)
        .filter(
            and_(
                IndexSnapshot.as_of_date <= target_date,
                IndexSnapshot.preset == preset
            )
        )
        .order_by(desc(IndexSnapshot.as_of_date))
        .first()
    )
    
    if not snapshot:
        # No snapshot exists - return zeros with insufficient flags
        return {
            "as_of_date": str(target_date),
            "overall": 0.0,
            "capabilities": 0.0,
            "agents": 0.0,
            "inputs": 0.0,
            "security": 0.0,
            "safety_margin": 0.0,
            "preset": preset,
            "confidence_bands": {
                "overall": {"lower": 0.0, "upper": 1.0},
                "capabilities": {"lower": 0.0, "upper": 1.0},
                "agents": {"lower": 0.0, "upper": 1.0},
                "inputs": {"lower": 0.0, "upper": 1.0},
                "security": {"lower": 0.0, "upper": 1.0},
            },
            "insufficient": {
                "overall": True,
                "categories": {
                    "capabilities": True,
                    "agents": True,
                    "inputs": True,
                    "security": True,
                }
            },
        }
    
    # Extract category values
    capabilities_val = float(snapshot.capabilities) if snapshot.capabilities else 0.0
    agents_val = float(snapshot.agents) if snapshot.agents else 0.0
    inputs_val = float(snapshot.inputs) if snapshot.inputs else 0.0
    security_val = float(snapshot.security) if snapshot.security else 0.0
    
    # Detect insufficient data: overall is insufficient if inputs OR security is zero
    # (harmonic mean with zero produces zero, which is uninformative)
    insufficient_overall = (inputs_val == 0.0 or security_val == 0.0)
    
    result = {
        "as_of_date": str(snapshot.as_of_date),
        "overall": float(snapshot.overall) if snapshot.overall else 0.0,
        "capabilities": capabilities_val,
        "agents": agents_val,
        "inputs": inputs_val,
        "security": security_val,
        "safety_margin": float(snapshot.safety_margin) if snapshot.safety_margin else 0.0,
        "preset": snapshot.preset,
        "confidence_bands": snapshot.details.get("confidence_bands", {})
        if snapshot.details
        else {},
        "insufficient": {
            "overall": insufficient_overall,
            "categories": {
                "capabilities": capabilities_val == 0.0,
                "agents": agents_val == 0.0,
                "inputs": inputs_val == 0.0,
                "security": security_val == 0.0,
            }
        },
    }
    
    # Generate ETag (varies by preset per Task 0e)
    content_json = json.dumps(result, sort_keys=True)
    etag = generate_etag(content_json, preset)
    
    # Check If-None-Match header
    if_none_match = request.headers.get("if-none-match")
    if if_none_match and if_none_match == etag:
        return Response(status_code=304)  # Not Modified
    
    # Set ETag header
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = f"public, max-age={settings.index_cache_ttl_seconds}"
    
    return result


@app.get("/v1/signposts")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
@cache(expire=settings.signposts_cache_ttl_seconds)
async def list_signposts(
    request: Request,
    category: Optional[str] = Query(None, regex="^(capabilities|agents|inputs|security)$"),
    first_class: Optional[bool] = None,
    roadmap: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List signposts with optional filtering.
    
    Query params:
    - category: Filter by category (capabilities, agents, inputs, security)
    - first_class: Filter by first-class status
    - roadmap: Filter by roadmap slug
    """
    query = db.query(Signpost)
    
    if category:
        query = query.filter(Signpost.category == category)
    
    if first_class is not None:
        query = query.filter(Signpost.first_class == first_class)
    
    if roadmap:
        roadmap_obj = db.query(Roadmap).filter(Roadmap.slug == roadmap).first()
        if roadmap_obj:
            query = query.filter(Signpost.roadmap_id == roadmap_obj.id)
    
    signposts = query.all()
    
    return [
        {
            "id": s.id,
            "code": s.code,
            "name": s.name,
            "description": s.description,
            "category": s.category,
            "metric_name": s.metric_name,
            "unit": s.unit,
            "direction": s.direction,
            "baseline_value": float(s.baseline_value) if s.baseline_value else None,
            "target_value": float(s.target_value) if s.target_value else None,
            "first_class": s.first_class,
        }
        for s in signposts
    ]


@app.get("/v1/signposts/{signpost_id}")
async def get_signpost(signpost_id: int, db: Session = Depends(get_db)):
    """Get detailed signpost information with evidence counts."""
    signpost = db.query(Signpost).filter(Signpost.id == signpost_id).first()
    
    if not signpost:
        raise HTTPException(status_code=404, detail="Signpost not found")
    
    # Count evidence by tier
    evidence_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    
    claim_signposts = (
        db.query(ClaimSignpost)
        .filter(ClaimSignpost.signpost_id == signpost_id)
        .all()
    )
    
    for cs in claim_signposts:
        claim = db.query(Claim).filter(Claim.id == cs.claim_id).first()
        if claim and not claim.retracted:
            source = db.query(Source).filter(Source.id == claim.source_id).first()
            if source:
                tier = source.credibility
                evidence_counts[tier] = evidence_counts.get(tier, 0) + 1
    
    return {
        "id": signpost.id,
        "code": signpost.code,
        "name": signpost.name,
        "description": signpost.description,
        "category": signpost.category,
        "metric_name": signpost.metric_name,
        "unit": signpost.unit,
        "direction": signpost.direction,
        "baseline_value": float(signpost.baseline_value) if signpost.baseline_value else None,
        "target_value": float(signpost.target_value) if signpost.target_value else None,
        "methodology_url": signpost.methodology_url,
        "first_class": signpost.first_class,
        "short_explainer": signpost.short_explainer,
        "icon_emoji": signpost.icon_emoji,
        "evidence_count": evidence_counts,
    }


@app.get("/v1/signposts/by-code/{code}")
async def get_signpost_by_code(code: str, db: Session = Depends(get_db)):
    """Get signpost by code."""
    signpost = db.query(Signpost).filter(Signpost.code == code).first()
    
    if not signpost:
        raise HTTPException(status_code=404, detail="Signpost not found")
    
    return {
        "id": signpost.id,
        "code": signpost.code,
        "name": signpost.name,
        "description": signpost.description,
        "category": signpost.category,
        "metric_name": signpost.metric_name,
        "unit": signpost.unit,
        "direction": signpost.direction,
        "baseline_value": float(signpost.baseline_value) if signpost.baseline_value else None,
        "target_value": float(signpost.target_value) if signpost.target_value else None,
        "methodology_url": signpost.methodology_url,
        "first_class": signpost.first_class,
        "short_explainer": signpost.short_explainer,
        "icon_emoji": signpost.icon_emoji,
    }


@app.get("/v1/signposts/by-code/{code}/content")
async def get_signpost_content(code: str, db: Session = Depends(get_db)):
    """Get rich educational content for a signpost."""
    signpost = db.query(Signpost).filter(Signpost.code == code).first()
    
    if not signpost:
        raise HTTPException(status_code=404, detail="Signpost not found")
    
    content = db.query(SignpostContent).filter(SignpostContent.signpost_id == signpost.id).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found for this signpost")
    
    return {
        "signpost_code": signpost.code,
        "why_matters": content.why_matters,
        "current_state": content.current_state,
        "key_papers": content.key_papers,
        "key_announcements": content.key_announcements,
        "technical_explanation": content.technical_explanation,
        "updated_at": content.updated_at.isoformat() if content.updated_at else None,
    }


@app.get("/v1/signposts/by-code/{code}/predictions")
async def get_signpost_predictions(code: str, db: Session = Depends(get_db)):
    """Get roadmap predictions for a signpost."""
    signpost = db.query(Signpost).filter(Signpost.code == code).first()
    
    if not signpost:
        raise HTTPException(status_code=404, detail="Signpost not found")
    
    predictions = db.query(RoadmapPrediction).filter(
        RoadmapPrediction.signpost_id == signpost.id
    ).all()
    
    results = []
    for pred in predictions:
        roadmap = db.query(Roadmap).filter(Roadmap.id == pred.roadmap_id).first()
        results.append({
            "roadmap_name": roadmap.name if roadmap else None,
            "roadmap_slug": roadmap.slug if roadmap else None,
            "prediction_text": pred.prediction_text,
            "predicted_date": pred.predicted_date.isoformat() if pred.predicted_date else None,
            "confidence_level": pred.confidence_level,
            "source_page": pred.source_page,
            "notes": pred.notes,
        })
    
    return {"predictions": results}


@app.get("/v1/signposts/by-code/{code}/pace")
async def get_pace_analysis(code: str, db: Session = Depends(get_db)):
    """Get pace analysis comparing current progress to roadmap predictions."""
    signpost = db.query(Signpost).filter(Signpost.code == code).first()
    
    if not signpost:
        raise HTTPException(status_code=404, detail="Signpost not found")
    
    # Get current value from latest claim
    latest_claim_signpost = (
        db.query(ClaimSignpost)
        .filter(ClaimSignpost.signpost_id == signpost.id)
        .join(Claim)
        .filter(Claim.retracted == False)
        .order_by(desc(Claim.observed_at))
        .first()
    )
    
    current_value = None
    current_date = None
    if latest_claim_signpost:
        claim = db.query(Claim).filter(Claim.id == latest_claim_signpost.claim_id).first()
        if claim:
            current_value = float(claim.metric_value) if claim.metric_value else None
            current_date = claim.observed_at.date()
    
    # Get predictions
    predictions = db.query(RoadmapPrediction).filter(
        RoadmapPrediction.signpost_id == signpost.id
    ).all()
    
    # Calculate ahead/behind for each roadmap (simplified linear interpolation)
    today = date.today()
    pace_metrics = []
    
    for pred in predictions:
        if current_value and pred.predicted_date and signpost.target_value:
            # Calculate progress (0-1)
            baseline = float(signpost.baseline_value) if signpost.baseline_value else 0.0
            target = float(signpost.target_value)
            
            if signpost.direction == ">=":
                progress = (current_value - baseline) / (target - baseline) if target != baseline else 0
            else:  # "<="
                progress = (baseline - current_value) / (baseline - target) if baseline != target else 0
            
            progress = max(0.0, min(1.0, progress))
            
            # Simple linear interpolation for expected progress
            days_until_target = (pred.predicted_date - today).days
            days_since_baseline = (today - date(2023, 1, 1)).days  # Approximate baseline date
            
            if days_since_baseline > 0:
                expected_progress = days_since_baseline / (days_since_baseline + days_until_target)
                days_ahead = int((progress - expected_progress) * days_until_target)
            else:
                days_ahead = 0
            
            roadmap = db.query(Roadmap).filter(Roadmap.id == pred.roadmap_id).first()
            
            pace_metrics.append({
                "roadmap_name": roadmap.name if roadmap else None,
                "roadmap_slug": roadmap.slug if roadmap else None,
                "days_ahead": days_ahead,
                "status": "ahead" if days_ahead > 0 else "behind" if days_ahead < 0 else "on_track",
                "current_value": current_value,
                "current_progress": round(progress * 100, 1),
                "predicted_date": pred.predicted_date.isoformat(),
            })
    
    # Get human-written analyses
    analyses_records = db.query(PaceAnalysis).filter(
        PaceAnalysis.signpost_id == signpost.id
    ).all()
    
    analyses = {}
    for analysis in analyses_records:
        roadmap = db.query(Roadmap).filter(Roadmap.id == analysis.roadmap_id).first()
        if roadmap:
            analyses[roadmap.slug] = analysis.analysis_text
    
    return {
        "signpost_code": signpost.code,
        "current_value": current_value,
        "current_date": current_date.isoformat() if current_date else None,
        "pace_metrics": pace_metrics,
        "analyses": analyses,
    }


@app.get("/v1/evidence")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
@cache(expire=settings.evidence_cache_ttl_seconds)
async def list_evidence(
    request: Request,
    signpost_id: Optional[int] = None,
    tier: Optional[str] = Query(None, regex="^[ABCD]$"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    List evidence claims with optional filtering.
    
    Query params:
    - signpost_id: Filter by signpost
    - tier: Filter by credibility tier (A/B/C/D)
    - skip: Pagination offset
    - limit: Page size (max 100)
    """
    limit = min(limit, 100)
    
    query = db.query(Claim).filter(Claim.retracted == False)
    
    if signpost_id:
        claim_ids = (
            db.query(ClaimSignpost.claim_id)
            .filter(ClaimSignpost.signpost_id == signpost_id)
            .all()
        )
        claim_ids = [c[0] for c in claim_ids]
        query = query.filter(Claim.id.in_(claim_ids))
    
    if tier:
        source_ids = (
            db.query(Source.id)
            .filter(Source.credibility == tier)
            .all()
        )
        source_ids = [s[0] for s in source_ids]
        query = query.filter(Claim.source_id.in_(source_ids))
    
    total = query.count()
    claims = query.order_by(desc(Claim.observed_at)).offset(skip).limit(limit).all()
    
    results = []
    for claim in claims:
        source = db.query(Source).filter(Source.id == claim.source_id).first()
        results.append(
            {
                "id": claim.id,
                "title": claim.title,
                "summary": claim.summary,
                "metric_name": claim.metric_name,
                "metric_value": float(claim.metric_value) if claim.metric_value else None,
                "unit": claim.unit,
                "observed_at": claim.observed_at.isoformat(),
                "source": {
                    "url": source.url if source else None,
                    "domain": source.domain if source else None,
                    "type": source.source_type if source else None,
                    "credibility": source.credibility if source else None,
                },
                "extraction_confidence": (
                    float(claim.extraction_confidence) if claim.extraction_confidence else None
                ),
                "retracted": claim.retracted,
            }
        )
    
    return {"total": total, "skip": skip, "limit": limit, "results": results}


@app.get("/v1/feed.json")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
@cache(expire=settings.feed_cache_ttl_seconds)
async def public_feed(request: Request, db: Session = Depends(get_db)):
    """
    Public JSON feed of extracted claims (CC BY 4.0).
    Safe for public consumption - excludes retracted/provisional and dev fixtures.
    """
    # Only include A/B tier (verified) claims
    # Exclude dev fixtures unless INCLUDE_DEV_FIXTURES env var is set
    include_dev_fixtures = os.getenv("INCLUDE_DEV_FIXTURES", "false").lower() == "true"
    
    query = db.query(Source.id).filter(Source.credibility.in_(["A", "B"]))
    if not include_dev_fixtures:
        query = query.filter(Source.domain != "dev-fixture.local")
    
    source_ids = query.all()
    source_ids = [s[0] for s in source_ids]
    
    claims = (
        db.query(Claim)
        .filter(
            and_(
                Claim.retracted == False,
                Claim.source_id.in_(source_ids)
            )
        )
        .order_by(desc(Claim.observed_at))
        .limit(100)
        .all()
    )
    
    feed_items = []
    for claim in claims:
        source = db.query(Source).filter(Source.id == claim.source_id).first()
        feed_items.append(
            {
                "title": claim.title,
                "summary": claim.summary,
                "metric": claim.metric_name,
                "value": float(claim.metric_value) if claim.metric_value else None,
                "unit": claim.unit,
                "date": claim.observed_at.isoformat(),
                "source_url": source.url if source else None,
                "tier": source.credibility if source else None,
            }
        )
    
    return {
        "version": "1.0",
        "license": "CC BY 4.0",
        "generated_at": datetime.utcnow().isoformat(),
        "items": feed_items,
    }


@app.get("/v1/changelog")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def changelog(request: Request, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Get recent changelog entries."""
    limit = min(limit, 100)
    
    total = db.query(ChangelogEntry).count()
    entries = (
        db.query(ChangelogEntry)
        .order_by(desc(ChangelogEntry.occurred_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "results": [
            {
                "id": e.id,
                "occurred_at": e.occurred_at.isoformat(),
                "type": e.type,
                "title": e.title,
                "body": e.body,
                "reason": e.reason,
            }
            for e in entries
        ],
    }


# Admin endpoints (protected by API key)


def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key for admin endpoints."""
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True


@app.post("/v1/retract")
async def retract_claim(
    claim_id: int,
    reason: str,
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Retract a claim (admin only)."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    claim.retracted = True
    
    # Create changelog entry
    changelog_entry = ChangelogEntry(
        type="retract",
        title=f"Retracted: {claim.title}",
        body=f"Claim {claim_id} has been retracted.",
        claim_id=claim_id,
        reason=reason,
    )
    db.add(changelog_entry)
    
    db.commit()
    
    return {"status": "success", "claim_id": claim_id, "retracted": True}


@app.post("/v1/recompute")
async def recompute_index(
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Trigger index recomputation (admin only)."""
    from app.tasks.snap_index import compute_daily_snapshot
    
    try:
        result = compute_daily_snapshot()
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recompute failed: {str(e)}")

