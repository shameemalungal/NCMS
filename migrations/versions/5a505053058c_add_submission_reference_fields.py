"""Add submission reference fields

Revision ID: 5a505053058c
Revises: 47e15183de88
Create Date: 2026-08-01 11:44:58.093182
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5a505053058c"
down_revision = "47e15183de88"
branch_labels = None
depends_on = None


def upgrade():

    # ------------------------------------------------------
    # 1. Remove temporary table left by failed migration
    # ------------------------------------------------------

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "_alembic_tmp_squads" in inspector.get_table_names():
        op.drop_table("_alembic_tmp_squads")

    # ------------------------------------------------------
    # 2. Remove submission token from Squad
    # ------------------------------------------------------

    with op.batch_alter_table("squads", schema=None) as batch_op:

        batch_op.drop_index(
            batch_op.f("ix_squads_submission_token")
        )

        batch_op.drop_column(
            "submission_token"
        )

    # ------------------------------------------------------
    # 3. Update Submission
    # ------------------------------------------------------

    with op.batch_alter_table("submissions", schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                "source",
                sa.String(length=50),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "submission_token",
                sa.String(length=30),
                nullable=True
            )
        )

        batch_op.create_index(
            batch_op.f(
                "ix_submissions_submission_token"
            ),
            ["submission_token"],
            unique=True
        )

    # ------------------------------------------------------
    # 4. Preserve existing submitted_from values
    # ------------------------------------------------------

    op.execute(
        """
        UPDATE submissions
        SET source = submitted_from
        WHERE submitted_from IS NOT NULL
        """
    )

    # ------------------------------------------------------
    # 5. Remove old submitted_from column
    # ------------------------------------------------------

    with op.batch_alter_table("submissions", schema=None) as batch_op:

        batch_op.drop_column(
            "submitted_from"
        )


def downgrade():

    # ------------------------------------------------------
    # Restore submitted_from
    # ------------------------------------------------------

    with op.batch_alter_table("submissions", schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                "submitted_from",
                sa.String(length=50),
                nullable=True
            )
        )

    # Restore values
    op.execute(
        """
        UPDATE submissions
        SET submitted_from = source
        WHERE source IS NOT NULL
        """
    )

    # Remove new fields
    with op.batch_alter_table("submissions", schema=None) as batch_op:

        batch_op.drop_index(
            batch_op.f(
                "ix_submissions_submission_token"
            )
        )

        batch_op.drop_column(
            "submission_token"
        )

        batch_op.drop_column(
            "source"
        )

    # Restore Squad token column
    with op.batch_alter_table("squads", schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                "submission_token",
                sa.String(length=100),
                nullable=True
            )
        )

        batch_op.create_index(
            batch_op.f(
                "ix_squads_submission_token"
            ),
            ["submission_token"],
            unique=True
        )