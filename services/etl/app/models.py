"""SQLAlchemy ORM models mirroring the database schema."""

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
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=True, index=True)  # Added index
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(20), nullable=False)
    metric_name = Column(String(100), nullable=True)
    unit = Column(String(50), nullable=True)
    direction = Column(String(5), nullable=False)
    baseline_value = Column(Numeric(12, 4), nullable=True)  # Support large values like 1e26 FLOP
    target_value = Column(Numeric(12, 4), nullable=True)
    methodology_url = Column(Text, nullable=True)
    first_class = Column(Boolean, default=False)
    short_explainer = Column(Text, nullable=True)
    icon_emoji = Column(String(10), nullable=True)
    
    # Rich metadata (Migration 027)
    why_matters = Column(Text, nullable=True)
    strategic_importance = Column(Text, nullable=True)
    measurement_methodology = Column(Text, nullable=True)
    measurement_source = Column(Text, nullable=True)
    measurement_frequency = Column(Text, nullable=True)
    verification_tier = Column(String(10), nullable=True)
    
    # Current SOTA tracking
    current_sota_value = Column(Numeric(12, 4), nullable=True)
    current_sota_model = Column(String(255), nullable=True)
    current_sota_date = Column(Date, nullable=True)
    current_sota_source = Column(Text, nullable=True)
    
    # Expert forecasts - Aschenbrenner
    aschenbrenner_timeline = Column(Date, nullable=True)
    aschenbrenner_confidence = Column(Numeric(3, 2), nullable=True)
    aschenbrenner_quote = Column(Text, nullable=True)
    aschenbrenner_rationale = Column(Text, nullable=True)
    
    # Expert forecasts - AI 2027
    ai2027_timeline = Column(Date, nullable=True)
    ai2027_confidence = Column(Numeric(3, 2), nullable=True)
    ai2027_rationale = Column(Text, nullable=True)
    
    # Expert forecasts - Cotra
    cotra_timeline = Column(Date, nullable=True)
    cotra_confidence = Column(Numeric(3, 2), nullable=True)
    
    # Expert forecasts - Epoch AI
    epoch_timeline = Column(Date, nullable=True)
    epoch_confidence = Column(Numeric(3, 2), nullable=True)
    
    # Citation tracking
    primary_paper_title = Column(Text, nullable=True)
    primary_paper_url = Column(Text, nullable=True)
    primary_paper_authors = Column(Text, nullable=True)
    primary_paper_year = Column(Integer, nullable=True)
    
    # Related signposts
    related_signpost_codes = Column(Text, nullable=True)  # Comma-separated codes
    
    # UI/UX fields
    display_order = Column(Integer, nullable=True)
    
    # OpenAI o1 preparation
    openai_prep_confidence = Column(Numeric(3, 2), nullable=True)  # Migration 030

    # Relationships
    roadmap = relationship("Roadmap", back_populates="signposts")
    predictions = relationship("RoadmapPrediction", back_populates="signpost")
    content = relationship("SignpostContent", back_populates="signpost", uselist=False)
    pace_analyses = relationship("PaceAnalysis", back_populates="signpost")
    signpost_links = relationship("EventSignpostLink", back_populates="signpost")

    __table_args__ = (
        CheckConstraint(
            "category IN ('capabilities', 'agents', 'inputs', 'security', 'economic', 'research', 'geopolitical', 'safety_incidents')",
            name="check_signpost_category"
        ),
        CheckConstraint(
            "direction IN ('>=', '<=')",
            name="check_signpost_direction"
        ),
        Index("idx_signposts_category", "category"),
        Index("idx_signposts_first_class", "first_class"),
    )


class Forecast(Base):
    """Expert forecast model for AGI timeline predictions."""

    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(Text, nullable=False)  # Expert/org name
    signpost_code = Column(String(100), ForeignKey("signposts.code", ondelete="CASCADE"), nullable=False, index=True)
    timeline = Column(Date, nullable=False)  # Predicted achievement date
    confidence = Column(Numeric(4, 2), nullable=True)  # 0.0-1.0
    quote = Column(Text, nullable=True)  # Supporting quote/reasoning
    url = Column(Text, nullable=True)  # Source URL
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    signpost = relationship("Signpost", backref="forecasts")

    # Indexes
    __table_args__ = (
        Index("idx_forecasts_signpost_timeline", "signpost_code", "timeline"),
        Index("idx_forecasts_source", "source"),
        Index("idx_forecasts_timeline", "timeline"),
    )


class Incident(Base):
    """Safety incident model for tracking jailbreaks, misuses, and failures."""

    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    occurred_at = Column(Date, nullable=False, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Integer, nullable=False)  # 1-5 scale
    vectors = Column(JSONB, nullable=True)  # ['jailbreak', 'bias', 'privacy']
    signpost_codes = Column(JSONB, nullable=True)  # Related signposts
    external_url = Column(Text, nullable=True)
    source = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_incidents_occurred_at", "occurred_at", postgresql_ops={"occurred_at": "DESC"}),
        Index("idx_incidents_severity", "severity"),
        CheckConstraint("severity >= 1 AND severity <= 5", name="check_incident_severity"),
    )


class Story(Base):
    """Weekly narrative story model for AGI progress summaries."""

    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    week_start = Column(Date, nullable=False, unique=True, index=True)
    week_end = Column(Date, nullable=False)
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=False)  # Markdown content
    summary = Column(Text, nullable=True)
    index_delta = Column(Numeric(5, 2), nullable=True)
    top_movers = Column(JSONB, nullable=True)  # {rising: [...], falling: [...]}
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_stories_week_start", "week_start", postgresql_ops={"week_start": "DESC"}),
    )


class ProgressIndexSnapshot(Base):
    """Progress Index snapshot model for historical tracking."""

    __tablename__ = "progress_index_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(Date, nullable=False, unique=True, index=True)
    value = Column(Numeric(6, 2), nullable=False)  # 0-100 score
    components = Column(JSONB, nullable=False)  # Component breakdown
    weights = Column(JSONB, nullable=True)  # Weights used
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_progress_index_date_desc", "snapshot_date", postgresql_ops={"snapshot_date": "DESC"}),
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


# ... rest of models
