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
        self.name = "Sarah & Tom (Live-Test)"
        self.instagram = "@sarah.und.tom"
        self.website = ""
        self.fokus = "Hochzeit"

def send_email(subject: str, content: str):
    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = NOTIFICATION_EMAIL

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("SUCCESS: SMTP Email sent!")
    except Exception as e:
        print(f"ERROR SMTP: {e}")

async def process_and_notify_lead(lead):
    system_prompt = """
### ROLLE
Du bist der kreative Assistant für "RealBehind". Die Marke steht für echte Momente, die man fühlt – ungestellte Behind-the-Scenes-Augenblicke.
Deine Aufgabe ist es, Leads extrem kurz, knackig und menschlich für deine Kollegin Pamela aufzubereiten – als wäre es eine schnelle WhatsApp-Nachricht.

### KONTEXT
- Marke: RealBehind (Echtheit über Perfektion, Festhalten verlorener Momente).
- Tonfall: Sehr natürlich, kurz, kumpelhaft (WICHTIG: KEINE KI-typischen Aufzählungen, keine Sternchen, keine dicken Formatierungen).

### AUFGABE
Schreibe den Text exakt in diesem kurzen, fließenden Format ohne Markdown:

INTERN FÜR PAMELA:
Hey Pamela, [1-2 kurze Sätze zum Potenzial dieses Leads]. Eine geile Idee für den ersten Setup-Call wäre: [1 konkrete, kreative Idee].
"""

    user_input = f"Lead-Daten:\nName/Brautpaar: {lead.name}\nInstagram: {lead.instagram}\nWebsite: {lead.website or 'Nicht angegeben'}\nAnlass/Fokus: {lead.fokus}"

    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[user_input],
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
            ),
        )
        print("SUCCESS: Gemini Response generated!")
        briefing_content = response.text
        subject = f"Neuer Lead Qualifiziert: {lead.name} ({lead.fokus})"
        full_content = f"--- INTERNES BRIEFING ---\n\n{briefing_content}\n\n--- LEAD-DETAILS ---\nName: {lead.name}\nInstagram: {lead.instagram}\nWebsite: {lead.website or 'Nicht angegeben'}\nFokus: {lead.fokus}"
        send_email(subject, full_content)
    except Exception as e:
         print(f"ERROR Gemini: {e}")

asyncio.run(process_and_notify_lead(LeadData()))
