import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key= api_key)

def check_compliance_with_gemini(email_text, regulations):
    prompt = f"""
    Analyze the following email for compliance violations.

    Email Content:
    \"\"\"
    {email_text}
    \"\"\"

    Compliance Regulations:
    \"\"\"
    {regulations}
    \"\"\"

    Is this email compliant or violates the regualtion? If the content does not directly violate the regulation(data privacy, GDPR, Financial information, ESG, etc) reply yes, and don't worry about the SPAM activites. Reply in the following format:

    Compliant: Yes or No  
    Reason: [short explanation]
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    output = response.text

    try:
        compliant_line = next(line for line in output.splitlines() if "Compliant:" in line)
        reason_line = next(line for line in output.splitlines() if "Reason:" in line)
        compliant = compliant_line.split("Compliant:")[1].strip()
        reason = reason_line.split("Reason:")[1].strip()
    except Exception as e:
        compliant = "Unknown"
        reason = f"Failed to parse Gemini response: {e}"

    return compliant, reason