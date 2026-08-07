from typing import Any

from pydantic import BaseModel, Field


class StoredFileAsset(BaseModel):
    public_id: str
    folder: str
    resource_type: str
    filename: str
    bytes: str


class SendEmailsResponse(BaseModel):
    message: str
    emails_sent: int
    emails_failed: int
    emails_total: int
    rows_stored: int
    columns_stored: list[str]
    files_stored: list[dict[str, Any]] = Field(default_factory=list)
    list_stored_at: str = "cedat/email-lists"
    list_public_id: str | None = None
    campaign_id: str | None = None
