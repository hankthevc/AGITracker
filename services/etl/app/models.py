"""SQLAlchemy ORM models mirroring the database schema."""
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Roadmap(Base):
    """Roadmap model."""
    
    __tablename__ = "roadmaps"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    preset_weights = Column(JSONB, nullable=True)
    author = Column(String(255), nullable=True)
    published_date = Column(Date, nullable=True)
    source_url = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    signposts = relationship("Signpost", back_populates="roadmap")
    predictions = relationship("RoadmapPrediction", back_populates="roadmap")
    pace_analyses = relationship("PaceAnalysis", back_populates="roadmap")


class Signpost(Base):
    """Signpost model."""
    
    __tablename__ = "signposts"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(20), nullable=False)
    metric_name = Column(String(100), nullable=True)
    unit = Column(String(50), nullable=True)
    direction = Column(String(5), nullable=False)
    baseline_value = Column(Numeric, nullable=True)
    target_value = Column(Numeric, nullable=True)
    methodology_url = Column(Text, nullable=True)
    first_class = Column(Boolean, default=False)
    short_explainer = Column(Text, nullable=True)
    icon_emoji = Column(String(10), nullable=True)
    embedding = Column(Vector(1536), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    roadmap = relationship("Roadmap", back_populates="signposts")
    claim_signposts = relationship("ClaimSignpost", back_populates="signpost")
    predictions = relationship("RoadmapPrediction", back_populates="signpost")
    content = relationship("SignpostContent", back_populates="signpost", uselist=False)
    pace_analyses = relationship("PaceAnalysis", back_populates="signpost")
    
    __table_args__ = (
        CheckConstraint(
            "category IN ('capabilities', 'agents', 'inputs', 'security')",
            name="check_signpost_category"
        ),
        CheckConstraint(
            "direction IN ('>=', '<=')",
            name="check_signpost_direction"
        ),
        Index("idx_signposts_category", "category"),
        Index("idx_signposts_first_class", "first_class"),
    )


class Benchmark(Base):
    """Benchmark model."""
    
    __tablename__ = "benchmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=True)
    family = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    claim_benchmarks = relationship("ClaimBenchmark", back_populates="benchmark")
    
    __table_args__ = (
        CheckConstraint(
            "family IN ('SWE_BENCH_VERIFIED', 'OSWORLD', 'WEBARENA', 'GPQA_DIAMOND', 'OTHER')",
            name="check_benchmark_family"
        ),
    )


class Source(Base):
    """Source model."""
    
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, unique=True, nullable=False)
    domain = Column(String(255), nullable=True)
    source_type = Column(String(50), nullable=False)
    credibility = Column(String(1), nullable=False)
    first_seen_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    claims = relationship("Claim", back_populates="source")
    
    __table_args__ = (
        CheckConstraint(
            "source_type IN ('paper', 'leaderboard', 'model_card', 'press', 'blog', 'social')",
            name="check_source_type"
        ),
        CheckConstraint(
            "credibility IN ('A', 'B', 'C', 'D')",
            name="check_credibility"
        ),
        Index("idx_sources_credibility", "credibility"),
    )


class Claim(Base):
    """Claim model."""
    
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=True)
    summary = Column(Text, nullable=True)
    metric_name = Column(String(100), nullable=True)
    metric_value = Column(Numeric, nullable=True)
    unit = Column(String(50), nullable=True)
    observed_at = Column(TIMESTAMP(timezone=True), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    url_hash = Column(String(64), unique=True, nullable=True)
    extraction_confidence = Column(Numeric, nullable=True)
    raw_json = Column(JSONB, nullable=True)
    retracted = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    source = relationship("Source", back_populates="claims")
    claim_benchmarks = relationship("ClaimBenchmark", back_populates="claim")
    claim_signposts = relationship("ClaimSignpost", back_populates="claim")
    changelogs = relationship("ChangelogEntry", back_populates="claim")
    
    __table_args__ = (
        Index("idx_claims_observed_at", "observed_at"),
        Index("idx_claims_retracted", "retracted"),
    )


class ClaimBenchmark(Base):
    """Many-to-many relationship between claims and benchmarks."""
    
    __tablename__ = "claim_benchmarks"
    
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="CASCADE"), primary_key=True)
    benchmark_id = Column(Integer, ForeignKey("benchmarks.id", ondelete="CASCADE"), primary_key=True)
    
    # Relationships
    claim = relationship("Claim", back_populates="claim_benchmarks")
    benchmark = relationship("Benchmark", back_populates="claim_benchmarks")


