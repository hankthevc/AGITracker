"""FastAPI main application for AGI Signpost Tracker API."""
import hashlib
import json
import os
import sys
import uuid
from contextvars import ContextVar
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
from sqlalchemy import and_, desc, func, or_
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
    Event,
    EventAnalysis,
    EventEntity,
    EventSignpostLink,
    IndexSnapshot,
    PaceAnalysis,
    Roadmap,
    RoadmapPrediction,
    Signpost,
    SignpostContent,
    Source,
)
from app.utils.query_helpers import query_active_events

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

# Context variable for request tracing
request_id_context: ContextVar[str] = ContextVar("request_id", default="")

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


# Request ID middleware - adds X-Request-ID to all requests/responses
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add X-Request-ID header to requests and responses for tracing."""
    import structlog
    
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request_id_context.set(request_id)
    
    # Bind request_id to structlog context for all logs in this request
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


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
    Full health check with configuration details and task watchdogs.
    Returns API configuration, task status, and system health.
    """
    from app.utils.task_tracking import get_all_task_statuses
    
    task_statuses = get_all_task_statuses()
    
    # Overall system health based on task statuses
    has_errors = any(t["status"] == "ERROR" for t in task_statuses.values())
    has_degraded = any(t["status"] == "DEGRADED" for t in task_statuses.values())
    
    system_status = "ok"
    if has_errors:
        system_status = "degraded"
    elif has_degraded:
        system_status = "warning"
    
    return {
        "status": system_status,
        "preset_default": "equal",
        "cors_origins": [origin.strip() for origin in settings.cors_origins.split(",")],
        "time": datetime.utcnow().isoformat() + "Z",
        "tasks": task_statuses,
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


@app.get("/v1/signposts/by-code/{code}/events")
async def get_signpost_events_by_code(
    code: str,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """Get recent events linked to a signpost (grouped by tier)."""
    signpost = db.query(Signpost).filter(Signpost.code == code).first()
    if not signpost:
        raise HTTPException(status_code=404, detail="Signpost not found")

    # Get latest links for this signpost
    links = (
        db.query(EventSignpostLink)
        .filter(EventSignpostLink.signpost_id == signpost.id)
        .order_by(desc(EventSignpostLink.observed_at))
        .limit(100)
        .all()
    )

    # Fetch corresponding events
    events_by_tier = {"A": [], "B": [], "C": [], "D": []}
    for link in links:
        event = db.query(Event).filter(Event.id == link.event_id).first()
        if not event:
            continue
        item = {
            "id": event.id,
            "title": event.title,
            "summary": event.summary,
            "url": event.source_url,
            "publisher": event.publisher,
            "date": event.published_at.isoformat() if event.published_at else None,
            "tier": event.evidence_tier,
            "provisional": event.provisional,
            "confidence": float(link.confidence) if link.confidence else None,
            "value": float(link.value) if link.value else None,
            "observed_at": link.observed_at.isoformat() if link.observed_at else None,
        }
        # Cap per-tier to limit (maintain order)
        tier_list = events_by_tier.get(event.evidence_tier, [])
        if len(tier_list) < limit:
            tier_list.append(item)
            events_by_tier[event.evidence_tier] = tier_list

    return {"signpost_code": code, "events": events_by_tier}

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
    """Get roadmap predictions for a signpost with status (ahead/on/behind)."""
    from app.metrics.roadmap_status import compute_status
    
    signpost = db.query(Signpost).filter(Signpost.code == code).first()
    
    if not signpost:
        raise HTTPException(status_code=404, detail="Signpost not found")
    
    predictions = db.query(RoadmapPrediction).filter(
        RoadmapPrediction.signpost_id == signpost.id
    ).all()
    
    # Get latest observed date for this signpost (from events or claims)
    latest_event_link = (
        db.query(EventSignpostLink)
        .filter(EventSignpostLink.signpost_id == signpost.id)
        .order_by(desc(EventSignpostLink.observed_at))
        .first()
    )
    observed_date = latest_event_link.observed_at.date() if latest_event_link and latest_event_link.observed_at else None
    
    results = []
    for pred in predictions:
        roadmap = db.query(Roadmap).filter(Roadmap.id == pred.roadmap_id).first()
        
        # Compute status if we have both dates
        status = None
        if pred.predicted_date and observed_date:
            status = compute_status(pred.predicted_date, observed_date, window_days=30)
        elif pred.predicted_date:
            status = "unobserved"
        
        results.append({
            "roadmap_name": roadmap.name if roadmap else None,
            "roadmap_slug": roadmap.slug if roadmap else None,
            "prediction_text": pred.prediction_text,
            "predicted_date": pred.predicted_date.isoformat() if pred.predicted_date else None,
            "confidence_level": pred.confidence_level,
            "source_page": pred.source_page,
            "notes": pred.notes,
            "status": status,
            "observed_date": observed_date.isoformat() if observed_date else None,
        })
    
    return {"predictions": results}


@app.get("/v1/signposts/by-code/{code}/events")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_signpost_events(
    request: Request,
    code: str,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get recent events mapped to this signpost, grouped by evidence tier.
    
    Returns last N events (default 10) with tier grouping.
    Policy: A/B tier events move gauges; C/D tier are "If true" only.
    """
    signpost = db.query(Signpost).filter(Signpost.code == code).first()
    
    if not signpost:
        raise HTTPException(status_code=404, detail="Signpost not found")
    
    # Get events linked to this signpost, ordered by published_at DESC
    event_links = (
        db.query(EventSignpostLink)
        .filter(EventSignpostLink.signpost_id == signpost.id)
        .join(Event)
        .order_by(desc(Event.published_at))
        .limit(limit)
        .all()
    )
    
    # Group by tier
    events_by_tier = {"A": [], "B": [], "C": [], "D": []}
    
    for link in event_links:
        event = db.query(Event).filter(Event.id == link.event_id).first()
        if not event:
            continue
        
        event_data = {
            "id": event.id,
            "title": event.title,
            "summary": event.summary,
            "source_url": event.source_url,
            "source_type": event.source_type,
            "publisher": event.publisher,
            "published_at": event.published_at.isoformat() if event.published_at else None,
            "evidence_tier": event.evidence_tier,
            "confidence": float(link.confidence) if link.confidence else None,
            "value": float(link.value) if link.value else None,
            "rationale": link.rationale,
            "moves_gauge": event.evidence_tier in ("A", "B"),  # Policy: only A/B move gauges
        }
        
        tier = event.evidence_tier
        if tier in events_by_tier:
            events_by_tier[tier].append(event_data)
    
    return {
        "signpost_code": code,
        "signpost_name": signpost.name,
        "total_events": len(event_links),
        "events_by_tier": events_by_tier,
        "policy_note": "A/B tier events can move gauges; C/D tier are 'If true' analysis only"
    }


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


@app.post("/v1/admin/retract")
async def retract_claim(
    claim_id: int,
    reason: str,
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Retract a claim (admin only). Requires X-API-Key header."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim.retracted:
        raise HTTPException(status_code=400, detail="Claim already retracted")
    
    claim.retracted = True
    
    # Create changelog entry
    changelog_entry = ChangelogEntry(
        type="retract",
        title=f"Retracted: {claim.title}",
        body=f"Claim #{claim_id} retracted: {reason}",
        claim_id=claim_id,
        reason=reason,
    )
    db.add(changelog_entry)
    db.commit()
    db.refresh(changelog_entry)
    
    return {
        "status": "success",
        "claim_id": claim_id,
        "changelog_id": changelog_entry.id,
        "retracted": True,
    }


@app.post("/v1/admin/recompute")
async def recompute_index(
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Trigger index recomputation and purge cache (admin only)."""
    from app.tasks.snap_index import compute_daily_snapshot
    
    try:
        result = compute_daily_snapshot()
        
        # Purge cache after recomputation
        try:
            await FastAPICache.clear()
            print("✓ Cache purged after recomputation")
        except Exception as cache_err:
            print(f"⚠️  Cache purge failed: {cache_err}")
        
        return {"status": "success", "result": result, "cache_purged": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recompute failed: {str(e)}")


# Events endpoints (v0.3)


@app.get("/v1/events")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def list_events(
    request: Request,
    tier: Optional[str] = Query(None, regex="^[ABCD]$"),
    outlet_cred: Optional[str] = Query(None, regex="^[ABCD]$"),
    source_tier: Optional[str] = Query(None, regex="^[ABCD]$"),
    source_type: Optional[str] = Query(None, regex="^(news|paper|blog|leaderboard|gov)$"),
    signpost_id: Optional[int] = None,
    signpost_code: Optional[str] = None,
    alias: Optional[str] = None,
    needs_review: Optional[bool] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    min_confidence: Optional[float] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    List news events with optional filtering.
    
    Query params:
    - tier: Filter by evidence tier (A/B/C/D)
    - signpost_id: Filter by linked signpost
    - needs_review: Filter by review status
    - skip: Pagination offset
    - limit: Page size (max 100)
    """
    limit = min(limit, 100)

    query = query_active_events(db.query(Event))
    
    # Filter out synthetic events by default (can be overridden with include_synthetic param)
    # Evidence tier (aliases: outlet_cred, source_tier)
    effective_tier = tier or outlet_cred or source_tier
    if effective_tier:
        query = query.filter(Event.evidence_tier == effective_tier)

    # Source type filter
    if source_type:
        query = query.filter(Event.source_type == source_type)

    # Signpost filters
    if signpost_id:
        event_ids = (
            db.query(EventSignpostLink.event_id)
            .filter(EventSignpostLink.signpost_id == signpost_id)
            .all()
        )
        event_ids = [e[0] for e in event_ids]
        if event_ids:
            query = query.filter(Event.id.in_(event_ids))
        else:
            # No matches possible
            return {"total": 0, "skip": skip, "limit": limit, "results": [], "items": []}

    # Join to links/signposts if we need to filter on signpost_code, alias, or min_confidence
    if signpost_code or alias or (min_confidence is not None):
        query = (
            query.join(EventSignpostLink, EventSignpostLink.event_id == Event.id)
            .join(Signpost, Signpost.id == EventSignpostLink.signpost_id)
        )
        if signpost_code:
            query = query.filter(Signpost.code == signpost_code)
        if alias:
            like = f"%{alias.lower()}%"
            query = query.filter(or_(func.lower(Signpost.code).like(like), func.lower(Signpost.name).like(like)))
        if min_confidence is not None:
            try:
                mc = float(min_confidence)
            except Exception:
                mc = 0.0
            query = query.filter(EventSignpostLink.confidence >= mc)

    # Needs review filter
    if needs_review is not None:
        query = query.filter(Event.needs_review == needs_review)

    # Date range filters (on published_at). Support start_date/end_date and since/until synonyms.
    if start_date or since:
        try:
            start_dt = datetime.strptime((start_date or since), "%Y-%m-%d")
            query = query.filter(Event.published_at >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date. Use YYYY-MM-DD")

    if end_date or until:
        try:
            end_dt = datetime.strptime((end_date or until), "%Y-%m-%d")
            query = query.filter(Event.published_at <= end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date. Use YYYY-MM-DD")

    events = query.order_by(desc(Event.published_at)).offset(skip).limit(limit).all()
    
    # Server-side de-dup: prefer source_url if present; otherwise title+date key
    seen_keys = set()
    results = []
    for event in events:
        # Get linked signposts
        links = (
            db.query(EventSignpostLink)
            .filter(EventSignpostLink.event_id == event.id)
            .all()
        )
        signpost_links = []
        for link in links:
            signpost = db.query(Signpost).filter(Signpost.id == link.signpost_id).first()
            if signpost:
                signpost_links.append({
                    "signpost_id": signpost.id,
                    "signpost_code": signpost.code,
                    "signpost_name": signpost.name,
                    # alias for web UI
                    "signpost_title": signpost.name,
                    "confidence": float(link.confidence) if link.confidence else None,
                    "value": float(link.value) if link.value else None,
                })
        # Build dedup key
        if event.source_url:
            key = ("url", event.source_url)
        else:
            title_norm = (event.title or "").lower()
            title_norm = "".join(c for c in title_norm if c.isalnum() or c.isspace()).strip()
            date_key = event.published_at.date().isoformat() if event.published_at else ""
            key = ("td", f"{title_norm}|{date_key}")
        if key in seen_keys:
            continue
        seen_keys.add(key)

        results.append({
            "id": event.id,
            "title": event.title,
            "summary": event.summary,
            "source_url": event.source_url,
            "publisher": event.publisher,
            "published_at": event.published_at.isoformat() if event.published_at else None,
            # aliases for web UI compatibility
            "date": event.published_at.isoformat() if event.published_at else None,
            "evidence_tier": event.evidence_tier,
            "tier": event.evidence_tier,
            "source_type": event.source_type,
            "provisional": event.provisional,
            "needs_review": event.needs_review,
            "signpost_links": signpost_links,
        })
    # Include both results and items keys for compatibility with existing web code
    return {"total": len(results), "skip": skip, "limit": limit, "results": results, "items": results}


@app.get("/v1/events/{event_id}")
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get detailed event information with signpost links, entities, and forecast comparison."""
    from app.services.forecast_comparison import get_forecast_comparison_for_event_link
    
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Get signpost links
    links = (
        db.query(EventSignpostLink)
        .filter(EventSignpostLink.event_id == event.id)
        .all()
    )
    signpost_links = []
    for link in links:
        signpost = db.query(Signpost).filter(Signpost.id == link.signpost_id).first()
        if signpost:
            # Get forecast comparison for this link
            forecast_comp = get_forecast_comparison_for_event_link(event.id, signpost.id, db)
            
            signpost_links.append({
                "signpost_id": signpost.id,
                "signpost_code": signpost.code,
                "signpost_name": signpost.name,
                "category": signpost.category,
                "confidence": float(link.confidence) if link.confidence else None,
                "rationale": link.rationale,
                "value": float(link.value) if link.value else None,
                "observed_at": link.observed_at.isoformat() if link.observed_at else None,
                "forecast_comparison": forecast_comp if forecast_comp else None,
            })
    
    # Get entities
    entities = (
        db.query(EventEntity)
        .filter(EventEntity.event_id == event.id)
        .all()
    )
    entity_list = [{"type": e.type, "value": e.value} for e in entities]
    
    return {
        "id": event.id,
        "title": event.title,
        "summary": event.summary,
        "source_url": event.source_url,
        "publisher": event.publisher,
        "published_at": event.published_at.isoformat() if event.published_at else None,
        "ingested_at": event.ingested_at.isoformat(),
        "evidence_tier": event.evidence_tier,
        "provisional": event.provisional,
        "needs_review": event.needs_review,
        "parsed": event.parsed,
        "signpost_links": signpost_links,
        "entities": entity_list,
    }


@app.get("/v1/events/{event_id}/analysis")
async def get_event_analysis(event_id: int, db: Session = Depends(get_db)):
    """
    Get LLM-generated analysis for an event (Phase 1).
    
    Returns latest analysis if available, 404 if not found.
    """
    # Verify event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Get latest analysis for this event
    analysis = (
        db.query(EventAnalysis)
        .filter(EventAnalysis.event_id == event_id)
        .order_by(desc(EventAnalysis.generated_at))
        .first()
    )
    
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis available for this event")
    
    return {
        "event_id": event.id,
        "summary": analysis.summary,
        "relevance_explanation": analysis.relevance_explanation,
        "impact_json": analysis.impact_json,
        "confidence_reasoning": analysis.confidence_reasoning,
        "significance_score": float(analysis.significance_score) if analysis.significance_score else None,
        "llm_version": analysis.llm_version,
        "generated_at": analysis.generated_at.isoformat(),
    }


@app.get("/v1/events/feed.json")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
@cache(expire=settings.feed_cache_ttl_seconds)
async def events_feed(
    request: Request,
    audience: str = Query("public", regex="^(public|research)$"),
    include_research: Optional[bool] = Query(None, description="Alias for research audience"),
    db: Session = Depends(get_db),
):
    """
    JSON feed of news events (public or research audience).
    
    Query params:
    - audience: 'public' (A/B tier only) or 'research' (A/B/C/D all tiers)
    
    Public mode: Safe for general consumption, A/B tier only
    Research mode: Includes C/D tier with clear tier labels
    """
    # Support legacy/include_research alias used by web anchors
    if include_research is True:
        audience = "research"

    if audience == "public":
        # Public: Only A/B tier (verified sources)
        query = query_active_events(db.query(Event)).filter(Event.evidence_tier.in_(["A", "B"]))
    else:
        # Research: All tiers (A/B/C/D)
        query = query_active_events(db.query(Event))
    
    # Order by published date
    events = query.order_by(desc(Event.published_at)).limit(100).all()
    
    feed_items = []
    for event in events:
        # Get linked signposts
        links = (
            db.query(EventSignpostLink)
            .filter(EventSignpostLink.event_id == event.id)
            .all()
        )
        
        signposts = []
        for link in links:
            signpost = db.query(Signpost).filter(Signpost.id == link.signpost_id).first()
            if signpost:
                signposts.append({
                    "code": signpost.code,
                    "confidence": float(link.confidence) if link.confidence else None,
                })
        
        feed_items.append({
            "title": event.title,
            "summary": event.summary,
            "url": event.source_url,
            "publisher": event.publisher,
            "date": event.published_at.isoformat() if event.published_at else None,
            "tier": event.evidence_tier,
            "provisional": event.provisional,
            "signposts": signposts,
        })
    
    return {
        "version": "1.0",
        "license": "CC BY 4.0",
        "audience": audience,
        "generated_at": datetime.utcnow().isoformat(),
        "policy": (
            "A/B tier: verified sources (A moves gauges directly, B provisional)."
            if audience == "public"
            else "All tiers included. C/D tier: displayed but NEVER moves gauges."
        ),
        "items": feed_items,
    }


@app.get("/v1/roadmaps/compare")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
@cache(expire=settings.index_cache_ttl_seconds)
async def roadmaps_compare(request: Request, db: Session = Depends(get_db)):
    """
    Compare all signposts against roadmap predictions.
    
    Returns:
        List of signposts with current values and forecast comparisons
        showing ahead/on_track/behind status for each roadmap.
    """
    from app.services.forecast_comparison import get_all_forecast_comparisons
    
    comparisons = get_all_forecast_comparisons(db)
    
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "signposts": comparisons,
    }


# Admin review endpoints for events


@app.get("/v1/events/links")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def list_event_links(
    request: Request,
    approved_only: bool = Query(True, description="Filter to approved links only"),
    signpost_code: Optional[str] = None,
    min_confidence: Optional[float] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    List event-signpost links with filtering.
    
    Query params:
    - approved_only: Filter to approved links (default: true)
    - signpost_code: Filter by signpost
    - min_confidence: Minimum confidence threshold
    - skip/limit: Pagination
    """
    limit = min(limit, 100)
    query = db.query(EventSignpostLink)
    
    if approved_only:
        query = query.filter(EventSignpostLink.approved_at.isnot(None))
    
    if signpost_code:
        signpost = db.query(Signpost).filter(Signpost.code == signpost_code).first()
        if signpost:
            query = query.filter(EventSignpostLink.signpost_id == signpost.id)
    
    if min_confidence is not None:
        query = query.filter(EventSignpostLink.confidence >= min_confidence)
    
    total = query.count()
    links = query.order_by(desc(EventSignpostLink.observed_at)).offset(skip).limit(limit).all()
    
    results = []
    for link in links:
        event = db.query(Event).filter(Event.id == link.event_id).first()
        signpost = db.query(Signpost).filter(Signpost.id == link.signpost_id).first()
        if event and signpost:
            results.append({
                "event_id": event.id,
                "event_title": event.title,
                "signpost_code": signpost.code,
                "signpost_name": signpost.name,
                "confidence": float(link.confidence) if link.confidence else None,
                "value": float(link.value) if link.value else None,
                "observed_at": link.observed_at.isoformat() if link.observed_at else None,
                "approved_at": link.approved_at.isoformat() if link.approved_at else None,
                "approved_by": link.approved_by,
            })
    
    return {"total": total, "skip": skip, "limit": limit, "results": results}


@app.post("/v1/admin/events/{event_id}/approve")
async def approve_event_mapping(
    event_id: int,
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Approve event signpost mappings (admin only).
    Sets needs_review=False and marks links as approved. Requires X-API-Key header.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.needs_review = False
    
    # Mark all links as approved with timestamp
    links = db.query(EventSignpostLink).filter(EventSignpostLink.event_id == event_id).all()
    approved_count = 0
    for link in links:
        if link.approved_at is None:
            link.approved_at = datetime.utcnow()
            link.approved_by = "admin"
            approved_count += 1
    
    db.commit()
    
    return {
        "status": "success",
        "event_id": event_id,
        "needs_review": False,
        "links_approved": approved_count,
        "message": f"Event approved with {approved_count} link(s)",
    }


@app.post("/v1/admin/events/{event_id}/reject")
async def reject_event_mapping(
    event_id: int,
    reason: str = Query(..., min_length=1),
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Reject event signpost mappings (admin only).
    Removes all signpost links and marks for review. Requires X-API-Key header.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Count links before deletion for audit
    links_count = db.query(EventSignpostLink).filter(EventSignpostLink.event_id == event_id).count()
    
    # Delete all signpost links
    db.query(EventSignpostLink).filter(EventSignpostLink.event_id == event_id).delete()
    
    # Mark as needs review with reason
    event.needs_review = True
    event.parsed = {
        **(event.parsed or {}),
        "rejected_at": datetime.utcnow().isoformat(),
        "rejection_reason": reason,
        "links_removed": links_count,
    }
    
    # Create changelog entry
    changelog_entry = ChangelogEntry(
        type="update",
        title=f"Event #{event_id} mappings rejected",
        body=f"Removed {links_count} link(s). Reason: {reason}",
        reason=reason,
    )
    db.add(changelog_entry)
    
    db.commit()
    
    return {
        "status": "success",
        "event_id": event_id,
        "needs_review": True,
        "links_removed": links_count,
        "message": f"Event mappings rejected: {reason}",
    }


@app.get("/v1/digests/latest")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_latest_digest(request: Request):
    """
    Get latest weekly digest JSON (CC BY 4.0).
    
    Returns most recent digest from public/digests/*.json or generates on-the-fly.
    """
    from pathlib import Path
    
    digest_dir = Path(__file__).parent.parent.parent.parent / "public" / "digests"
    
    if digest_dir.exists():
        # Find latest digest JSON
        json_files = sorted(digest_dir.glob("*.json"), reverse=True)
        if json_files:
            with open(json_files[0]) as f:
                return json.load(f)
    
    # No digest found, return empty placeholder
    return {
        "version": "1.0",
        "week": "N/A",
        "generated_at": datetime.utcnow().isoformat(),
        "license": "CC BY 4.0",
        "ab_events": [],
        "cd_if_true": [],
        "message": "No digest generated yet. Run scripts/generate_digest.py to create."
    }


@app.post("/v1/recompute")
async def recompute_deprecated():
    """Deprecated: Moved to /v1/admin/recompute."""
    return Response(
        status_code=410,
        content=json.dumps({"error": "Endpoint moved to /v1/admin/recompute"}),
        media_type="application/json"
    )


# Phase 2/3 Stub Endpoints (not yet implemented)

@app.get("/v1/roadmaps/{roadmap_id}/tracking")
async def get_roadmap_tracking(roadmap_id: int):
    """
    Get roadmap tracking data comparing predictions vs actual progress.
    
    TODO(Phase 3): Implement forecast comparison logic
    """
    return {"todo": True, "message": "Phase 3: Not yet implemented"}


@app.get("/v1/review/queue")
async def get_review_queue(
    tier: Optional[str] = Query(None, regex="^[ABCD]$"),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
):
    """
    Get queue of events/mappings pending human review.
    
    TODO(Phase 2): Implement review queue with prioritization
    """
    from app.models import Event, EventSignpostLink, EventAnalysis, Signpost
    
    try:
        # Get events that need review (only active events)
        events_query = query_active_events(db.query(Event)).filter(Event.needs_review == True)
        if tier:
            events_query = events_query.filter(Event.evidence_tier == tier)
        
        events = events_query.order_by(Event.published_at.desc()).limit(limit).all()
        
        result = []
        for event in events:
            # Get signpost links
            links = db.query(EventSignpostLink).filter(
                EventSignpostLink.event_id == event.id
            ).all()
            
            # Get analysis if available
            analysis = db.query(EventAnalysis).filter(
                EventAnalysis.event_id == event.id
            ).order_by(EventAnalysis.generated_at.desc()).first()
            
            result.append({
                "type": "event",
                "id": event.id,
                "title": event.title,
                "summary": event.summary,
                "publisher": event.publisher,
                "evidence_tier": event.evidence_tier,
                "published_at": event.published_at,
                "needs_review": event.needs_review,
                "signpost_links": [
                    {
                        "id": link.id,
                        "signpost_id": link.signpost_id,
                        "confidence": link.confidence,
                        "rationale": link.rationale,
                        "needs_review": link.needs_review,
                        "link_type": link.link_type
                    }
                    for link in links
                ],
                "analysis": {
                    "summary": analysis.summary if analysis else None,
                    "significance_score": analysis.significance_score if analysis else None,
                    "confidence": analysis.confidence_reasoning if analysis else None
                } if analysis else None
            })
        
        # Get counts for pagination (only active events)
        total_events = query_active_events(db.query(Event)).filter(Event.needs_review == True).count()
        total_mappings = db.query(EventSignpostLink).filter(EventSignpostLink.needs_review == True).count()
        
        return {
            "items": result,
            "total": total_events + total_mappings,
            "total_events": total_events,
            "total_mappings": total_mappings
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching review queue: {str(e)}")


@app.post("/v1/review/submit")
async def submit_review(
    event_id: int,
    action: str = Query(..., regex="^(approve|reject|flag)$"),
    reason: Optional[str] = None,
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Submit human review decision for an event or mapping.
    
    TODO(Phase 2): Implement review workflow with audit trail
    """
    from app.models import Event, EventSignpostLink
    from datetime import datetime, timezone
    
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
        
        if action == "approve":
            # Mark event as reviewed and approved
            event.needs_review = False
            event.reviewed_at = datetime.now(timezone.utc)
            event.review_status = "approved"
            
            # Also approve all signpost links for this event
            links = db.query(EventSignpostLink).filter(EventSignpostLink.event_id == event_id).all()
            for link in links:
                link.needs_review = False
                link.reviewed_at = datetime.now(timezone.utc)
                link.review_status = "approved"
            
            db.commit()
            
            return {
                "status": "approved",
                "event_id": event_id,
                "message": f"Event {event_id} and {len(links)} mappings approved",
                "reviewed_at": event.reviewed_at
            }
            
        elif action == "reject":
            # Mark event as reviewed but rejected
            event.needs_review = False
            event.reviewed_at = datetime.now(timezone.utc)
            event.review_status = "rejected"
            event.rejection_reason = reason
            
            # Also reject all signpost links for this event
            links = db.query(EventSignpostLink).filter(EventSignpostLink.event_id == event_id).all()
            for link in links:
                link.needs_review = False
                link.reviewed_at = datetime.now(timezone.utc)
                link.review_status = "rejected"
                link.rejection_reason = reason
            
            db.commit()
            
            return {
                "status": "rejected",
                "event_id": event_id,
                "message": f"Event {event_id} and {len(links)} mappings rejected",
                "reason": reason,
                "reviewed_at": event.reviewed_at
            }
            
        elif action == "flag":
            # Flag for additional review
            event.needs_review = True
            event.flag_reason = reason
            
            db.commit()
            
            return {
                "status": "flagged",
                "event_id": event_id,
                "message": f"Event {event_id} flagged for additional review",
                "reason": reason
            }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing review: {str(e)}")


@app.get("/v1/predictions", tags=["predictions"])
async def get_predictions(
    signpost_id: Optional[int] = Query(None),
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500),
):
    """
    Get expert predictions for signposts.
    """
    from app.models import ExpertPrediction, Signpost
    
    try:
        query = db.query(ExpertPrediction)
        
        if signpost_id:
            query = query.filter(ExpertPrediction.signpost_id == signpost_id)
        
        if source:
            query = query.filter(ExpertPrediction.source.ilike(f"%{source}%"))
        
        predictions = query.order_by(ExpertPrediction.predicted_date.asc()).limit(limit).all()
        
        result = []
        for pred in predictions:
            signpost = db.query(Signpost).filter(Signpost.id == pred.signpost_id).first()
            result.append({
                "id": pred.id,
                "source": pred.source,
                "signpost_id": pred.signpost_id,
                "signpost_code": signpost.code if signpost else None,
                "signpost_name": signpost.name if signpost else None,
                "predicted_date": pred.predicted_date,
                "predicted_value": float(pred.predicted_value) if pred.predicted_value else None,
                "confidence_lower": float(pred.confidence_lower) if pred.confidence_lower else None,
                "confidence_upper": float(pred.confidence_upper) if pred.confidence_upper else None,
                "rationale": pred.rationale,
                "added_at": pred.added_at
            })
        
        return {
            "predictions": result,
            "total": len(result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching predictions: {str(e)}")


@app.get("/v1/predictions/compare", tags=["predictions"])
async def compare_predictions_vs_actual(
    signpost_id: Optional[int] = Query(None),
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Compare expert predictions vs actual progress for signposts.
    """
    from app.models import ExpertPrediction, Signpost, EventSignpostLink
    from sqlalchemy import func
    
    try:
        # Get predictions
        query = db.query(ExpertPrediction)
        if signpost_id:
            query = query.filter(ExpertPrediction.signpost_id == signpost_id)
        if source:
            query = query.filter(ExpertPrediction.source.ilike(f"%{source}%"))
        
        predictions = query.all()
        
        result = []
        for pred in predictions:
            signpost = db.query(Signpost).filter(Signpost.id == pred.signpost_id).first()
            if not signpost:
                continue
            
            # Get actual progress from events
            actual_links = db.query(EventSignpostLink).filter(
                EventSignpostLink.signpost_id == pred.signpost_id
            ).all()
            
            if actual_links:
                # Calculate current progress
                latest_link = max(actual_links, key=lambda x: x.created_at)
                current_progress = float(latest_link.impact_estimate) if latest_link.impact_estimate else 0.0
                
                # Calculate days ahead/behind if we have a predicted date
                days_status = None
                if pred.predicted_date:
                    from datetime import date
                    today = date.today()
                    if pred.predicted_date >= today:
                        days_status = f"{(pred.predicted_date - today).days} days ahead"
                    else:
                        days_status = f"{(today - pred.predicted_date).days} days behind"
            else:
                current_progress = 0.0
                days_status = "No data"
            
            result.append({
                "prediction_id": pred.id,
                "source": pred.source,
                "signpost_code": signpost.code,
                "signpost_name": signpost.name,
                "predicted_date": pred.predicted_date,
                "predicted_value": float(pred.predicted_value) if pred.predicted_value else None,
                "confidence_lower": float(pred.confidence_lower) if pred.confidence_lower else None,
                "confidence_upper": float(pred.confidence_upper) if pred.confidence_upper else None,
                "current_progress": current_progress,
                "days_status": days_status,
                "rationale": pred.rationale
            })
        
        return {
            "comparisons": result,
            "total": len(result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing predictions: {str(e)}")


@app.get("/v1/predictions/surprise-score", tags=["predictions"])
async def calculate_surprise_scores(
    db: Session = Depends(get_db),
):
    """
    Calculate surprise scores for recent events vs expert predictions.
    """
    from app.models import ExpertPrediction, Event, EventSignpostLink
    from sqlalchemy import func, desc
    
    try:
        # Get recent active events with signpost links
        recent_events = query_active_events(db.query(Event)).join(EventSignpostLink).filter(
            Event.published_at >= func.now() - func.interval('30 days')
        ).order_by(desc(Event.published_at)).limit(20).all()
        
        surprise_scores = []
        for event in recent_events:
            event_links = db.query(EventSignpostLink).filter(
                EventSignpostLink.event_id == event.id
            ).all()
            
            for link in event_links:
                # Get predictions for this signpost
                predictions = db.query(ExpertPrediction).filter(
                    ExpertPrediction.signpost_id == link.signpost_id
                ).all()
                
                if predictions:
                    # Calculate average surprise score
                    total_surprise = 0.0
                    prediction_count = 0
                    
                    for pred in predictions:
                        if pred.predicted_date and event.published_at:
                            # Calculate how surprising this timing was
                            days_diff = abs((event.published_at.date() - pred.predicted_date).days)
                            surprise_score = min(days_diff / 365.0, 1.0)  # Normalize to 0-1
                            total_surprise += surprise_score
                            prediction_count += 1
                    
                    if prediction_count > 0:
                        avg_surprise = total_surprise / prediction_count
                        surprise_scores.append({
                            "event_id": event.id,
                            "event_title": event.title,
                            "signpost_id": link.signpost_id,
                            "surprise_score": avg_surprise,
                            "confidence": float(link.confidence),
                            "published_at": event.published_at
                        })
        
        # Sort by surprise score (most surprising first)
        surprise_scores.sort(key=lambda x: x["surprise_score"], reverse=True)
        
        return {
            "surprise_scores": surprise_scores[:10],  # Top 10 most surprising
            "total_analyzed": len(surprise_scores)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating surprise scores: {str(e)}")


@app.post("/v1/admin/retract", tags=["admin"])
async def retract_event(
    event_id: int,
    reason: str,
    evidence_url: Optional[str] = None,
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Retract an event with reason and evidence.
    
    This marks an event as retracted, records the reason and evidence,
    and triggers recomputation of affected metrics.
    """
    from app.models import Event, EventSignpostLink
    from app.utils.cache import invalidate_signpost_caches
    from datetime import datetime, timezone
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
        
        if event.retracted:
            # Idempotent: return success if already retracted
            return {
                "status": "already_retracted",
                "event_id": event_id,
                "retracted_at": event.retracted_at.isoformat() if event.retracted_at else None,
                "reason": event.retraction_reason,
                "evidence_url": event.retraction_evidence_url,
                "message": f"Event {event_id} was already retracted."
            }
        
        # Mark event as retracted
        event.retracted = True
        event.retracted_at = datetime.now(timezone.utc)
        event.retraction_reason = reason
        event.retraction_evidence_url = evidence_url
        
        # Get affected signposts for recomputation
        affected_signposts = db.query(EventSignpostLink).filter(
            EventSignpostLink.event_id == event_id
        ).all()
        
        affected_signpost_ids = [link.signpost_id for link in affected_signposts]
        
        # Create changelog entry
        changelog = ChangelogEntry(
            type="retract",
            title=f"Event #{event_id} retracted",
            body=f"Event '{event.title}' retracted. Reason: {reason}",
            reason=reason,
        )
        db.add(changelog)
        
        db.commit()
        
        # Invalidate caches for affected signposts
        cache_count = await invalidate_signpost_caches(affected_signpost_ids)
        
        # Log retraction for audit trail
        logger.info(
            "event_retracted",
            event_id=event_id,
            publisher=event.publisher,
            reason=reason,
            evidence_url=evidence_url,
            affected_signposts=len(affected_signpost_ids),
            caches_invalidated=cache_count
        )
        
        return {
            "status": "retracted",
            "event_id": event_id,
            "retracted_at": event.retracted_at.isoformat() if event.retracted_at else None,
            "reason": reason,
            "evidence_url": evidence_url,
            "affected_signposts": affected_signpost_ids,
            "caches_invalidated": cache_count,
            "message": f"Event {event_id} retracted successfully. {len(affected_signpost_ids)} signposts affected, {cache_count} caches invalidated."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("retraction_failed", event_id=event_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error retracting event: {str(e)}")


@app.get("/v1/admin/source-credibility", tags=["admin"])
async def get_source_credibility(
    min_volume: int = Query(5, description="Minimum articles to include"),
    exclude_d_tier: bool = Query(True, description="Exclude D-tier sources"),
    db: Session = Depends(get_db),
):
    """
    Get credibility scores for all sources using Wilson score interval.
    
    Uses Wilson score lower bound for conservative credibility estimates
    that account for sample size uncertainty. Small-volume publishers get
    appropriately wide confidence intervals.
    
    Query params:
    - min_volume: Minimum articles required (default 5)
    - exclude_d_tier: Whether to exclude D-tier sources (default true)
    """
    from app.models import Event
    from app.utils.statistics import wilson_lower_bound, credibility_tier
    from sqlalchemy import func, case
    
    try:
        # Calculate retraction stats per publisher (only non-D-tier events)
        query = db.query(
            Event.publisher,
            func.count(Event.id).label('total_events'),
            func.sum(case((Event.retracted == True, 1), else_=0)).label('retracted_count')
        )
        
        # Exclude D-tier sources from input if requested
        if exclude_d_tier:
            query = query.filter(Event.evidence_tier.in_(["A", "B", "C"]))
        
        results = query.group_by(Event.publisher).all()
        
        credibility_scores = []
        for row in results:
            if not row.publisher or row.total_events < min_volume:
                continue
            
            retracted = row.retracted_count or 0
            total = row.total_events
            successes = total - retracted  # Non-retracted articles
            
            # Wilson score lower bound (conservative estimate)
            wilson_score = wilson_lower_bound(successes, total, confidence=0.95)
            
            # Determine tier based on Wilson score and volume
            tier = credibility_tier(wilson_score, total)
            
            # Raw retraction rate for comparison
            retraction_rate = retracted / total if total > 0 else 0.0
            
            credibility_scores.append({
                "publisher": row.publisher,
                "total_articles": total,
                "retracted_count": retracted,
                "retraction_rate": round(retraction_rate * 100, 2),
                "credibility_score": round(wilson_score, 3),
                "credibility_tier": tier,
                "methodology": "wilson_95ci_lower"
            })
        
        # Sort by credibility score descending
        credibility_scores.sort(key=lambda x: x["credibility_score"], reverse=True)
        
        return {
            "sources": credibility_scores,
            "total_sources": len(credibility_scores),
            "min_volume": min_volume,
            "methodology": "Wilson score 95% confidence interval (lower bound)",
            "note": "Lower scores for low-volume publishers reflect statistical uncertainty"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating source credibility: {str(e)}")


@app.get("/v1/admin/source-credibility/history", tags=["admin"])
async def get_source_credibility_history(
    publisher: Optional[str] = Query(None, description="Filter by publisher"),
    days: int = Query(30, description="Number of days of history"),
    db: Session = Depends(get_db),
):
    """
    Get historical source credibility snapshots.
    
    Returns time-series data of publisher credibility scores.
    Useful for tracking reliability trends and identifying degradation.
    
    Query params:
    - publisher: Filter to specific publisher (optional)
    - days: Number of days to query (default 30)
    """
    from app.models import SourceCredibilitySnapshot
    from datetime import date, timedelta
    from sqlalchemy import desc
    
    try:
        cutoff_date = date.today() - timedelta(days=days)
        
        query = db.query(SourceCredibilitySnapshot).filter(
            SourceCredibilitySnapshot.snapshot_date >= cutoff_date
        )
        
        if publisher:
            query = query.filter(SourceCredibilitySnapshot.publisher == publisher)
        
        snapshots = query.order_by(
            SourceCredibilitySnapshot.publisher,
            desc(SourceCredibilitySnapshot.snapshot_date)
        ).all()
        
        # Format response
        history = []
        for snap in snapshots:
            history.append({
                "publisher": snap.publisher,
                "date": snap.snapshot_date.isoformat(),
                "total_articles": snap.total_articles,
                "retracted_count": snap.retracted_count,
                "retraction_rate": float(snap.retraction_rate),
                "credibility_score": float(snap.credibility_score),
                "credibility_tier": snap.credibility_tier,
                "methodology": snap.methodology
            })
        
        return {
            "history": history,
            "total_snapshots": len(history),
            "days": days,
            "publisher_filter": publisher
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching credibility history: {str(e)}")


# ============================================================================
# LLM Prompt Management Endpoints (Phase 5)
# ============================================================================

@app.get("/v1/admin/prompts", tags=["admin"])
async def list_prompts(
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    include_deprecated: bool = Query(False, description="Include deprecated prompts"),
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    List all LLM prompt templates with versioning info.
    
    Returns all prompts used for AI analysis with their metadata.
    Useful for auditing prompt changes and A/B testing.
    
    Query params:
    - task_type: Filter by task (e.g., "event_analysis", "event_mapping")
    - include_deprecated: Show deprecated prompts (default false)
    """
    from app.models import LLMPrompt
    from sqlalchemy import desc
    
    try:
        query = db.query(LLMPrompt)
        
        if task_type:
            query = query.filter(LLMPrompt.task_type == task_type)
        
        if not include_deprecated:
            query = query.filter(LLMPrompt.deprecated_at == None)
        
        prompts = query.order_by(
            LLMPrompt.task_type,
            desc(LLMPrompt.created_at)
        ).all()
        
        result = []
        for prompt in prompts:
            result.append({
                "id": prompt.id,
                "version": prompt.version,
                "task_type": prompt.task_type,
                "model": prompt.model,
                "temperature": float(prompt.temperature) if prompt.temperature else None,
                "max_tokens": prompt.max_tokens,
                "notes": prompt.notes,
                "created_at": prompt.created_at.isoformat(),
                "deprecated_at": prompt.deprecated_at.isoformat() if prompt.deprecated_at else None,
                "is_active": prompt.deprecated_at is None
            })
        
        return {
            "prompts": result,
            "total": len(result),
            "task_type_filter": task_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing prompts: {str(e)}")


@app.get("/v1/admin/prompts/{prompt_id}", tags=["admin"])
async def get_prompt_detail(
    prompt_id: int,
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Get full details of a specific prompt including template text.
    """
    from app.models import LLMPrompt
    
    try:
        prompt = db.query(LLMPrompt).filter(LLMPrompt.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail=f"Prompt {prompt_id} not found")
        
        return {
            "id": prompt.id,
            "version": prompt.version,
            "task_type": prompt.task_type,
            "prompt_template": prompt.prompt_template,
            "system_message": prompt.system_message,
            "model": prompt.model,
            "temperature": float(prompt.temperature) if prompt.temperature else None,
            "max_tokens": prompt.max_tokens,
            "notes": prompt.notes,
            "created_at": prompt.created_at.isoformat(),
            "deprecated_at": prompt.deprecated_at.isoformat() if prompt.deprecated_at else None,
            "is_active": prompt.deprecated_at is None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching prompt: {str(e)}")


@app.post("/v1/admin/prompts", tags=["admin"])
async def create_prompt(
    version: str,
    task_type: str,
    prompt_template: str,
    model: str,
    system_message: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    notes: Optional[str] = None,
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Create a new prompt template version.
    
    Body:
    - version: Unique version identifier (e.g., "event-analysis-v2")
    - task_type: Task name (e.g., "event_analysis", "event_mapping")
    - prompt_template: The actual prompt text
    - model: LLM model to use (e.g., "gpt-4o-mini")
    - system_message: Optional system message
    - temperature: Optional temperature setting
    - max_tokens: Optional max tokens
    - notes: Optional notes about this version
    """
    from app.models import LLMPrompt
    
    try:
        # Check if version already exists
        existing = db.query(LLMPrompt).filter(LLMPrompt.version == version).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Prompt version '{version}' already exists")
        
        prompt = LLMPrompt(
            version=version,
            task_type=task_type,
            prompt_template=prompt_template,
            system_message=system_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            notes=notes
        )
        
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        
        return {
            "status": "created",
            "id": prompt.id,
            "version": prompt.version,
            "task_type": prompt.task_type,
            "created_at": prompt.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating prompt: {str(e)}")


@app.post("/v1/admin/prompts/{prompt_id}/deprecate", tags=["admin"])
async def deprecate_prompt(
    prompt_id: int,
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Mark a prompt template as deprecated.
    
    Deprecated prompts are hidden from active use but retained for audit trail.
    """
    from app.models import LLMPrompt
    from datetime import datetime, timezone
    
    try:
        prompt = db.query(LLMPrompt).filter(LLMPrompt.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail=f"Prompt {prompt_id} not found")
        
        if prompt.deprecated_at:
            return {
                "status": "already_deprecated",
                "id": prompt_id,
                "version": prompt.version,
                "deprecated_at": prompt.deprecated_at.isoformat()
            }
        
        prompt.deprecated_at = datetime.now(timezone.utc)
        db.commit()
        
        return {
            "status": "deprecated",
            "id": prompt_id,
            "version": prompt.version,
            "deprecated_at": prompt.deprecated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deprecating prompt: {str(e)}")


@app.get("/v1/admin/prompt-runs", tags=["admin"])
async def list_prompt_runs(
    task_name: Optional[str] = Query(None, description="Filter by task name"),
    event_id: Optional[int] = Query(None, description="Filter by event ID"),
    days: int = Query(7, description="Days of history"),
    limit: int = Query(100, description="Max results"),
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    List LLM API call history with costs and token usage.
    
    Returns audit trail of all LLM calls for cost tracking and debugging.
    
    Query params:
    - task_name: Filter by task (e.g., "event_analysis")
    - event_id: Filter by specific event
    - days: Number of days of history (default 7)
    - limit: Max results to return (default 100)
    """
    from app.models import LLMPromptRun
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import desc
    
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        query = db.query(LLMPromptRun).filter(
            LLMPromptRun.created_at >= cutoff
        )
        
        if task_name:
            query = query.filter(LLMPromptRun.task_name == task_name)
        
        if event_id is not None:
            query = query.filter(LLMPromptRun.event_id == event_id)
        
        runs = query.order_by(desc(LLMPromptRun.created_at)).limit(limit).all()
        
        result = []
        total_cost = 0.0
        total_tokens = 0
        
        for run in runs:
            result.append({
                "id": run.id,
                "task_name": run.task_name,
                "event_id": run.event_id,
                "model": run.model,
                "prompt_tokens": run.prompt_tokens,
                "completion_tokens": run.completion_tokens,
                "total_tokens": run.total_tokens,
                "cost_usd": float(run.cost_usd),
                "success": run.success,
                "error_message": run.error_message,
                "created_at": run.created_at.isoformat()
            })
            
            total_cost += float(run.cost_usd)
            total_tokens += run.total_tokens
        
        return {
            "runs": result,
            "total_runs": len(result),
            "total_cost_usd": round(total_cost, 2),
            "total_tokens": total_tokens,
            "days": days,
            "task_name_filter": task_name,
            "event_id_filter": event_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing prompt runs: {str(e)}")


# ======================================================================
# REVIEW QUEUE ENDPOINTS (Phase 2)
# ======================================================================

@app.get("/v1/review-queue/mappings", tags=["review"])
def get_review_queue(
    needs_review_only: bool = True,
    min_confidence: Optional[float] = None,
    max_confidence: Optional[float] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get event-signpost mappings that need human review.
    
    Returns mappings with low confidence or flagged for review, sorted by confidence.
    """
    try:
        query = db.query(EventSignpostLink).join(Event).join(Signpost)
        
        if needs_review_only:
            query = query.filter(EventSignpostLink.needs_review == True)
        
        if min_confidence is not None:
            query = query.filter(EventSignpostLink.confidence >= min_confidence)
        
        if max_confidence is not None:
            query = query.filter(EventSignpostLink.confidence <= max_confidence)
        
        # Order by confidence (lowest first) and created_at (newest first)
        query = query.order_by(EventSignpostLink.confidence.asc(), EventSignpostLink.created_at.desc())
        
        total = query.count()
        links = query.limit(limit).offset(offset).all()
        
        result = []
        for link in links:
            event = db.query(Event).filter(Event.id == link.event_id).first()
            signpost = db.query(Signpost).filter(Signpost.id == link.signpost_id).first()
            
            result.append({
                "id": link.id,
                "event_id": link.event_id,
                "event_title": event.title if event else None,
                "event_summary": event.summary if event else None,
                "event_tier": event.evidence_tier if event else None,
                "signpost_id": link.signpost_id,
                "signpost_code": signpost.code if signpost else None,
                "signpost_name": signpost.name if signpost else None,
                "confidence": float(link.confidence) if link.confidence else None,
                "rationale": link.rationale,
                "impact_estimate": float(link.impact_estimate) if link.impact_estimate else None,
                "link_type": link.link_type,
                "needs_review": link.needs_review,
                "reviewed_at": link.reviewed_at.isoformat() if link.reviewed_at else None,
                "review_status": link.review_status,
                "created_at": link.created_at.isoformat() if link.created_at else None
            })
        
        return {
            "mappings": result,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching review queue: {str(e)}")


@app.post("/v1/review-queue/mappings/{mapping_id}/approve", tags=["review"])
def approve_mapping(
    mapping_id: int,
    db: Session = Depends(get_db),
    x_api_key: str = Header(None)
):
    """Approve a mapping (mark as reviewed and not needing review)."""
    try:
        # Verify API key for admin actions
        if not x_api_key or x_api_key != settings.api_key:
            raise HTTPException(status_code=403, detail="Invalid or missing API key")
        
        link = db.query(EventSignpostLink).filter(EventSignpostLink.id == mapping_id).first()
        if not link:
            raise HTTPException(status_code=404, detail="Mapping not found")
        
        link.needs_review = False
        link.reviewed_at = datetime.utcnow()
        link.review_status = "approved"
        
        db.commit()
        
        return {
            "message": "Mapping approved",
            "mapping_id": mapping_id,
            "reviewed_at": link.reviewed_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error approving mapping: {str(e)}")


@app.post("/v1/review-queue/mappings/{mapping_id}/reject", tags=["review"])
def reject_mapping(
    mapping_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    x_api_key: str = Header(None)
):
    """Reject a mapping (mark as reviewed and rejected)."""
    try:
        # Verify API key for admin actions
        if not x_api_key or x_api_key != settings.api_key:
            raise HTTPException(status_code=403, detail="Invalid or missing API key")
        
        link = db.query(EventSignpostLink).filter(EventSignpostLink.id == mapping_id).first()
        if not link:
            raise HTTPException(status_code=404, detail="Mapping not found")
        
        link.needs_review = False
        link.reviewed_at = datetime.utcnow()
        link.review_status = "rejected"
        link.rejection_reason = reason
        
        db.commit()
        
        return {
            "message": "Mapping rejected",
            "mapping_id": mapping_id,
            "reason": reason,
            "reviewed_at": link.reviewed_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error rejecting mapping: {str(e)}")


@app.get("/v1/review-queue/stats", tags=["review"])
def get_review_stats(db: Session = Depends(get_db)):
    """Get review queue statistics."""
    try:
        total_mappings = db.query(EventSignpostLink).count()
        needs_review = db.query(EventSignpostLink).filter(EventSignpostLink.needs_review == True).count()
        approved = db.query(EventSignpostLink).filter(EventSignpostLink.review_status == "approved").count()
        rejected = db.query(EventSignpostLink).filter(EventSignpostLink.review_status == "rejected").count()
        
        # Confidence distribution
        low_conf = db.query(EventSignpostLink).filter(EventSignpostLink.confidence < 0.5).count()
        med_conf = db.query(EventSignpostLink).filter(
            and_(EventSignpostLink.confidence >= 0.5, EventSignpostLink.confidence < 0.7)
        ).count()
        high_conf = db.query(EventSignpostLink).filter(EventSignpostLink.confidence >= 0.7).count()
        
        return {
            "total_mappings": total_mappings,
            "needs_review": needs_review,
            "approved": approved,
            "rejected": rejected,
            "pending_review": total_mappings - approved - rejected,
            "confidence_distribution": {
                "low": low_conf,  # < 0.5
                "medium": med_conf,  # 0.5-0.7
                "high": high_conf  # >= 0.7
            },
            "review_rate": round((approved + rejected) / total_mappings * 100, 2) if total_mappings > 0 else 0.0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching review stats: {str(e)}")

