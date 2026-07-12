"""Phase 1: users, departments, asset_categories

Revision ID: 0001_phase1_auth_master_data
Revises:
Create Date: 2026-07-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_phase1_auth_master_data"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")

    user_role_enum = postgresql.ENUM(
        "EMPLOYEE", "DEPARTMENT_HEAD", "ASSET_MANAGER", "ADMIN", name="user_role"
    )
    user_status_enum = postgresql.ENUM("ACTIVE", "INACTIVE", name="user_status")
    department_status_enum = postgresql.ENUM("ACTIVE", "INACTIVE", name="department_status")

    bind = op.get_bind()
    user_role_enum.create(bind, checkfirst=True)
    user_status_enum.create(bind, checkfirst=True)
    department_status_enum.create(bind, checkfirst=True)

    # departments first (self-referencing FK), head_user_id added without FK
    # constraint to avoid a circular dependency at creation time.
    op.create_table(
        "departments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("parent_department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("head_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", department_status_enum, nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_departments_parent_department_id", "departments", ["parent_department_id"])

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("role", user_role_enum, nullable=False, server_default="EMPLOYEE"),
        sa.Column("status", user_status_enum, nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_department_id_status", "users", ["department_id", "status"])

    # Deferred FK: departments.head_user_id -> users.id (added after users exists)
    op.create_foreign_key(
        "fk_departments_head_user_id",
        "departments",
        "users",
        ["head_user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "asset_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("custom_fields_schema", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("asset_categories")
    op.drop_constraint("fk_departments_head_user_id", "departments", type_="foreignkey")
    op.drop_index("ix_users_department_id_status", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_departments_parent_department_id", table_name="departments")
    op.drop_table("departments")

    postgresql.ENUM(name="department_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="user_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="user_role").drop(op.get_bind(), checkfirst=True)
