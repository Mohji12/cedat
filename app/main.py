import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv(project_root / ".env", override=True)
load_dotenv(Path(__file__).parent / ".env", override=True)

from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.mailer import send_email
from app.cloudinary_utils import upload_banner, upload_all_recipient_lists
from app.data_archive import read_recipient_file, build_storage_files
from mangum import Mangum

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/send-emails")
async def send_emails(
    subject: str = Form(...),
    content: str = Form(...),
    banner: UploadFile = File(...),
    csv_file: UploadFile = File(...),
):
    banner_bytes = await banner.read()
    try:
        banner_url = upload_banner(banner_bytes, banner.filename or "banner.jpg")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to upload banner to Cloudinary: {str(e)}"},
        )

    contents = await csv_file.read()

    try:
        data = read_recipient_file(contents, csv_file.filename)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Failed to read file: {str(e)}"})

    email_column = None
    for col in data.columns:
        if str(col).strip().lower() in ["email", "email address"]:
            email_column = col
            break

    if not email_column:
        return JSONResponse(status_code=400, content={"error": "Email column not found in the file."})

    try:
        storage_files = build_storage_files(data, contents, csv_file.filename)
        list_assets = upload_all_recipient_lists(storage_files)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to store recipient list on Cloudinary: {str(e)}"},
        )

    emails = data[email_column].dropna().astype(str).tolist()
    emails = [e.strip() for e in emails if str(e).strip()]

    for email in emails:
        try:
            send_email(email, subject, content, banner_url)
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")

    columns = [str(c) for c in data.columns.tolist()]

    return {
        "message": "Emails sent!",
        "rows_stored": len(data),
        "columns_stored": columns,
        "files_stored": list_assets,
        "list_stored_at": list_assets[-1]["folder"] if list_assets else "cedat/email-lists",
        "list_public_id": list_assets[-1]["public_id"] if list_assets else None,
    }


handler = Mangum(app)
