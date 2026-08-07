from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.db import ensure_schema, fetch_all, fetch_one, get_connection, mysql_configured


@dataclass
class RecipientOutcome:
    email: str
    status: str  # sent | failed
    error_message: str | None = None
    provider_response_id: str | None = None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _campaign_status(total: int, sent: int, failed: int) -> str:
    if total == 0:
        return "empty"
    if sent == 0 and failed > 0:
        return "failed"
    if failed > 0:
        return "partial"
    return "success"


def save_campaign(
    *,
    subject: str,
    content: str,
    banner_url: str | None,
    emails_total: int,
    emails_sent: int,
    emails_failed: int,
    list_public_id: str | None,
    list_folder: str | None,
    source: str,
    outcomes: list[RecipientOutcome],
) -> str | None:
    """
    Persist a campaign and its per-recipient outcomes.
    Returns campaign id, or None if MySQL is not configured / write soft-fails.
    """
    if not mysql_configured():
        print("Analytics skip: MySQL is not configured.")
        return None

    campaign_id = str(uuid4())
    now = _utc_now()
    preview = (content or "").strip().replace("\n", " ")
    if len(preview) > 280:
        preview = preview[:277] + "..."
    status = _campaign_status(emails_total, emails_sent, emails_failed)

    try:
        ensure_schema()
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO email_campaigns (
                        id, created_at, subject, content_preview, banner_url,
                        emails_total, emails_sent, emails_failed, status,
                        list_public_id, list_folder, source
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s
                    )
                    """,
                    (
                        campaign_id,
                        now,
                        subject[:500],
                        preview or None,
                        banner_url,
                        emails_total,
                        emails_sent,
                        emails_failed,
                        status,
                        list_public_id,
                        list_folder,
                        source if source in ("file", "manual") else "file",
                    ),
                )
                if outcomes:
                    cur.executemany(
                        """
                        INSERT INTO email_send_events (
                            campaign_id, recipient_email, status,
                            error_message, provider_response_id, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        [
                            (
                                campaign_id,
                                o.email[:320],
                                o.status,
                                o.error_message,
                                o.provider_response_id,
                                now,
                            )
                            for o in outcomes
                        ],
                    )
        return campaign_id
    except Exception as e:
        print(f"Analytics soft-fail (campaign not saved): {e}")
        return None


def _date_bounds(date_from: str | None, date_to: str | None) -> tuple[str, str]:
    """Normalize to inclusive datetime range strings."""
    start = (date_from or "1970-01-01")[:10] + " 00:00:00"
    end = (date_to or "9999-12-31")[:10] + " 23:59:59.999999"
    return start, end


def summary_kpis(date_from: str | None = None, date_to: str | None = None) -> dict[str, Any]:
    ensure_schema()
    start, end = _date_bounds(date_from, date_to)
    row = fetch_one(
        """
        SELECT
            COUNT(*) AS campaigns,
            COALESCE(SUM(emails_total), 0) AS attempted,
            COALESCE(SUM(emails_sent), 0) AS delivered,
            COALESCE(SUM(emails_failed), 0) AS failed
        FROM email_campaigns
        WHERE created_at BETWEEN %s AND %s
        """,
        (start, end),
    ) or {}
    campaigns = int(row.get("campaigns") or 0)
    attempted = int(row.get("attempted") or 0)
    delivered = int(row.get("delivered") or 0)
    failed = int(row.get("failed") or 0)
    success_rate = round((delivered / attempted) * 100, 2) if attempted else 0.0
    avg_recipients = round(attempted / campaigns, 2) if campaigns else 0.0
    return {
        "campaigns": campaigns,
        "attempted": attempted,
        "delivered": delivered,
        "failed": failed,
        "success_rate": success_rate,
        "avg_recipients": avg_recipients,
    }


