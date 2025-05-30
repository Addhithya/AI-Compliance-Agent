from agents.gmail_monitor import fetch_recent_emails
from agents.compliance_checker import assess_email_compliance
from agents.email_labeler import label_email
from agents.notifier import send_notification
import json

def main():
    emails = fetch_recent_emails(max_results=10)
    all_emails = []

    for email in emails:
        is_compliant, reason = assess_email_compliance(email)

        label_email(email['id'], is_compliant)

        if is_compliant == "No":
            send_notification(email['subject'], reason)
        all_emails.append({
            "subject": email['subject'],
            "from": email['from'],
            "date": email['date'],
            "Compliance": is_compliant,
            "reason": reason,
            "snippet": email['snippet']
        })

    with open("all_emails.json", "w") as f:
        json.dump(all_emails, f, indent=2)

    print(f"Checked {len(emails)} emails. {len(all_emails)}.")

if __name__ == "__main__":
    main()
