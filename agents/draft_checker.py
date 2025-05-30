from agents.compliance_checker import assess_email_compliance
from agents.email_labeler import label_email
from utils.auth import get_gmail_drafts
from utils.auth import authenticate_gmail


def check_drafts_for_compliance():
    service = authenticate_gmail()
    drafts = get_gmail_drafts(service, max_results = 1)
    # non_compliant = []

    for draft in drafts:
        is_compliant, reason = assess_email_compliance(draft)

        label_email(draft['id'], is_compliant)
        if is_compliant == "No":
            # non_compliant.append({
            #     "subject": draft['subject'],
            #     "to": draft['to'],
            #     "reason": reason,
            #     # "suggestions": suggestions,
            #     "snippet": draft['snippet']
            # })
            print(f"[❌ NON-COMPLIANT DRAFT] {draft['subject']}\nReason: {reason}\n")#Suggestions: {suggestions}\n")
        else:
            print(f"[✅ COMPLIANT DRAFT] {draft['subject']}")
    return is_compliant, reason
