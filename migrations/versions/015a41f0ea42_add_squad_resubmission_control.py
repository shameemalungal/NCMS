"""Add squad resubmission control

Revision ID: 015a41f0ea42
Revises: 493bc878b2a4
Create Date: 2026-08-09 13:37:00

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision = "015a41f0ea42"
down_revision = "493bc878b2a4"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table(
        "squads",
        schema=None,
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "resubmission_allowed",
                sa.Boolean(),
                server_default="0",
                nullable=False,
            )
        )

        batch_op.add_column(
            sa.Column(
                "resubmission_allowed_at",
                sa.DateTime(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "resubmission_allowed_by",
                sa.String(length=100),
                nullable=True,
            )
        )


def downgrade():

    with op.batch_alter_table(
        "squads",
        schema=None,
    ) as batch_op:

        batch_op.drop_column(
            "resubmission_allowed_by"
        )

        batch_op.drop_column(
            "resubmission_allowed_at"
        )

        batch_op.drop_column(
            "resubmission_allowed"
        )
