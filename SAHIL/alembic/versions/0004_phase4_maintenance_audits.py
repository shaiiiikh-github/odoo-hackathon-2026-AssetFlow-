"""Phase 4: maintenance requests, audit cycles/assignments/findings

Revision ID: 0004_phase4_maintenance_audits
Revises: 0003_phase3_allocation_booking
Create Date: 2026-07-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004_phase4_maintenance_audits"
down_revision = "0003_phase3_allocation_booking"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    maintenance_priority_enum = postgresql.ENUM("LOW", "MEDIUM", "HIGH", "CRITICAL", name="maintenance_priority")
    maintenance_status_enum = postgresql.ENUM(
        "PENDING", "APPROVED", "REJECTED", "TECHNICIAN_ASSIGNED", "IN_PROGRESS", "RESOLVED",
        name="maintenance_status",
    )
    audit_cycle_status_enum = postgresql.ENUM("OPEN", "CLOSED", name="audit_cycle_status")
    audit_finding_status_enum = postgresql.ENUM("PENDING", "VERIFIED", "MISSING", "DAMAGED", name="audit_finding_status")

    maintenance_priority_enum.create(bind, checkfirst=True)
    maintenance_status_enum.create(bind, checkfirst=True)
    audit_cycle_status_enum.create(bind, checkfirst=True)
    audit_finding_status_enum.create(bind, checkfirst=True)

    # ------------------------------------------------------------------ maintenance_requests
    op.create_table(
        "maintenance_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("raised_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issue_description", sa.String(2000), nullable=False),
        sa.Column("priority", maintenance_priority_enum, nullable=False),
        sa.Column("status", maintenance_status_enum, nullable=False, server_default="PENDING"),
        sa.Column("photo_url", sa.String(1024), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rejection_reason", sa.String(1000), nullable=True),
        sa.Column("assigned_technician_name", sa.String(255), nullable=True),
        sa.Column("assigned_technician_contact", sa.String(255), nullable=True),
        sa.Column("resolution_notes", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_maintenance_requests_asset_id", "maintenance_requests", ["asset_id"])
    op.create_index("ix_maintenance_requests_status", "maintenance_requests", ["status"])

    # *** THE concurrency guarantee for maintenance: at most one OPEN request per asset ***
    # Same partial-unique-index technique as uq_active_allocation_per_asset:
    # unique on asset_id, but only among rows whose status is still "open"
    # (i.e. not REJECTED/RESOLVED). Prevents two employees from raising
    # overlapping maintenance requests for the same asset, and keeps the
    # "approval flips asset to UNDER_MAINTENANCE" step unambiguous — there's
    # never more than one candidate request that could cause that flip.
    op.execute(
        """
        CREATE UNIQUE INDEX uq_open_maintenance_per_asset
        ON maintenance_requests (asset_id)
        WHERE status IN ('PENDING', 'APPROVED', 'TECHNICIAN_ASSIGNED', 'IN_PROGRESS')
        """
    )

    # ------------------------------------------------------------------ audit_cycles
    op.create_table(
        "audit_cycles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("status", audit_cycle_status_enum, nullable=False, server_default="OPEN"),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("closed_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("end_date >= start_date", name="ck_audit_cycles_end_after_start"),
    )
    op.create_index("ix_audit_cycles_department_id", "audit_cycles", ["department_id"])
    op.create_index("ix_audit_cycles_status", "audit_cycles", ["status"])

    # ------------------------------------------------------------------ audit_assignments
    op.create_table(
        "audit_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("cycle_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("audit_cycles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("auditor_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("cycle_id", "auditor_user_id", name="uq_audit_assignment_cycle_auditor"),
    )
    op.create_index("ix_audit_assignments_cycle_id", "audit_assignments", ["cycle_id"])
    op.create_index("ix_audit_assignments_auditor_user_id", "audit_assignments", ["auditor_user_id"])

    # ------------------------------------------------------------------ audit_findings
    op.create_table(
        "audit_findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("cycle_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("audit_cycles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("marked_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", audit_finding_status_enum, nullable=False, server_default="PENDING"),
        sa.Column("notes", sa.String(1000), nullable=True),
        sa.Column("marked_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("cycle_id", "asset_id", name="uq_audit_finding_cycle_asset"),
    )
    op.create_index("ix_audit_findings_cycle_id", "audit_findings", ["cycle_id"])
    op.create_index("ix_audit_findings_asset_id", "audit_findings", ["asset_id"])
    op.create_index("ix_audit_findings_status", "audit_findings", ["status"])
    # Composite index backing the discrepancy-report query (findings for a
    # cycle filtered to MISSING/DAMAGED) — avoids a sequential scan even as
    # a large audit cycle accumulates thousands of findings.
    op.create_index("ix_audit_findings_cycle_id_status", "audit_findings", ["cycle_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_audit_findings_cycle_id_status", table_name="audit_findings")
    op.drop_index("ix_audit_findings_status", table_name="audit_findings")
    op.drop_index("ix_audit_findings_asset_id", table_name="audit_findings")
    op.drop_index("ix_audit_findings_cycle_id", table_name="audit_findings")
    op.drop_table("audit_findings")

    op.drop_index("ix_audit_assignments_auditor_user_id", table_name="audit_assignments")
    op.drop_index("ix_audit_assignments_cycle_id", table_name="audit_assignments")
    op.drop_table("audit_assignments")

    op.drop_index("ix_audit_cycles_status", table_name="audit_cycles")
    op.drop_index("ix_audit_cycles_department_id", table_name="audit_cycles")
    op.drop_table("audit_cycles")

    op.execute("DROP INDEX IF EXISTS uq_open_maintenance_per_asset")
    op.drop_index("ix_maintenance_requests_status", table_name="maintenance_requests")
    op.drop_index("ix_maintenance_requests_asset_id", table_name="maintenance_requests")
    op.drop_table("maintenance_requests")

    postgresql.ENUM(name="audit_finding_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="audit_cycle_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="maintenance_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="maintenance_priority").drop(op.get_bind(), checkfirst=True)
