"""Add retraction tracking fields to events

Revision ID: 011_add_retraction_fields
Revises: 009_add_review_fields
Create Date: 2024-12-19 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '011_add_retraction_fields'
down_revision = '009_add_review_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add retraction tracking fields to events table
    op.add_column('events', sa.Column('retracted_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('events', sa.Column('retraction_reason', sa.Text(), nullable=True))
    op.add_column('events', sa.Column('retraction_evidence_url', sa.Text(), nullable=True))
    
    # Add index on retracted column if it doesn't exist
    # Note: retracted column already exists, just adding index
    try:
        op.create_index('idx_events_retracted', 'events', ['retracted'])
    except:
        pass  # Index might already exist


def downgrade() -> None:
    # Remove retraction tracking fields
    op.drop_column('events', 'retraction_evidence_url')
    op.drop_column('events', 'retraction_reason')
    op.drop_column('events', 'retracted_at')
    
    # Drop index
    try:
        op.drop_index('idx_events_retracted', table_name='events')
    except:
        pass
