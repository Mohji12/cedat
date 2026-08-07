from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.analytics_store import (
    failure_breakdown,
    get_campaign,
    list_campaigns,
    summary_kpis,
    volume_by_day,
)
from app.db import ensure_schema, mysql_configured

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _require_mysql():
    if not mysql_configured():
        return JSONResponse(
            status_code=503,
            content={"error": "MySQL analytics is not configured."},
        )
    try:
        ensure_schema()
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"error": f"Unable to connect to MySQL: {e}"},
        )
    return None


@router.get("/summary")
def analytics_summary(
    date_from: str | None = Query(None, alias="from"),
    date_to: str | None = Query(None, alias="to"),
):
    err = _require_mysql()
    if err:
        return err
    try:
        return summary_kpis(date_from, date_to)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/campaigns")
def analytics_campaigns(
    date_from: str | None = Query(None, alias="from"),
    date_to: str | None = Query(None, alias="to"),
    q: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    err = _require_mysql()
    if err:
        return err
    try:
        return list_campaigns(
            date_from=date_from,
            date_to=date_to,
            q=q,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/campaigns/{campaign_id}")
def analytics_campaign_detail(campaign_id: str):
    err = _require_mysql()
    if err:
        return err
    try:
        campaign = get_campaign(campaign_id)
        if not campaign:
            return JSONResponse(status_code=404, content={"error": "Campaign not found."})
        return campaign
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/volume")
def analytics_volume(
    date_from: str | None = Query(None, alias="from"),
    date_to: str | None = Query(None, alias="to"),
):
    err = _require_mysql()
    if err:
        return err
    try:
        return {"items": volume_by_day(date_from, date_to)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/failures")
def analytics_failures(
    date_from: str | None = Query(None, alias="from"),
    date_to: str | None = Query(None, alias="to"),
    limit: int = Query(20, ge=1, le=100),
):
    err = _require_mysql()
    if err:
        return err
    try:
        return {"items": failure_breakdown(date_from, date_to, limit=limit)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
