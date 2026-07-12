"""Phase 2: assets, asset_state_transitions, asset_tag_seq

Revision ID: 0002_phase2_assets
Revises: 0001_phase1_auth_master_data
Create Date: 2026-07-19
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_phase2_assets"
down_revision = "0001_phase1_auth_master_data"
branch_labels = None
depends_on = None


def upgrade() -> None:
    asset_status_enum = postgresql.ENUM(
        "AVAILABLE", "ALLOCATED", "RESERVED", "UNDER_MAINTENANCE", "LOST", "RETIRED", "DISPOSED",
        name="asset_status",
    )
    asset_condition_enum = postgresql.ENUM("NEW", "GOOD", "FAIR", "POOR", "DAMAGED", name="asset_condition")

    bind = op.get_bind()
    asset_status_enum.create(bind, checkfirst=True)
    asset_condition_enum.create(bind, checkfirst=True)

    # Race-safe Asset Tag generator. START WITH 1 formatted as AF-0001 by the
    # repository layer (AssetTag.format). A DB sequence guarantees atomic,
    # gap-tolerant, concurrency-safe increments — unlike a MAX(id)+1 query,
    # which is vulnerable to a classic read-then-write race under concurrent
    # registrations.
    op.execute("CREATE SEQUENCE IF NOT EXISTS asset_tag_seq START WITH 1 INCREMENT BY 1")

    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("asset_tag", sa.String(32), nullable=False),
        sa.Column("serial_number", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("asset_categories.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", asset_status_enum, nullable=False, server_default="AVAILABLE"),
        sa.Column("condition", asset_condition_enum, nullable=False, server_default="GOOD"),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("is_bookable", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("acquisition_date", sa.Date, nullable=True),
        sa.Column("acquisition_cost", sa.Numeric(14, 2), nullable=True),
        sa.Column("photo_url", sa.String(1024), nullable=True),
        sa.Column("document_urls", postgresql.ARRAY(sa.String(1024)), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Uniqueness constraints — the actual source of truth backing the
    # duplicate-serial-number and duplicate-tag domain checks. The service
    # layer pre-checks are a UX nicety; these indexes are what makes the
    # guarantee airtight under concurrency.
    op.create_unique_constraint("uq_assets_asset_tag", "assets", ["asset_tag"])
    op.create_unique_constraint("uq_assets_serial_number", "assets", ["serial_number"])

    # Composite/filter indexes matching the search endpoint's filter set.
    op.create_index("ix_assets_asset_tag", "assets", ["asset_tag"])
    op.create_index("ix_assets_serial_number", "assets", ["serial_number"])
    op.create_index("ix_assets_category_id", "assets", ["category_id"])
    op.create_index("ix_assets_department_id", "assets", ["department_id"])
    op.create_index("ix_assets_status", "assets", ["status"])
    op.create_index("ix_assets_status_department_id", "assets", ["status", "department_id"])

    op.create_table(
        "asset_state_transitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_state", asset_status_enum, nullable=False),
        sa.Column("to_state", asset_status_enum, nullable=False),
        sa.Column("triggered_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_asset_state_transitions_asset_id", "asset_state_transitions", ["asset_id"])


def downgrade() -> None:
    op.drop_index("ix_asset_state_transitions_asset_id", table_name="asset_state_transitions")
    op.drop_table("asset_state_transitions")

    op.drop_index("ix_assets_status_department_id", table_name="assets")
    op.drop_index("ix_assets_status", table_name="assets")
    op.drop_index("ix_assets_department_id", table_name="assets")
    op.drop_index("ix_assets_category_id", table_name="assets")
    op.drop_index("ix_assets_serial_number", table_name="assets")
    op.drop_index("ix_assets_asset_tag", table_name="assets")
    op.drop_constraint("uq_assets_serial_number", "assets", type_="unique")
    op.drop_constraint("uq_assets_asset_tag", "assets", type_="unique")
    op.drop_table("assets")

    op.execute("DROP SEQUENCE IF EXISTS asset_tag_seq")

    postgresql.ENUM(name="asset_condition").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="asset_status").drop(op.get_bind(), checkfirst=True)
