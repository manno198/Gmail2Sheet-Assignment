import base64
from email.utils import parseaddr
from bs4 import BeautifulSoup

def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def parse_email(service, msg_id):
    message = service.users().messages().get(
        userId="me",
        id=msg_id,
        format="full"
    ).execute()

    headers = message["payload"]["headers"]
    payload = message["payload"]

    email_data = {
        "from": "",
        "subject": "",
        "date": "",
        "body": "",
        "timestamp": int(message["internalDate"])
    }

    for h in headers:
        if h["name"] == "From":
            email_data["from"] = parseaddr(h["value"])[1]
        elif h["name"] == "Subject":
            email_data["subject"] = h["value"]
        elif h["name"] == "Date":
            email_data["date"] = h["value"]

    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data")
                if data:
                    email_data["body"] = base64.urlsafe_b64decode(data).decode("utf-8")
    else:
        body = payload["body"].get("data")
        if body:
            email_data["body"] = base64.urlsafe_b64decode(body).decode("utf-8")
    

    # Convert HTML to plain text if needed
    email_data["body"] = html_to_text(email_data["body"])

    MAX_CELL_LENGTH = 30000  #Below the Google Sheets limit

    email_data["body"] = email_data["body"][:MAX_CELL_LENGTH]

    return email_data
