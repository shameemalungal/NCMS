"""Add missing backup history table

Revision ID: 92ab14a34ea3
Revises: 015a41f0ea42
Create Date: 2026-08-17

This migration fixes a pre-existing schema mismatch.

The BackupHistory model and backup functionality already exist
in the NCMS application, but the backup_history table was never
included in the original migration chain.

This migration creates only the missing backup_history table.
RBAC tables are intentionally NOT created here.
"""

from alembic import op
import sqlalchemy as sa


# ==========================================================
# Revision identifiers
# ==========================================================

revision = "92ab14a34ea3"

down_revision = "015a41f0ea42"

branch_labels = None

depends_on = None


# ==========================================================
# Upgrade
# ==========================================================

def upgrade():
    """
    Create the pre-existing NCMS backup_history table.

    No RBAC tables are created by this migration.
    """

    op.create_table(
        "backup_history",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "filename",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "created_by",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),
    )


# ==========================================================
# Downgrade
# ==========================================================

def downgrade():
    """
    Remove only the backup_history table created by this
    migration.
    """

    op.drop_table(
        "backup_history"
    )