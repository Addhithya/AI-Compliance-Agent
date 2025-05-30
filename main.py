import os
import base64
# import pickle
# import datetime
# import io
import json

from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb import PersistentClient
# from sentence_transformers import SentenceTransformer
from nomic import embed


from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from PyPDF2 import PdfReader
from docx import Document

from gemini import check_compliance_with_gemini  # You must define this based on your Gemini integration

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


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


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


def download_and_extract_attachments(service, msg_id, payload):
    attachments_text = []
    parts = payload.get('parts', [])
    for part in parts:
        filename = part.get("filename")
        body = part.get("body", {})
        if filename and "attachmentId" in body:
            attachment_id = body["attachmentId"]
            attachment = service.users().messages().attachments().get(
                userId='me', messageId=msg_id, id=attachment_id
            ).execute()
            data = base64.urlsafe_b64decode(attachment['data'])
            file_path = os.path.join("temp_attachments", filename)
            os.makedirs("temp_attachments", exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(data)
            if filename.endswith(".pdf"):
                attachments_text.append(extract_text_from_pdf(file_path))
            elif filename.endswith(".docx"):
                attachments_text.append(extract_text_from_docx(file_path))
    return "\n".join(attachments_text)


def fetch_and_check_emails():
    service = authenticate_gmail()
    results = service.users().messages().list(userId='me', q='in:anywhere', maxResults=10).execute()
    messages = results.get('messages', [])

    flagged_emails = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        payload = msg_data['payload']
        headers = payload.get('headers', [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown Sender)')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

        body = ""
        if 'data' in payload.get('body', {}):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode("utf-8")
        else:
            for part in payload.get('parts', []):
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode("utf-8")

        attachment_text = download_and_extract_attachments(service, msg['id'], payload)

        full_text = body + "\n" + attachment_text

        client = PersistentClient(path="chroma_db")
        collection = client.get_collection(name="compliance-laws")
        # embed_model = SentenceTransformer("all-MiniLM-L6-v2")


        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        email_chunks = splitter.split_text(full_text)
        query_embeddings = embed.text(
            texts=email_chunks,
            model='nomic-embed-text-v1',
            task_type='search_document'
        )['embeddings']

        relevant_regulations = []
        for emb in query_embeddings:
            results = collection.query(
                query_embeddings=[emb],
                n_results=3  # top 3 matches
            )
            for doc in results['documents'][0]:
                relevant_regulations.append(doc)

        unique_regulations = list(set(relevant_regulations))
        regulation_text = "\n\n".join(unique_regulations)


        # regulation_text = open("regulations.txt").read()  # Or fetch from Chroma/vector store
        compliant, reason = check_compliance_with_gemini(full_text, regulation_text)

        if not compliant:
            flagged_emails.append({
                "subject": subject,
                "from": sender,
                "date": date,
                "reason": reason,
                "snippet": full_text[:300]
            })

    with open("flagged_emails.json", "w") as f:
        json.dump(flagged_emails, f, indent=2)

    print(f"Checked {len(messages)} emails. {len(flagged_emails)} flagged.")


if __name__ == '__main__':
    fetch_and_check_emails()
