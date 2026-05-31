import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

_APP_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _APP_DIR.parent


def _load_env() -> None:
    load_dotenv(_PROJECT_ROOT / ".env", override=True)
    load_dotenv(_APP_DIR / ".env", override=True)


def send_email(to_email: str, subject: str, body: str, banner_url: str):
    """
    Sends email using ZeptoMail REST API.
    This version is for the E drive codebase which uses a single banner_url string.
    """
    _load_env()
    zepto_token = (os.getenv("SMTP_PASSWORD") or os.getenv("ZEPTO_API_TOKEN") or "").strip()
    if not zepto_token:
        raise RuntimeError("Missing SMTP_PASSWORD or ZEPTO_API_TOKEN in environment.")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "support@harishcriticalcareclasses.com")
    SENDER_NAME = os.getenv("SENDER_NAME", "Harish Critical Care Classes")
    API_URL = "https://api.zeptomail.in/v1.1/email"

    # Step 1: Format the body
    formatted_body = body.replace("\n", "<br>")
    url_pattern = r"(https?://\S+)"

    def link_to_button(match):
        url = match.group(0)
        return f"""
        <div style="text-align:center;">
            <a href="{url}" style="display:inline-block;padding:10px 20px;background-color:#00c59a;color:white;text-decoration:none;border-radius:5px;">
                Click Here
            </a>
        </div>
        """

    formatted_body = re.sub(url_pattern, link_to_button, formatted_body)

    # Step 2: Create HTML Body
    html_body = f"""
    <html>
    <body>
        <div style="max-width:600px;margin:auto;background:#fff;padding:20px;">
            <img src="{banner_url}" alt="Banner" style="width:100%;height:auto;object-fit:cover;" />
            <div style="margin-top:20px;">{formatted_body}</div>
        </div>
    </body>
    </html>
    """

    # Step 3: Prepare API Payload
    payload = {
        "from": {
            "address": SENDER_EMAIL,
            "name": SENDER_NAME
        },
        "to": [
            {
                "email_address": {
                    "address": to_email
                }
            }
        ],
        "subject": subject,
        "htmlbody": html_body
    }

    # Step 4: Send API Request
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Zoho-enczapikey {zepto_token}"
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        
        if response.status_code != 200 and response.status_code != 201:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("details", [{}])[0].get("message", "Unknown error")
            raise Exception(f"ZeptoMail API Error: {error_msg}")
                
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to connect to ZeptoMail API: {str(e)}")
    except Exception as e:
        raise Exception(str(e))