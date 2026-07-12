"""Phase 3: allocations, transfer_requests, bookings — concurrency-safe

Revision ID: 0003_phase3_allocation_booking
Revises: 0002_phase2_assets
Create Date: 2026-07-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003_phase3_allocation_booking"
down_revision = "0002_phase2_assets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    # btree_gist lets a GIST exclusion constraint mix a plain equality column
    # (asset_id) with a range-overlap column (time_range) in one constraint.
    # Without it, GIST only understands range/geometric operators, not "=".
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    allocation_status_enum = postgresql.ENUM("ACTIVE", "RETURNED", "TRANSFERRED", name="allocation_status")
    transfer_status_enum = postgresql.ENUM("REQUESTED", "APPROVED", "REJECTED", name="transfer_status")
    booking_status_enum = postgresql.ENUM("UPCOMING", "ONGOING", "COMPLETED", "CANCELLED", name="booking_status")
    allocation_status_enum.create(bind, checkfirst=True)
    transfer_status_enum.create(bind, checkfirst=True)
    booking_status_enum.create(bind, checkfirst=True)

    # ------------------------------------------------------------------ allocations
    op.create_table(
        "allocations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("holder_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("holder_department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("allocated_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", allocation_status_enum, nullable=False, server_default="ACTIVE"),
        sa.Column("expected_return_date", sa.Date, nullable=True),
        sa.Column("allocated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("return_condition_notes", sa.String(1000), nullable=True),
        sa.CheckConstraint("holder_user_id IS NOT NULL OR holder_department_id IS NOT NULL", name="ck_allocations_has_holder"),
    )
    op.create_index("ix_allocations_asset_id", "allocations", ["asset_id"])
    op.create_index("ix_allocations_holder_user_id", "allocations", ["holder_user_id"])
    op.create_index("ix_allocations_holder_department_id", "allocations", ["holder_department_id"])
    op.create_index("ix_allocations_status", "allocations", ["status"])

    # *** THE concurrency guarantee for allocation ***
    # A partial unique index: unique on asset_id, but ONLY among rows where
    # status = 'ACTIVE'. This means Postgres itself refuses to let a second
    # ACTIVE row exist for an asset that already has one — no matter what
    # race condition happens at the application layer above it. Returned/
    # transferred (closed) rows are invisible to this index, so an asset can
    # accumulate unlimited allocation history while only ever having one
    # live holder.
    op.execute(
        """
        CREATE UNIQUE INDEX uq_active_allocation_per_asset
        ON allocations (asset_id)
        WHERE status = 'ACTIVE'
        """
    )

    # ------------------------------------------------------------------ transfer_requests
    op.create_table(
        "transfer_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_allocation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("allocations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_for_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_for_department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", transfer_status_enum, nullable=False, server_default="REQUESTED"),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_notes", sa.String(1000), nullable=True),
        sa.CheckConstraint(
            "requested_for_user_id IS NOT NULL OR requested_for_department_id IS NOT NULL",
            name="ck_transfer_requests_has_target",
        ),
    )
    op.create_index("ix_transfer_requests_asset_id", "transfer_requests", ["asset_id"])
    op.create_index("ix_transfer_requests_status", "transfer_requests", ["status"])

    # Only one PENDING (REQUESTED) transfer per allocation at a time — stops
    # two Department Heads from racing to approve/reject two duplicate
    # requests raised for the same asset in the same instant.
    op.execute(
        """
        CREATE UNIQUE INDEX uq_pending_transfer_per_allocation
        ON transfer_requests (from_allocation_id)
        WHERE status = 'REQUESTED'
        """
    )

    # ------------------------------------------------------------------ bookings
    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("booked_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", booking_status_enum, nullable=False, server_default="UPCOMING"),
        sa.Column("purpose", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("end_time > start_time", name="ck_bookings_end_after_start"),
    )
    op.create_index("ix_bookings_asset_id", "bookings", ["asset_id"])
    op.create_index("ix_bookings_booked_by_user_id", "bookings", ["booked_by_user_id"])
    op.create_index("ix_bookings_status", "bookings", ["status"])
    op.create_index("ix_bookings_start_time", "bookings", ["start_time"])

    # Generated column: a half-open range [start_time, end_time) computed
    # automatically from the two timestamp columns and kept in sync by
    # Postgres on every INSERT/UPDATE (STORED = materialized on disk, so it
    # can be GIST-indexed — a VIRTUAL generated column could not be).
    op.execute(
        """
        ALTER TABLE bookings
        ADD COLUMN time_range TSTZRANGE
        GENERATED ALWAYS AS (tstzrange(start_time, end_time, '[)')) STORED
        """
    )
    op.execute("CREATE INDEX ix_bookings_time_range ON bookings USING gist (time_range)")

    # *** THE concurrency guarantee for booking overlap ***
    # An EXCLUDE constraint is like a UNIQUE constraint, but instead of
    # rejecting rows where a column is EQUAL to an existing row, it rejects
    # rows where a *combination of operators* all evaluate true against an
    # existing row. Here: same asset_id (=) AND overlapping time_range (&&).
    # Enforcement happens inside the same index (and therefore the same
    # atomic operation) as the INSERT itself — there is no separate
    # check-then-insert window for two concurrent transactions to both slip
    # through, which is exactly the race a naive "SELECT to check, then
    # INSERT if clear" approach is vulnerable to.
    # The partial WHERE clause excludes CANCELLED/COMPLETED bookings from
    # ever conflicting with a new request over the same historical slot.
    op.execute(
        """
        ALTER TABLE bookings
        ADD CONSTRAINT no_overlapping_bookings
        EXCLUDE USING gist (
            asset_id WITH =,
            time_range WITH &&
        )
        WHERE (status IN ('UPCOMING', 'ONGOING'))
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE bookings DROP CONSTRAINT no_overlapping_bookings")
    op.drop_index("ix_bookings_time_range", table_name="bookings")
    op.execute("ALTER TABLE bookings DROP COLUMN time_range")
    op.drop_index("ix_bookings_start_time", table_name="bookings")
    op.drop_index("ix_bookings_status", table_name="bookings")
    op.drop_index("ix_bookings_booked_by_user_id", table_name="bookings")
    op.drop_index("ix_bookings_asset_id", table_name="bookings")
    op.drop_table("bookings")

    op.execute("DROP INDEX IF EXISTS uq_pending_transfer_per_allocation")
    op.drop_index("ix_transfer_requests_status", table_name="transfer_requests")
    op.drop_index("ix_transfer_requests_asset_id", table_name="transfer_requests")
    op.drop_table("transfer_requests")

    op.execute("DROP INDEX IF EXISTS uq_active_allocation_per_asset")
    op.drop_index("ix_allocations_status", table_name="allocations")
    op.drop_index("ix_allocations_holder_department_id", table_name="allocations")
    op.drop_index("ix_allocations_holder_user_id", table_name="allocations")
    op.drop_index("ix_allocations_asset_id", table_name="allocations")
    op.drop_table("allocations")

    postgresql.ENUM(name="booking_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="transfer_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="allocation_status").drop(op.get_bind(), checkfirst=True)
