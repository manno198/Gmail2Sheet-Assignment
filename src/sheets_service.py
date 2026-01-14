import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from config import SHEETS_SCOPES, TOKEN_FILE, SPREADSHEET_ID, SHEET_NAME


def authenticate_sheets():
    creds = Credentials.from_authorized_user_file(
        TOKEN_FILE, SHEETS_SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def append_row(service, row):
    body = {
        "values": [row]
    }

    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_NAME,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()
