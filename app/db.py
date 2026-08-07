from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Generator

import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

from app.config import get_mysql_settings

_schema_ready = False


def mysql_configured() -> bool:
    settings = get_mysql_settings()
    return bool(settings["host"] and settings["user"] and settings["database"])


@contextmanager
def get_connection() -> Generator[Connection, None, None]:
    if not mysql_configured():
        raise RuntimeError(
            "MySQL is not configured. Set MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DB."
        )
    settings = get_mysql_settings()
    conn = pymysql.connect(
        host=str(settings["host"]),
        port=int(settings["port"]),
        user=str(settings["user"]),
        password=str(settings["password"]),
        database=str(settings["database"]),
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
        connect_timeout=10,
        read_timeout=30,
        write_timeout=30,
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ensure_schema() -> None:
    """Create analytics tables if they do not exist."""
    global _schema_ready
    if _schema_ready:
        return
    if not mysql_configured():
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS email_campaigns (
                    id CHAR(36) NOT NULL PRIMARY KEY,
                    created_at DATETIME(6) NOT NULL,
                    subject VARCHAR(500) NOT NULL,
                    content_preview VARCHAR(280) NULL,
                    banner_url TEXT NULL,
                    emails_total INT NOT NULL DEFAULT 0,
                    emails_sent INT NOT NULL DEFAULT 0,
                    emails_failed INT NOT NULL DEFAULT 0,
                    status VARCHAR(20) NOT NULL,
                    list_public_id VARCHAR(512) NULL,
                    list_folder VARCHAR(255) NULL,
                    source VARCHAR(20) NOT NULL DEFAULT 'file',
                    INDEX idx_campaigns_created_at (created_at),
                    INDEX idx_campaigns_subject (subject)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS email_send_events (
                    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    campaign_id CHAR(36) NOT NULL,
                    recipient_email VARCHAR(320) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    error_message TEXT NULL,
                    provider_response_id VARCHAR(255) NULL,
                    created_at DATETIME(6) NOT NULL,
                    INDEX idx_events_campaign (campaign_id),
                    INDEX idx_events_recipient (recipient_email),
                    INDEX idx_events_created_at (created_at),
                    CONSTRAINT fk_events_campaign
                        FOREIGN KEY (campaign_id) REFERENCES email_campaigns(id)
                        ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
    _schema_ready = True


def fetch_all(sql: str, params: tuple[Any, ...] | list[Any] | None = None) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            return list(rows or [])


def fetch_one(sql: str, params: tuple[Any, ...] | list[Any] | None = None) -> dict[str, Any] | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            row = cur.fetchone()
            return dict(row) if row else None