def list_campaigns(
    *,
    date_from: str | None = None,
    date_to: str | None = None,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    ensure_schema()
    start, end = _date_bounds(date_from, date_to)
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    params: list[Any] = [start, end]
    where = "WHERE created_at BETWEEN %s AND %s"
    if q and q.strip():
        where += " AND subject LIKE %s"
        params.append(f"%{q.strip()}%")

    total_row = fetch_one(
        f"SELECT COUNT(*) AS total FROM email_campaigns {where}",
        tuple(params),
    ) or {"total": 0}

    rows = fetch_all(
        f"""
        SELECT
            id, created_at, subject, content_preview, banner_url,
            emails_total, emails_sent, emails_failed, status,
            list_public_id, list_folder, source
        FROM email_campaigns
        {where}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """,
        tuple(params + [limit, offset]),
    )
    items = []
    for r in rows:
        total = int(r["emails_total"] or 0)
        sent = int(r["emails_sent"] or 0)
        items.append(
            {
                "id": r["id"],
                "created_at": r["created_at"].isoformat(sep=" ") if r.get("created_at") else None,
                "subject": r["subject"],
                "content_preview": r.get("content_preview"),
                "banner_url": r.get("banner_url"),
                "emails_total": total,
                "emails_sent": sent,
                "emails_failed": int(r["emails_failed"] or 0),
                "success_rate": round((sent / total) * 100, 2) if total else 0.0,
                "status": r["status"],
                "list_public_id": r.get("list_public_id"),
                "list_folder": r.get("list_folder"),
                "source": r.get("source"),
            }
        )
    return {"total": int(total_row.get("total") or 0), "items": items}


def get_campaign(campaign_id: str) -> dict[str, Any] | None:
    ensure_schema()
    r = fetch_one(
        """
        SELECT
            id, created_at, subject, content_preview, banner_url,
            emails_total, emails_sent, emails_failed, status,
            list_public_id, list_folder, source
        FROM email_campaigns
        WHERE id = %s
        """,
        (campaign_id,),
    )
    if not r:
        return None
    events = fetch_all(
        """
        SELECT recipient_email, status, error_message, provider_response_id, created_at
        FROM email_send_events
        WHERE campaign_id = %s
        ORDER BY id ASC
        """,
        (campaign_id,),
    )
    total = int(r["emails_total"] or 0)
    sent = int(r["emails_sent"] or 0)
    return {
        "id": r["id"],
        "created_at": r["created_at"].isoformat(sep=" ") if r.get("created_at") else None,
        "subject": r["subject"],
        "content_preview": r.get("content_preview"),
        "banner_url": r.get("banner_url"),
        "emails_total": total,
        "emails_sent": sent,
        "emails_failed": int(r["emails_failed"] or 0),
        "success_rate": round((sent / total) * 100, 2) if total else 0.0,
        "status": r["status"],
        "list_public_id": r.get("list_public_id"),
        "list_folder": r.get("list_folder"),
        "source": r.get("source"),
        "events": [
            {
                "recipient_email": e["recipient_email"],
                "status": e["status"],
                "error_message": e.get("error_message"),
                "provider_response_id": e.get("provider_response_id"),
                "created_at": e["created_at"].isoformat(sep=" ") if e.get("created_at") else None,
            }
            for e in events
        ],
    }


def volume_by_day(date_from: str | None = None, date_to: str | None = None) -> list[dict[str, Any]]:
    ensure_schema()
    start, end = _date_bounds(date_from, date_to)
    rows = fetch_all(
        """
        SELECT
            DATE(created_at) AS day,
            COALESCE(SUM(emails_total), 0) AS attempted,
            COALESCE(SUM(emails_sent), 0) AS delivered,
            COALESCE(SUM(emails_failed), 0) AS failed
        FROM email_campaigns
        WHERE created_at BETWEEN %s AND %s
        GROUP BY DATE(created_at)
        ORDER BY day ASC
        """,
        (start, end),
    )
    return [
        {
            "day": r["day"].isoformat() if hasattr(r["day"], "isoformat") else str(r["day"]),
            "attempted": int(r["attempted"] or 0),
            "delivered": int(r["delivered"] or 0),
            "failed": int(r["failed"] or 0),
        }
        for r in rows
    ]


def failure_breakdown(
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    ensure_schema()
    start, end = _date_bounds(date_from, date_to)
    limit = max(1, min(limit, 100))
    rows = fetch_all(
        """
        SELECT
            COALESCE(NULLIF(TRIM(error_message), ''), 'Unknown error') AS error_message,
            COUNT(*) AS count
        FROM email_send_events
        WHERE status = 'failed'
          AND created_at BETWEEN %s AND %s
        GROUP BY COALESCE(NULLIF(TRIM(error_message), ''), 'Unknown error')
        ORDER BY count DESC
        LIMIT %s
        """,
        (start, end, limit),
    )
    return [
        {"error_message": r["error_message"], "count": int(r["count"] or 0)}
        for r in rows
    ]
