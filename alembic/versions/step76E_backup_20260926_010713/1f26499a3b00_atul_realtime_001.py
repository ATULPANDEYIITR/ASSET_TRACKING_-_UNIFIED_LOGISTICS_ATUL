"""ATUL realtime database notification triggers.

Revision ID: atul_intelligence_001
Revises: atul_intelligence_001
"""

from typing import Sequence, Union

from alembic import op


revision: str = "atul_intelligence_001"
down_revision: Union[str, Sequence[str], None] = "atul_assets_001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION atul_realtime_notify()
        RETURNS trigger
        LANGUAGE plpgsql
        AS \$\$
        DECLARE
            payload JSON;
            record_id TEXT;
            operation_name TEXT;
        BEGIN
            operation_name := TG_OP;

            IF TG_OP = 'DELETE' THEN
                record_id := COALESCE(OLD.id::TEXT, '');
            ELSE
                record_id := COALESCE(NEW.id::TEXT, '');
            END IF;

            payload := json_build_object(
                'event', 'database_change',
                'operation', operation_name,
                'table', TG_TABLE_NAME,
                'record_id', record_id,
                'timestamp', CURRENT_TIMESTAMP
            );

            PERFORM pg_notify(
                'atul_realtime',
                payload::TEXT
            );

            RETURN COALESCE(NEW, OLD);
        END;
        \$\$;
        """
    )

    op.execute(
        """
        DROP TRIGGER IF EXISTS atul_assets_realtime_trigger
        ON assets;

        CREATE TRIGGER atul_assets_realtime_trigger
        AFTER INSERT OR UPDATE OR DELETE
        ON assets
        FOR EACH ROW
        EXECUTE FUNCTION atul_realtime_notify();
        """
    )

    op.execute(
        """
        DROP TRIGGER IF EXISTS atul_audit_logs_realtime_trigger
        ON audit_logs;

        CREATE TRIGGER atul_audit_logs_realtime_trigger
        AFTER INSERT OR UPDATE OR DELETE
        ON audit_logs
        FOR EACH ROW
        EXECUTE FUNCTION atul_realtime_notify();
        """
    )

    op.execute(
        """
        DROP TRIGGER IF EXISTS atul_sync_records_realtime_trigger
        ON sync_records;

        CREATE TRIGGER atul_sync_records_realtime_trigger
        AFTER INSERT OR UPDATE OR DELETE
        ON sync_records
        FOR EACH ROW
        EXECUTE FUNCTION atul_realtime_notify();
        """
    )

    op.execute(
        """
        DROP TRIGGER IF EXISTS atul_automation_rules_realtime_trigger
        ON automation_rules;

        CREATE TRIGGER atul_automation_rules_realtime_trigger
        AFTER INSERT OR UPDATE OR DELETE
        ON automation_rules
        FOR EACH ROW
        EXECUTE FUNCTION atul_realtime_notify();
        """
    )

    op.execute(
        """
        DROP TRIGGER IF EXISTS atul_events_realtime_trigger
        ON events;

        CREATE TRIGGER atul_events_realtime_trigger
        AFTER INSERT OR UPDATE OR DELETE
        ON events
        FOR EACH ROW
        EXECUTE FUNCTION atul_realtime_notify();
        """
    )

    op.execute(
        """
        DROP TRIGGER IF EXISTS atul_notifications_realtime_trigger
        ON notifications;

        CREATE TRIGGER atul_notifications_realtime_trigger
        AFTER INSERT OR UPDATE OR DELETE
        ON notifications
        FOR EACH ROW
        EXECUTE FUNCTION atul_realtime_notify();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS atul_assets_realtime_trigger
        ON assets;

        DROP TRIGGER IF EXISTS atul_audit_logs_realtime_trigger
        ON audit_logs;

        DROP TRIGGER IF EXISTS atul_sync_records_realtime_trigger
        ON sync_records;

        DROP TRIGGER IF EXISTS atul_automation_rules_realtime_trigger
        ON automation_rules;

        DROP TRIGGER IF EXISTS atul_events_realtime_trigger
        ON events;

        DROP TRIGGER IF EXISTS atul_notifications_realtime_trigger
        ON notifications;

        DROP FUNCTION IF EXISTS atul_realtime_notify();
        """
    )

