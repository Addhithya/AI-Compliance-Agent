from gemini import check_compliance_with_gemini
from agents.rag_engine import fetch_relevant_regulations

def assess_email_compliance(email):
    full_text = email.get('full_text')
    regulations = fetch_relevant_regulations(full_text)
    return check_compliance_with_gemini(full_text, regulations)
