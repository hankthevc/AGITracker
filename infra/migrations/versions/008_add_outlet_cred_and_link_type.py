"""add outlet_cred to events and link_type to event_signpost_links

Revision ID: 008_add_outlet_cred_and_link_type
Revises: 007_enhance_events
Create Date: 2025-10-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "008_add_outlet_cred_and_link_type"
down_revision: Union[str, None] = "007_enhance_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- events.outlet_cred (A/B/C/D) ---
    outlet_cred_enum = sa.Enum("A", "B", "C", "D", name="outlet_cred")
    outlet_cred_enum.create(op.get_bind(), checkfirst=True)

    # Add column nullable first for backfill
    op.add_column(
        "events",
        sa.Column("outlet_cred", outlet_cred_enum, nullable=True),
    )

    # Backfill from existing evidence_tier if present
    op.execute(
        """
        UPDATE events
        SET outlet_cred = CASE
            WHEN evidence_tier IN ('A','B','C','D') THEN evidence_tier::outlet_cred
            ELSE NULL
        END
        WHERE outlet_cred IS NULL
        """
    )

    # Make non-nullable thereafter
    op.alter_column("events", "outlet_cred", nullable=False)

    # Index on outlet_cred
    op.create_index("idx_events_outlet_cred", "events", ["outlet_cred"])

    # Ensure created_at on events (if not present)
    op.add_column(
        "events",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )

    # --- event_signpost_links.link_type (supports/contradicts/related) ---
    link_type_enum = sa.Enum("supports", "contradicts", "related", name="link_type")
    link_type_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "event_signpost_links",
        sa.Column("link_type", link_type_enum, nullable=True, server_default="supports"),
    )

    # Make non-nullable after default in place
    op.alter_column("event_signpost_links", "link_type", nullable=False)

    # Ensure created_at on links
    op.add_column(
        "event_signpost_links",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )

    # Ensure index on (signpost_id, observed_at) exists per spec
    try:
        op.create_index(
            "idx_event_signpost_signpost_observed",
            "event_signpost_links",
            ["signpost_id", "observed_at"],
            postgresql_ops={"observed_at": "DESC"},
        )
    except Exception:
        # Likely already exists from prior migrations
        pass


def downgrade() -> None:
    # Drop created_at from links
    try:
        op.drop_column("event_signpost_links", "created_at")
    except Exception:
        pass

    # Drop link_type
    try:
        op.drop_column("event_signpost_links", "link_type")
    except Exception:
        pass
    op.execute("DROP TYPE IF EXISTS link_type")

    # Drop created_at from events
    try:
        op.drop_column("events", "created_at")
    except Exception:
        pass

    # Drop outlet_cred and enum
    try:
        op.drop_index("idx_events_outlet_cred", table_name="events")
    except Exception:
        pass
    try:
        op.drop_column("events", "outlet_cred")
    except Exception:
        pass
    op.execute("DROP TYPE IF EXISTS outlet_cred")
