import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from google import genai
import asyncio

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "")

class LeadData:
    def __init__(self):
        self.name = "Paul Elia & Zukünftige"
        self.instagram = "@paul.elia.privat"
        self.website = ""
        self.fokus = "Hochzeit"

def send_email(subject: str, content: str):
    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = NOTIFICATION_EMAIL

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()
    print("SUCCESS: Email sent!")

async def process_and_notify_lead(lead):
    system_prompt = """
### ROLLE
... [Truncated for prompt brevity, replaced in script] ...
1. BRIEFING
2. BESTÄTIGUNGS-MAIL
"""

    user_input = f"Lead-Daten:\nName/Brautpaar: {lead.name}\nInstagram: {lead.instagram}\nWebsite: {lead.website or 'Nicht angegeben'}\nAnlass/Fokus: {lead.fokus}"

    client = genai.Client(api_key=GOOGLE_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[user_input],
        config=genai.types.GenerateContentConfig(
            system_instruction="Du bist der Kern von RealBehind. Erstelle Fokus/Check für Paul Elia Hochzeit. 1. Internes Briefing. 2. Bestaetigungs-Mail. Sei empathisch und professionell.",
        ),
    )
    
    briefing_content = response.text
    subject = f"Neuer Lead Qualifiziert: {lead.name} ({lead.fokus})"
    full_content = f"--- INTERNES BRIEFING ---\n\n{briefing_content}\n\n--- LEAD-DETAILS ---\nName: {lead.name}\nInstagram: {lead.instagram}\nWebsite: {lead.website or 'Nicht angegeben'}\nFokus: {lead.fokus}"
    send_email(subject, full_content)

asyncio.run(process_and_notify_lead(LeadData()))
