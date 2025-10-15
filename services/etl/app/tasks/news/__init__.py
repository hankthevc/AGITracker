"""News ingestion tasks for v0.3."""

from .ingest_company_blogs import ingest_company_blogs_task

__all__ = ["ingest_company_blogs_task"]

