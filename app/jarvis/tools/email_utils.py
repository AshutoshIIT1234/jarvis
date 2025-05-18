"""Utility functions for Gmail integration."""

import json
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define scopes needed for Gmail
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

# Path for token storage
TOKEN_PATH = Path("~/.credentials/gmail_token.json").expanduser()
CREDENTIALS_PATH = Path("credentials.json")


def get_gmail_service():
    """
    Authenticate and create a Gmail service object.

    Returns:
        A Gmail service object or None if authentication fails
    """
    creds = None

    # Check if token exists and is valid
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_info(
            json.loads(TOKEN_PATH.read_text()), SCOPES
        )

    # If credentials don't exist or are invalid, refresh or get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # If credentials.json doesn't exist, we can't proceed with OAuth flow
            if not CREDENTIALS_PATH.exists():
                print(
                    f"Error: {CREDENTIALS_PATH} not found. Please follow setup instructions."
                )
                return None

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json())

    # Create and return the Gmail service
    return build("gmail", "v1", credentials=creds)


def create_message(sender, to, subject, message_text, is_html=False):
    """
    Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        is_html: Boolean indicating if the message is HTML.

    Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    if is_html:
        msg = MIMEText(message_text, 'html')
    else:
        msg = MIMEText(message_text, 'plain')
    
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}


def format_message(message):
    """
    Format a message from Gmail API into a readable format.

    Args:
        message: A message object from Gmail API

    Returns:
        dict: A formatted message with key details
    """
    headers = {}
    for header in message.get('payload', {}).get('headers', []):
        headers[header['name'].lower()] = header['value']
    
    # Extract message body (simplified - in real implementation, would need to handle multipart)
    body = ""
    try:
        if 'parts' in message.get('payload', {}):
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode()
                    break
        elif 'body' in message.get('payload', {}) and 'data' in message['payload']['body']:
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode()
    except Exception:
        body = "[Could not decode message body]"

    return {
        "id": message.get('id', ''),
        "thread_id": message.get('threadId', ''),
        "from": headers.get('from', 'Unknown'),
        "to": headers.get('to', 'Unknown'),
        "subject": headers.get('subject', '(No Subject)'),
        "date": headers.get('date', 'Unknown'),
        "snippet": message.get('snippet', ''),
        "body": body
    }