import logging
from pathlib import Path

import psycopg
from techmunkak.core.config import settings
from techmunkak.core.logging import setup_logging

logger = logging.getLogger(__name__)

MIGRATIONS = Path(__file__).resolve().parents[5] / "db" / "migrations"

TRACKING = """
CREATE SCHEMA IF NOT EXISTS ops;
CREATE TABLE IF NOT EXISTS ops.schema_migrations (
    filename    text PRIMARY KEY,
    applied_at  timestamptz NOT NULL DEFAULT now()
);
"""

def main() -> None:
    setup_logging()
    with psycopg.connect(settings.database_url, autocommit=False) as conn:
        try:
            conn.execute(TRACKING)
            conn.commit()
            applied = {r[0] for r in conn.execute(
                "SELECT filename FROM ops.schema_migrations")}

            for path in sorted(MIGRATIONS.glob("*.sql")):
                if path.name in applied:
                    continue
                
                logger.info("applying %s", path.name)
                
                try:
                    sql = path.read_text()
                    conn.execute(sql)
                    conn.execute(
                        "INSERT INTO ops.schema_migrations (filename) VALUES (%s)",
                        (path.name,))
                    conn.commit()
                except Exception as exc:
                    conn.rollback()
                    raise RuntimeError(f"Migration failed: {path.name}: {exc}") from exc
        except Exception:
            conn.rollback()
            raise
        
    logger.info("up to date")