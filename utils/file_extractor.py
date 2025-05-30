import os
import base64
from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_attachments(service, msg_id, payload):
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

def extract_all_attachments_text(service, message_id):
    message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    payload = message['payload']
    return extract_attachments(service, message_id, payload)