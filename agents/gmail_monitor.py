from utils.auth import authenticate_gmail
from utils.file_extractor import extract_attachments
import base64

def fetch_recent_emails(max_results=10):
    service = authenticate_gmail()
    results = service.users().messages().list(userId='me', q='in:anywhere', maxResults=max_results).execute()
    messages = results.get('messages', [])
    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        payload = msg_data['payload']
        headers = payload.get('headers', [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown Sender)')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        msg_id = msg['id']

        body = ""
        if 'data' in payload.get('body', {}):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode("utf-8")
        else:
            for part in payload.get('parts', []):
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode("utf-8")

        attachment_text = extract_attachments(service, msg_id, payload)
        full_text = body + "\n" + attachment_text

        emails.append({
            'id': msg_id,
            'subject': subject,
            'from': sender,
            'date': date,
            'full_text': full_text,
            'snippet': full_text[:300]
        })

    return emails
