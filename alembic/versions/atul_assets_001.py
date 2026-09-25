"""create assets table

Revision ID: atul_assets_001
Revises: 0d114d06bfe5
Create Date: 2026-09-25
"""

from alembic import op
import sqlalchemy as sa


revision = "atul_assets_001"
down_revision = "0d114d06bfe5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("asset_code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("asset_type", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("serial_number", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("owner", sa.String(length=255), nullable=True),
        sa.Column("purchase_date", sa.DateTime(), nullable=True),
        sa.Column("purchase_value", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("current_value", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("asset_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("asset_code"),
        sa.UniqueConstraint("serial_number"),
    )

    op.create_index("ix_assets_asset_code", "assets", ["asset_code"], unique=True)
    op.create_index("ix_assets_asset_type", "assets", ["asset_type"], unique=False)
    op.create_index("ix_assets_serial_number", "assets", ["serial_number"], unique=True)
    op.create_index("ix_assets_status", "assets", ["status"], unique=False)
    op.create_index("ix_assets_location", "assets", ["location"], unique=False)


def downgrade():
    op.drop_index("ix_assets_location", table_name="assets")
    op.drop_index("ix_assets_status", table_name="assets")
    op.drop_index("ix_assets_serial_number", table_name="assets")
    op.drop_index("ix_assets_asset_type", table_name="assets")
    op.drop_index("ix_assets_asset_code", table_name="assets")
    op.drop_table("assets")
