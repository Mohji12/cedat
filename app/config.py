import os
from pathlib import Path

from dotenv import load_dotenv

_APP_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _APP_DIR.parent

_loaded = False


def load_settings() -> None:
    """Load dotenv once from project root and app/.env."""
    global _loaded
    if _loaded:
        return
    load_dotenv(_PROJECT_ROOT / ".env", override=True)
    load_dotenv(_APP_DIR / ".env", override=True)
    _loaded = True


load_settings()


def env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


def _cors_origins() -> list[str]:
    origins: list[str] = []
    defaults = [
        "https://cedat-gules.vercel.app",
        "https://staging.d2iyruqxvegk0e.amplifyapp.com",
        "https://staging.djrmd1qw4vs3h.amplifyapp.com",
        "https://staging.dlg2wln5wgzi2c.amplifyapp.com",
        "https://cedat.krintix.in",
        "https://cedat.mijnlevenspad.com",
        "https://cedat.menteetracker.com",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    extra = env("CORS_ORIGINS") or env("CORS_ORIGIN_EXTRA")
    for value in [*defaults, extra]:
        for part in value.split(","):
            origin = part.strip().rstrip("/")
            if origin and origin not in origins:
                origins.append(origin)
    return origins


CORS_ORIGINS = _cors_origins()
# Preview hosts change often (Amplify + Vercel).
CORS_ORIGIN_REGEX = r"https://([a-z0-9-]+\.)*(amplifyapp\.com|vercel\.app)"

ZEPTO_API_URL = "https://api.zeptomail.in/v1.1/email"


def get_zepto_token() -> str:
    load_settings()
    return env("SMTP_PASSWORD") or env("ZEPTO_API_TOKEN")


def get_sender_email() -> str:
    load_settings()
    return env("SENDER_EMAIL", "support@harishcriticalcareclasses.com")


def get_sender_name() -> str:
    load_settings()
    return env("SENDER_NAME", "Harish Critical Care Classes")


def get_cloudinary_credentials() -> tuple[str, str, str, str]:
    load_settings()
    return (
        env("CLOUDINARY_CLOUD_NAME"),
        env("CLOUDINARY_API_KEY"),
        env("CLOUDINARY_API_SECRET"),
        env("CLOUDINARY_URL"),
    )


def get_mysql_settings() -> dict[str, str | int]:
    load_settings()
    port_raw = env("MYSQL_PORT", "3306")
    try:
        port = int(port_raw)
    except ValueError:
        port = 3306
    return {
        "host": env("MYSQL_HOST"),
        "port": port,
        "user": env("MYSQL_USER"),
        "password": env("MYSQL_PASSWORD"),
        "database": env("MYSQL_DB", "cedat"),
    }
