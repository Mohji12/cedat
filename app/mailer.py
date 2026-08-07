import json
import re

import requests

from app import config


def _extract_provider_id(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    for key in ("request_id", "message_id", "id"):
        value = payload.get(key)
        if value:
            return str(value)[:255]
    data = payload.get("data")
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            for key in ("message_id", "request_id", "code"):
                value = first.get(key)
                if value:
                    return str(value)[:255]
    elif isinstance(data, dict):
        for key in ("message_id", "request_id", "code"):
            value = data.get(key)
            if value:
                return str(value)[:255]
    return None


def send_email(to_email: str, subject: str, body: str, banner_url: str) -> dict:
    """
    Sends email using ZeptoMail REST API.
    Returns {"provider_response_id": str|None, "raw": dict}.
    """
    config.load_settings()
    zepto_token = config.get_zepto_token()
    if not zepto_token:
        raise RuntimeError("Missing SMTP_PASSWORD or ZEPTO_API_TOKEN in environment.")

    sender_email = config.get_sender_email()
    sender_name = config.get_sender_name()
    api_url = config.ZEPTO_API_URL

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

    payload = {
        "from": {
            "address": sender_email,
            "name": sender_name,
        },
        "to": [
            {
                "email_address": {
                    "address": to_email,
                }
            }
        ],
        "subject": subject,
        "htmlbody": html_body,
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Zoho-enczapikey {zepto_token}",
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))

        if response.status_code not in (200, 201):
            error_data = response.json()
            error_msg = (
                error_data.get("error", {})
                .get("details", [{}])[0]
                .get("message", "Unknown error")
            )
            raise RuntimeError(f"ZeptoMail API Error: {error_msg}")

        raw = response.json()
        return {
            "provider_response_id": _extract_provider_id(raw),
            "raw": raw,
        }

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to connect to ZeptoMail API: {e}") from e
