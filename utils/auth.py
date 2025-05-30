import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from utils.file_extractor import extract_attachments


SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_gmail_drafts(service, max_results=10):
    drafts = service.users().drafts().list(userId='me', maxResults=max_results).execute().get('drafts', [])
    messages = []

    for draft in drafts:
        msg = service.users().drafts().get(userId='me', id=draft['id']).execute().get('message')
        payload = msg.get('payload', {})
        headers = {h['name']: h['value'] for h in payload.get('headers', [])}

        body = ''
        parts = payload.get('parts', [])
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                body += base64.urlsafe_b64decode(part['body'].get('data', '')).decode()

        attachment_text = extract_attachments(service, msg['id'], payload)
        full_text = body + "\n" + attachment_text
        
        messages.append({
            'id': msg['id'],
            'full_text' : full_text,
            'snippet': full_text[:300],
            'subject': headers.get('Subject', '(No Subject)'),
            'to': headers.get('To', '(No Recipient)'),
            'date': headers.get('Date', ''),
        })
    return messages
