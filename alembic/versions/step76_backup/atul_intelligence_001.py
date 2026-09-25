"""add audit logs and synchronization records

Revision ID: atul_intelligence_001
Revises: atul_assets_001
Create Date: 2026-09-25
"""

from alembic import op
import sqlalchemy as sa


revision = "atul_intelligence_001"
down_revision = "atul_assets_001"
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(

        "audit_logs",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False
        ),

        sa.Column(
            "action",
            sa.String(length=50),
            nullable=False
        ),

        sa.Column(
            "entity_type",
            sa.String(length=100),
            nullable=False
        ),

        sa.Column(
            "entity_id",
            sa.Integer(),
            nullable=True
        ),

        sa.Column(
            "asset_code",
            sa.String(length=100),
            nullable=True
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "old_data",
            sa.JSON(),
            nullable=True
        ),

        sa.Column(
            "new_data",
            sa.JSON(),
            nullable=True
        ),

        sa.Column(
            "source",
            sa.String(length=100),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False
        ),

        sa.PrimaryKeyConstraint("id"),

    )


    op.create_index(
        "ix_audit_logs_action",
        "audit_logs",
        ["action"]
    )

    op.create_index(
        "ix_audit_logs_entity_type",
        "audit_logs",
        ["entity_type"]
    )

    op.create_index(
        "ix_audit_logs_entity_id",
        "audit_logs",
        ["entity_id"]
    )

    op.create_index(
        "ix_audit_logs_asset_code",
        "audit_logs",
        ["asset_code"]
    )

    op.create_index(
        "ix_audit_logs_created_at",
        "audit_logs",
        ["created_at"]
    )


    op.create_table(

        "sync_records",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False
        ),

        sa.Column(
            "source_name",
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            "source_type",
            sa.String(length=100),
            nullable=False
        ),

        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False
        ),

        sa.Column(
            "records_found",
            sa.Integer(),
            nullable=False,
            server_default="0"
        ),

        sa.Column(
            "records_created",
            sa.Integer(),
            nullable=False,
            server_default="0"
        ),

        sa.Column(
            "records_updated",
            sa.Integer(),
            nullable=False,
            server_default="0"
        ),

        sa.Column(
            "records_failed",
            sa.Integer(),
            nullable=False,
            server_default="0"
        ),

        sa.Column(
            "message",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "started_at",
            sa.DateTime(),
            nullable=False
        ),

        sa.Column(
            "completed_at",
            sa.DateTime(),
            nullable=True
        ),

        sa.PrimaryKeyConstraint("id"),

    )


    op.create_index(
        "ix_sync_records_source_name",
        "sync_records",
        ["source_name"]
    )

    op.create_index(
        "ix_sync_records_source_type",
        "sync_records",
        ["source_type"]
    )

    op.create_index(
        "ix_sync_records_status",
        "sync_records",
        ["status"]
    )


def downgrade():

    op.drop_index(
        "ix_sync_records_status",
        table_name="sync_records"
    )

    op.drop_index(
        "ix_sync_records_source_type",
        table_name="sync_records"
    )

    op.drop_index(
        "ix_sync_records_source_name",
        table_name="sync_records"
    )

    op.drop_table("sync_records")


    op.drop_index(
        "ix_audit_logs_created_at",
        table_name="audit_logs"
    )

    op.drop_index(
        "ix_audit_logs_asset_code",
        table_name="audit_logs"
    )

    op.drop_index(
        "ix_audit_logs_entity_id",
        table_name="audit_logs"
    )

    op.drop_index(
        "ix_audit_logs_entity_type",
        table_name="audit_logs"
    )

    op.drop_index(
        "ix_audit_logs_action",
        table_name="audit_logs"
    )

    op.drop_table("audit_logs")