class ClaimSignpost(Base):
    """Many-to-many relationship between claims and signposts with mapping metadata."""
    
    __tablename__ = "claim_signposts"
    
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="CASCADE"), primary_key=True)
    signpost_id = Column(Integer, ForeignKey("signposts.id", ondelete="CASCADE"), primary_key=True)
    fit_score = Column(Numeric, nullable=True)
    impact_estimate = Column(Numeric, nullable=True)
    
    # Relationships
    claim = relationship("Claim", back_populates="claim_signposts")
    signpost = relationship("Signpost", back_populates="claim_signposts")


class IndexSnapshot(Base):
    """Index snapshot model."""
    
    __tablename__ = "index_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    as_of_date = Column(Date, unique=True, nullable=False)
    capabilities = Column(Numeric, nullable=True)
    agents = Column(Numeric, nullable=True)
    inputs = Column(Numeric, nullable=True)
    security = Column(Numeric, nullable=True)
    overall = Column(Numeric, nullable=True)
    safety_margin = Column(Numeric, nullable=True)
    preset = Column(String(50), default="equal")
    details = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class ChangelogEntry(Base):
    """Changelog entry model."""
    
    __tablename__ = "changelog"
    
    id = Column(Integer, primary_key=True, index=True)
    occurred_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    type = Column(String(20), nullable=False)
    title = Column(String(500), nullable=True)
    body = Column(Text, nullable=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    claim = relationship("Claim", back_populates="changelogs")
    
    __table_args__ = (
        CheckConstraint(
            "type IN ('add', 'update', 'retract')",
            name="check_changelog_type"
        ),
    )


class WeeklyDigest(Base):
    """Weekly digest model."""
    
    __tablename__ = "weekly_digest"
    
    id = Column(Integer, primary_key=True, index=True)
    week_start = Column(Date, unique=True, nullable=False)
    json = Column(JSONB, nullable=True)


class APIKey(Base):
    """API key model."""
    
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    hashed_key = Column(String(255), unique=True, nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'readonly')",
            name="check_api_key_role"
        ),
    )


class RoadmapPrediction(Base):
    """Roadmap prediction model for timeline predictions."""
    
    __tablename__ = "roadmap_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    signpost_id = Column(Integer, ForeignKey("signposts.id"), nullable=True)
    signpost_code = Column(String(100), nullable=True, index=True)  # For JSON-based predictions
    prediction_text = Column(Text, nullable=False)
    predicted_date = Column(Date, nullable=True)
    confidence_level = Column(String(20), nullable=False)
    source_page = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    roadmap = relationship("Roadmap", back_populates="predictions")
    signpost = relationship("Signpost", back_populates="predictions")
    
    __table_args__ = (
        CheckConstraint(
            "confidence_level IN ('high', 'medium', 'low')",
            name="check_confidence_level"
        ),
        Index("idx_roadmap_predictions_roadmap", "roadmap_id"),
        Index("idx_roadmap_predictions_signpost", "signpost_id"),
    )


