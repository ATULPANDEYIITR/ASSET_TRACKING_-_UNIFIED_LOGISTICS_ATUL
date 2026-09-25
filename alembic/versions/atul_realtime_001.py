"""ATUL realtime PostgreSQL LISTEN/NOTIFY infrastructure.

Revision ID: atul_realtime_001
Revises: atul_intelligence_001
"""

from alembic import op


revision = "atul_realtime_001"
down_revision = "atul_intelligence_001"
branch_labels = None
depends_on = None


CHANNEL_NAME = "atul_realtime"

TABLES = (
    "assets",
    "audit_logs",
    "sync_records",
    "automation_rules",
    "events",
    "notifications",
)


def upgrade() -> None:
    op.execute(
        f"""
        CREATE OR REPLACE FUNCTION atul_realtime_notify()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        DECLARE
            record_id INTEGER;
            payload TEXT;
        BEGIN
            IF TG_OP = 'DELETE' THEN
                record_id := OLD.id;
            ELSE
                record_id := NEW.id;
            END IF;

            payload := json_build_object(
                'event', 'database_change',
                'operation', TG_OP,
                'table', TG_TABLE_NAME,
                'record_id', record_id
            )::text;

            PERFORM pg_notify('{CHANNEL_NAME}', payload);

            IF TG_OP = 'DELETE' THEN
                RETURN OLD;
            END IF;

            RETURN NEW;
        END;
        $$;
        """
    )

    for table in TABLES:
        trigger_name = f"atul_{table}_realtime_trigger"

        op.execute(
            f"""
            DROP TRIGGER IF EXISTS {trigger_name}
            ON {table};
            """
        )

        op.execute(
            f"""
            CREATE TRIGGER {trigger_name}
            AFTER INSERT OR UPDATE OR DELETE
            ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION atul_realtime_notify();
            """
        )


def downgrade() -> None:
    for table in reversed(TABLES):
        trigger_name = f"atul_{table}_realtime_trigger"

        op.execute(
            f"""
            DROP TRIGGER IF EXISTS {trigger_name}
            ON {table};
            """
        )

    op.execute(
        """
        DROP FUNCTION IF EXISTS atul_realtime_notify();
        """
    )
