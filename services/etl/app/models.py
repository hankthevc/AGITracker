class DashboardSnapshot(Base):
    """Dashboard snapshot model for caching homepage data."""

    __tablename__ = "dashboard_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    generated_at = Column(TIMESTAMP(timezone=True), nullable=False, unique=True, index=True)
    snapshot = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
