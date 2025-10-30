"""add embeddings to events and signposts

Revision ID: 20251029_add_embeddings
Revises: 20251020115051
Create Date: 2025-10-29

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = '20251029_add_embeddings'
down_revision = '20251020115051'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add embedding columns and HNSW indexes."""
    
    # Add embedding column to events table
    op.add_column('events',
        sa.Column('embedding', Vector(1536), nullable=True)
    )
    
    # Add embedding column to signposts table (already exists in models.py, this is a no-op if it exists)
    # But let's be safe and check
    try:
        op.add_column('signposts',
            sa.Column('embedding', Vector(1536), nullable=True)
        )
    except Exception:
        # Column might already exist
        pass
    
    # Create HNSW index for fast nearest neighbor search on events
    # Using cosine distance (inner product with normalized vectors)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_embedding_hnsw 
        ON events 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)
    
    # Create HNSW index for signposts
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_signposts_embedding_hnsw 
        ON signposts 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)


def downgrade() -> None:
    """Remove embedding columns and indexes."""
    
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_events_embedding_hnsw;")
    op.execute("DROP INDEX IF EXISTS idx_signposts_embedding_hnsw;")
    
    # Drop columns
    op.drop_column('events', 'embedding')
    
    try:
        op.drop_column('signposts', 'embedding')
    except Exception:
        # Column might not exist
        pass

