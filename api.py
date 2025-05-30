from flask import Flask, request, jsonify
from utils.auth import authenticate_gmail, get_gmail_drafts
# from utils.file_extractor import extract_attachments
from agents.email_labeler import label_email
# from agents.rag_engine import fetch_relevant_regulations
from agents.compliance_checker import assess_email_compliance
from agents.draft_checker import check_drafts_for_compliance
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

# def has_attachments(payload):
#     parts = payload.get("parts", [])
#     for part in parts:
#         filename = part.get("filename")
#         body = part.get("body", {})
#         if filename and "attachmentId" in body:
#             return True
#     return False

@app.route('/assess', methods=['POST'])
def assess():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # is_compliant, reason = check_drafts_for_compliance()
    # attachment_text = ""
    # msg_id = None

    # try:
    service = authenticate_gmail()
    drafts = get_gmail_drafts(service, max_results=1)
    
    for draft in drafts:
        is_compliant, reason = assess_email_compliance(draft)

        # draft_obj = service.users().drafts().get(userId='me', id=draft['id']).execute()
        # message_id = draft['id']
        
        # label_email(message_id, is_compliant)

        # label_email(draft['id'], is_compliant)
    # for draft in drafts:
        # if draft["body"].strip() == text.strip():
            # print("Draft changed. Attachment detected...")
    # msg_id = draft['id']
    # msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    # payload = msg.get("payload", {})
    # if has_attachments(payload):
    #     print("📎 Draft has attachments.")
    #     attachment_text = extract_attachments(service, msg_id, payload)
    # attachment_text = extract_attachments(service, msg_id, payload)
    # except Exception as e:
    #     print("Attachment extraction failed:", e)


    # full_text = draft['full_text']
    # regulations = fetch_relevant_regulations(full_text)
    # is_compliant, reason = assess_email_compliance(draft)

    # label_email(draft['id'], is_compliant)
    # if msg_id:
    #     try:
    #         label_email(msg_id, is_compliant)
    #     except Exception as e:
    #         print("Labeling failed:", e)


    return jsonify({
        "compliant": is_compliant,
        "reason": reason if is_compliant == "No" else None
    })

if __name__ == '__main__':
    app.run(port=8000)
