import io
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

_APP_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _APP_DIR.parent


def _load_env() -> None:
    """Load env files on each configure call (uvicorn --reload does not watch .env)."""
    load_dotenv(_PROJECT_ROOT / ".env", override=True)
    load_dotenv(_APP_DIR / ".env", override=True)


def _configure() -> None:
    _load_env()

    cloud_name = (os.getenv("CLOUDINARY_CLOUD_NAME") or "").strip()
    api_key = (os.getenv("CLOUDINARY_API_KEY") or "").strip()
    api_secret = (os.getenv("CLOUDINARY_API_SECRET") or "").strip()
    if cloud_name and api_key and api_secret:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )
        return

    url = (os.getenv("CLOUDINARY_URL") or "").strip()
    if url:
        os.environ["CLOUDINARY_URL"] = url
        cloudinary.config(secure=True)
        return

    raise RuntimeError(
        "Missing Cloudinary config. Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, "
        "and CLOUDINARY_API_SECRET in app/.env "
        f"(checked {_APP_DIR / '.env'})."
    )


def _safe_filename(filename: str) -> str:
    raw = PurePosixPath(filename or "file").name
    return "".join(c for c in raw if c.isalnum() or c in "._- ")[:180] or "file"


def upload_banner(file_content: bytes, original_filename: str) -> str:
    """Upload email banner image; returns public HTTPS URL for use in HTML emails."""
    _configure()
    result = cloudinary.uploader.upload(
        io.BytesIO(file_content),
        folder="cedat/banners",
        resource_type="image",
        use_filename=True,
        unique_filename=True,
        filename_override=_safe_filename(original_filename or "banner.jpg"),
    )
    return str(result["secure_url"])


def upload_recipient_list(file_content: bytes, original_filename: str) -> dict[str, str]:
    """
    Archive CSV/Excel on Cloudinary (contains PII).
    Uses folder cedat/email-lists, resource_type raw, access_control none (not public CDN).
    Returns public_id and asset_folder for logging / API response.
    """
    _configure()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    uid = uuid.uuid4().hex[:10]
    safe_name = _safe_filename(original_filename or "list.csv")

    result = cloudinary.uploader.upload(
        io.BytesIO(file_content),
        folder="cedat/email-lists",
        resource_type="raw",
        type="private",
        use_filename=True,
        unique_filename=True,
        filename_override=f"{ts}_{uid}_{safe_name}",
    )

    public_id = str(result["public_id"])
    asset_folder = str(result.get("asset_folder") or "cedat/email-lists")
    print(f"Stored recipient list on Cloudinary: public_id={public_id} folder={asset_folder}")

    return {
        "public_id": public_id,
        "folder": asset_folder,
        "resource_type": str(result.get("resource_type", "raw")),
    }
