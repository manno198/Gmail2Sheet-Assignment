import os
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import GMAIL_SCOPES, SHEETS_SCOPES, CREDENTIALS_FILE, TOKEN_FILE, STATE_FILE



def authenticate_gmail():
    creds = None
    ALL_SCOPES = GMAIL_SCOPES + SHEETS_SCOPES  

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, ALL_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, ALL_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)



def load_last_timestamp():
    if not os.path.exists(STATE_FILE):
        return 0

    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_timestamp", 0)
    except (json.JSONDecodeError, ValueError):
        # Corrupted or empty state file
        return 0



def save_last_timestamp(timestamp):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_timestamp": timestamp}, f)


def fetch_unread_emails(service, last_timestamp):
    query = "is:unread in:inbox"
    response = service.users().messages().list(
        userId="me",
        q=query
    ).execute()
    return response.get("messages", [])



def mark_as_read(service, msg_id):
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={"removeLabelIds": ["UNREAD"]}
    ).execute()
