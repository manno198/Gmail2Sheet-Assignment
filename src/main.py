import sys
import os
import logging

# Add project root to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from config import LOG_FILE
from gmail_service import (
    authenticate_gmail,
    fetch_unread_emails,
    mark_as_read,
    load_last_timestamp,
    save_last_timestamp
)
from sheets_service import authenticate_sheets, append_row
from email_parser import parse_email


# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=LOG_FILE
)


def main():
    gmail_service = authenticate_gmail()
    sheets_service = authenticate_sheets()

    last_timestamp = load_last_timestamp()
    messages = fetch_unread_emails(gmail_service, last_timestamp)

    logging.info(f"Fetched {len(messages)} unread emails")

    newest_timestamp = last_timestamp

    for msg in messages:
        email = parse_email(gmail_service, msg["id"])

        # Subject-based filter
        if "invoice" not in email["subject"].lower():
            logging.info(f"Skipped email with subject: {email['subject']}")
            continue

        row = [
            email["from"],
            email["subject"],
            email["date"],
            email["body"]
        ]

        append_row(sheets_service, row)
        logging.info(f"Appended email: {email['subject']}")

        mark_as_read(gmail_service, msg["id"])
        logging.info(f"Marked email as read: {email['subject']}")

        newest_timestamp = max(newest_timestamp, email["timestamp"])

    save_last_timestamp(newest_timestamp)
    logging.info("Email sync complete.")


if __name__ == "__main__":
    main()
