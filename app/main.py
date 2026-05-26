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
from app.cloudinary_utils import upload_banner, upload_recipient_list
import pandas as pd
from io import StringIO, BytesIO
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
        if csv_file.filename.endswith(".csv"):
            try:
                content_str = contents.decode("utf-8")
                data = pd.read_csv(StringIO(content_str))
            except UnicodeDecodeError:
                content_str = contents.decode("latin-1")
                data = pd.read_csv(StringIO(content_str))
        elif csv_file.filename.endswith((".xls", ".xlsx")):
            data = pd.read_excel(BytesIO(contents))
        else:
            raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Failed to read file: {str(e)}"})

    email_column = None
    for col in data.columns:
        if col.strip().lower() in ["email", "email address"]:
            email_column = col
            break

    if not email_column:
        return JSONResponse(status_code=400, content={"error": "Email column not found in the file."})

    try:
        list_asset = upload_recipient_list(contents, csv_file.filename or "list.csv")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to store recipient list on Cloudinary: {str(e)}"},
        )

    emails = data[email_column].dropna().astype(str).tolist()

    for email in emails:
        try:
            send_email(email, subject, content, banner_url)
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")

    return {
        "message": "Emails sent!",
        "list_stored_at": list_asset["folder"],
        "list_public_id": list_asset["public_id"],
    }


handler = Mangum(app)