class SignpostContent(Base):
    """Rich educational content for signposts."""
    
    __tablename__ = "signpost_content"
    
    id = Column(Integer, primary_key=True, index=True)
    signpost_id = Column(Integer, ForeignKey("signposts.id"), nullable=False, unique=True)
    why_matters = Column(Text, nullable=True)
    current_state = Column(Text, nullable=True)
    key_papers = Column(JSONB, nullable=True)
    key_announcements = Column(JSONB, nullable=True)
    technical_explanation = Column(Text, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    signpost = relationship("Signpost", back_populates="content")
    
    __table_args__ = (
        Index("idx_signpost_content_signpost", "signpost_id"),
    )


class PaceAnalysis(Base):
    """Human-written pace analysis comparing progress to roadmap predictions."""
    
    __tablename__ = "pace_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    signpost_id = Column(Integer, ForeignKey("signposts.id"), nullable=False)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    analysis_text = Column(Text, nullable=False)
    last_updated = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    signpost = relationship("Signpost", back_populates="pace_analyses")
    roadmap = relationship("Roadmap", back_populates="pace_analyses")
    
    __table_args__ = (
        Index("idx_pace_analysis_signpost", "signpost_id"),
        Index("idx_pace_analysis_roadmap", "roadmap_id"),
    )


class Event(Base):
    """
    News event model (v0.3).
    
    Stores AI news/announcements from various sources with evidence tiering.
    """
    
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    source_url = Column(Text, nullable=False, unique=True)  # URL is unique for idempotency
    source_domain = Column(String(255), nullable=True)
    source_type = Column(Enum("news", "paper", "blog", "leaderboard", "gov", name="source_type"), nullable=False, index=True)
    publisher = Column(String(255), nullable=True, index=True)
    published_at = Column(TIMESTAMP(timezone=True), nullable=True, index=True)
    ingested_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    evidence_tier = Column(Enum("A", "B", "C", "D", name="evidence_tier"), nullable=False, index=True)
    content_text = Column(Text, nullable=True)  # Full article content
    author = Column(String(255), nullable=True)
    byline = Column(String(500), nullable=True)
    lang = Column(String(10), nullable=False, server_default="en")
    retracted = Column(Boolean, nullable=False, server_default="false")
    provisional = Column(Boolean, nullable=False, server_default="true")
    parsed = Column(JSONB, nullable=True)  # Extracted fields (metric, value, etc.)
    needs_review = Column(Boolean, nullable=False, server_default="false", index=True)
    is_synthetic = Column(Boolean, nullable=False, server_default="false", index=True)  # Marks fixture/test data
    
    # Relationships
    signpost_links = relationship("EventSignpostLink", back_populates="event", cascade="all, delete-orphan")
    entities = relationship("EventEntity", back_populates="event", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint(
            "evidence_tier IN ('A', 'B', 'C', 'D')",
            name="check_evidence_tier"
        ),
        CheckConstraint(
            "source_type IN ('news', 'paper', 'blog', 'leaderboard', 'gov')",
            name="check_source_type"
        ),
    )


class EventSignpostLink(Base):
    """
    Link between events and signposts with confidence and extracted values.
    """
    
    __tablename__ = "event_signpost_links"
    
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    signpost_id = Column(Integer, ForeignKey("signposts.id", ondelete="CASCADE"), primary_key=True)
    confidence = Column(Numeric(3, 2), nullable=False)  # 0.00 to 1.00
    rationale = Column(Text, nullable=True)
    observed_at = Column(TIMESTAMP(timezone=True), nullable=True)  # Date claim refers to
    value = Column(Numeric, nullable=True)  # Extracted numeric value if applicable
    # approved_at = Column(TIMESTAMP(timezone=True), nullable=True)  # Migration 009 not applied yet
    # approved_by = Column(String(100), nullable=True)  # Migration 009 not applied yet
    
    # Relationships
    event = relationship("Event", back_populates="signpost_links")
    signpost = relationship("Signpost")
    
    __table_args__ = (
        Index("idx_event_signpost_signpost_observed", "signpost_id", "observed_at"),
    )


class EventEntity(Base):
    """
    Helper table for extracted entities from events (benchmarks, metrics, orgs).
    """
    
    __tablename__ = "event_entities"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(100), nullable=False)  # e.g., "benchmark", "metric", "org"
    value = Column(Text, nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="entities")


class IngestRun(Base):
    """
    Tracks ETL connector runs for monitoring and debugging.
    """
    
    __tablename__ = "ingest_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    connector_name = Column(String(100), nullable=False, index=True)
    started_at = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    finished_at = Column(TIMESTAMP(timezone=True), nullable=True)
    status = Column(Enum("success", "fail", "running", name="ingest_status"), nullable=False, index=True)
    new_events_count = Column(Integer, nullable=False, server_default="0")
    new_links_count = Column(Integer, nullable=False, server_default="0")
    error = Column(Text, nullable=True)

