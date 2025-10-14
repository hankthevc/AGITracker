"""Pydantic v2 models mirroring TypeScript schemas."""
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Category(str, Enum):
    CAPABILITIES = "capabilities"
    AGENTS = "agents"
    INPUTS = "inputs"
    SECURITY = "security"


class Direction(str, Enum):
    GTE = ">="
    LTE = "<="


class BenchmarkFamily(str, Enum):
    SWE_BENCH_VERIFIED = "SWE_BENCH_VERIFIED"
    OSWORLD = "OSWORLD"
    WEBARENA = "WEBARENA"
    GPQA_DIAMOND = "GPQA_DIAMOND"
    OTHER = "OTHER"


class SourceType(str, Enum):
    PAPER = "paper"
    LEADERBOARD = "leaderboard"
    MODEL_CARD = "model_card"
    PRESS = "press"
    BLOG = "blog"
    SOCIAL = "social"


class Credibility(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class ChangelogType(str, Enum):
    ADD = "add"
    UPDATE = "update"
    RETRACT = "retract"


class Preset(str, Enum):
    EQUAL = "equal"
    ASCHENBRENNER = "aschenbrenner"
    AI2027 = "ai2027"
    CUSTOM = "custom"


class Role(str, Enum):
    ADMIN = "admin"
    READONLY = "readonly"


class RoadmapModel(BaseModel):
    id: int
    slug: str
    name: str
    description: Optional[str] = None
    preset_weights: Optional[dict[str, float]] = None
    created_at: datetime


class SignpostModel(BaseModel):
    id: int
    code: str
    roadmap_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    category: Category
    metric_name: Optional[str] = None
    unit: Optional[str] = None
    direction: Direction
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    methodology_url: Optional[str] = None
    first_class: bool = False
    created_at: datetime


class BenchmarkModel(BaseModel):
    id: int
    code: str
    name: str
    url: Optional[str] = None
    family: BenchmarkFamily
    created_at: datetime


class SourceModel(BaseModel):
    id: int
    url: str
    domain: Optional[str] = None
    source_type: SourceType
    credibility: Credibility
    first_seen_at: datetime


class ClaimModel(BaseModel):
    id: int
    title: Optional[str] = None
    summary: Optional[str] = None
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    unit: Optional[str] = None
    observed_at: datetime
    source_id: Optional[int] = None
    url_hash: Optional[str] = None
    extraction_confidence: Optional[float] = None
    raw_json: Optional[dict[str, Any]] = None
    retracted: bool = False
    created_at: datetime


class IndexSnapshotModel(BaseModel):
    id: int
    as_of_date: str
    capabilities: Optional[float] = None
    agents: Optional[float] = None
    inputs: Optional[float] = None
    security: Optional[float] = None
    overall: Optional[float] = None
    safety_margin: Optional[float] = None
    preset: Preset = Preset.EQUAL
    details: Optional[dict[str, Any]] = None
    created_at: datetime


class ChangelogModel(BaseModel):
    id: int
    occurred_at: datetime
    type: ChangelogType
    title: Optional[str] = None
    body: Optional[str] = None
    claim_id: Optional[int] = None
    reason: Optional[str] = None
    created_at: datetime


class EvidenceCount(BaseModel):
    A: int = 0
    B: int = 0
    C: int = 0
    D: int = 0


class SignpostWithProgress(SignpostModel):
    progress: float
    evidence_count: EvidenceCount


class ConfidenceBand(BaseModel):
    lower: float
    upper: float


class IndexResponse(BaseModel):
    as_of_date: str
    overall: float
    capabilities: float
    agents: float
    inputs: float
    security: float
    safety_margin: float
    preset: Preset
    confidence_bands: dict[str, ConfidenceBand]

