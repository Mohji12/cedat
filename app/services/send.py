from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from app.analytics_store import RecipientOutcome, save_campaign
from app.cloudinary_utils import upload_all_recipient_lists, upload_banner
from app.data_archive import (
    build_storage_files,
    extract_emails,
    find_email_column,
    read_recipient_file,
)
from app.config import get_send_concurrency
from app.mailer import send_email
from app.schemas import SendEmailsResponse


class SendEmailsError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _send_one(email: str, subject: str, content: str, banner_url: str) -> RecipientOutcome:
    try:
        result = send_email(email, subject, content, banner_url)
        provider_id = result.get("provider_response_id") if isinstance(result, dict) else None
        return RecipientOutcome(
            email=email,
            status="sent",
            provider_response_id=str(provider_id) if provider_id else None,
        )
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")
        return RecipientOutcome(
            email=email,
            status="failed",
            error_message=str(e)[:2000],
        )


def _detect_source(list_filename: str | None) -> str:
    name = (list_filename or "").strip().lower()
    if name == "manual_emails.csv" or name.endswith("manual_emails.csv"):
        return "manual"
    return "file"


def process_send_emails(
    *,
    subject: str,
    content: str,
    banner_bytes: bytes,
    banner_filename: str | None,
    list_bytes: bytes,
    list_filename: str | None,
) -> SendEmailsResponse:
    try:
        banner_url = upload_banner(banner_bytes, banner_filename or "banner.jpg")
    except Exception as e:
        raise SendEmailsError(
            f"Failed to upload banner to Cloudinary: {e}",
            status_code=500,
        ) from e

    try:
        data = read_recipient_file(list_bytes, list_filename)
    except Exception as e:
        raise SendEmailsError(f"Failed to read file: {e}", status_code=400) from e

    email_column = find_email_column(data)
    if not email_column:
        raise SendEmailsError("Email column not found in the file.", status_code=400)

    try:
        storage_files = build_storage_files(data, list_bytes, list_filename)
        list_assets = upload_all_recipient_lists(storage_files)
    except Exception as e:
        raise SendEmailsError(
            f"Failed to store recipient list on Cloudinary: {e}",
            status_code=500,
        ) from e

    emails = extract_emails(data, email_column)

    outcomes: list[RecipientOutcome] = []
    if emails:
        workers = min(get_send_concurrency(), len(emails))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            outcomes = list(
                pool.map(lambda addr: _send_one(addr, subject, content, banner_url), emails)
            )

    emails_sent = sum(1 for o in outcomes if o.status == "sent")
    emails_failed = len(outcomes) - emails_sent

    total = len(emails)
    if total == 0:
        message = "No email addresses found to send."
    elif emails_sent == 0:
        message = f"Failed to send all {total} emails."
    elif emails_failed > 0:
        message = f"Sent {emails_sent} of {total} emails ({emails_failed} failed)."
    else:
        message = f"Successfully sent {emails_sent} email{'s' if emails_sent != 1 else ''}."

    columns = [str(c) for c in data.columns.tolist()]
    list_folder = list_assets[-1]["folder"] if list_assets else "cedat/email-lists"
    list_public_id = list_assets[-1]["public_id"] if list_assets else None

    campaign_id = save_campaign(
        subject=subject,
        content=content,
        banner_url=banner_url,
        emails_total=total,
        emails_sent=emails_sent,
        emails_failed=emails_failed,
        list_public_id=list_public_id,
        list_folder=list_folder,
        source=_detect_source(list_filename),
        outcomes=outcomes,
    )

    return SendEmailsResponse(
        message=message,
        emails_sent=emails_sent,
        emails_failed=emails_failed,
        emails_total=total,
        rows_stored=len(data),
        columns_stored=columns,
        files_stored=list_assets,
        list_stored_at=list_folder,
        list_public_id=list_public_id,
        campaign_id=campaign_id,
    )
