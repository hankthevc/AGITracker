"""merge heads

Revision ID: 017_merge_heads
Revises: 015_merge_branches, 016_news_events_pipeline
Create Date: 2025-10-27 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '017_merge_heads'
down_revision: Union[str, Sequence[str], None] = ('015_merge_branches', '016_news_events_pipeline')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge migration - no changes needed."""
    pass


def downgrade() -> None:
    """Merge migration - no changes needed."""
    pass

