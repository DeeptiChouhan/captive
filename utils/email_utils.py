import os
import base64
import re
import html

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


# ---------------------------
# 1️⃣ Gmail Authentication
# ---------------------------
def gmail_service():
    """Authenticate Gmail API and return a service object"""

    creds = None

    # Load saved token
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no token / expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


# ---------------------------
# 2️⃣ Universal Email Invitation Extractor
# ---------------------------
def get_invitation_link(target_email):
    """Fetch the **latest** invitation link from any type of Gmail message."""

    service = gmail_service()

    KEYWORDS = [
        "invitation",
        "invitations",
        "account invitation",
        "account invitations",
        "set password",
        "set your password",
        "activate",
        "verify",
    ]

    keyword_query = " OR ".join([f'subject:\"{k}\"' for k in KEYWORDS])
    query = f'to:{target_email} ({keyword_query})'

    # Search Gmail
    result = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=10
    ).execute()

    messages = result.get("messages", [])
    if not messages:
        raise Exception(f"No invitation email found for {target_email}")

    # ---------------------------
    # 🔥 FIX: Sort by internalDate (newest first)
    # ---------------------------
    messages = sorted(
        messages,
        key=lambda m: int(m.get("internalDate", 0)),
        reverse=True
    )

    latest_id = messages[0]["id"]

    msg = service.users().messages().get(
        userId="me",
        id=latest_id,
        format="full"
    ).execute()

    # ---------------------------
    # HTML Extraction (Recursive)
    # ---------------------------
    def extract_html(payload):
        """Recursively search payload for HTML content."""
        if payload.get("mimeType") == "text/html":
            data = payload["body"].get("data")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        for part in payload.get("parts", []):
            html_body = extract_html(part)
            if html_body:
                return html_body
        
        return None

    html_body = extract_html(msg["payload"])

    if not html_body:
        raise Exception("Email contains no HTML content.")

    # Extract links
    links = re.findall(r'https?://[^\s"]+', html_body)
    if not links:
        raise Exception("Invitation email found but NO link in content.")

    return html.unescape(links[0])
