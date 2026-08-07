import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.config import CORS_ORIGINS, load_settings
from app.db import ensure_schema, mysql_configured
from app.routes.analytics import router as analytics_router
from app.services.send import SendEmailsError, process_send_emails

load_settings()

app = FastAPI(title="CEDAT Email Automation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics_router)


@app.on_event("startup")
def _startup_schema() -> None:
    if mysql_configured():
        try:
            ensure_schema()
            print("MySQL analytics schema ready.")
        except Exception as e:
            print(f"MySQL schema init skipped/failed: {e}")


@app.post("/send-emails")
async def send_emails(
    subject: str = Form(...),
    content: str = Form(...),
    banner: UploadFile = File(...),
    csv_file: UploadFile = File(...),
):
    banner_bytes = await banner.read()
    list_bytes = await csv_file.read()

    try:
        result = process_send_emails(
            subject=subject,
            content=content,
            banner_bytes=banner_bytes,
            banner_filename=banner.filename,
            list_bytes=list_bytes,
            list_filename=csv_file.filename,
        )
    except SendEmailsError as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.message})

    return result.model_dump()


handler = Mangum(app)
