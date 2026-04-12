import os
import smtplib
from email.message import EmailMessage
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI(title="RealBehind Lead-Funnel API", version="1.1.0")

# ── Config ──────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "")

from typing import Optional

# ── Models ──────────────────────────────────────────────
class LeadData(BaseModel):
    name: str
    instagram: str
    website: Optional[str] = None
    fokus: str

# ── Helpers ─────────────────────────────────────────────

def send_email(subject: str, content: str):
    if not SMTP_USER or not SMTP_PASSWORD or not NOTIFICATION_EMAIL:
        print("DEBUG: Email configuration missing. Skipping email.")
        return

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
        print(f"DEBUG: Email sent to {NOTIFICATION_EMAIL}")
    except Exception as e:
        print(f"DEBUG: Failed to send email: {str(e)}")

async def process_and_notify_lead(lead: LeadData):
    """
    Qualifies the lead using Gemini and sends the briefing via email.
    """
    if not GOOGLE_API_KEY:
        print("DEBUG: GOOGLE_API_KEY missing. Skipping qualification.")
        return

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

TEXT FÜR DEN KUNDEN:
Betreff: Echte Momente: Unser Kennenlernen!
Hey [Name], mega, dass wir sprechen. Der Termin ist geblockt. Überleg dir doch bis zu unserem Call schon mal kurz, welche kleinen, ungestellten Momente dir an eurem Tag eigentlich am wichtigsten sind! Freue mich riesig drauf.
"""

    user_input = f"Lead-Daten:\nName/Brautpaar: {lead.name}\nInstagram: {lead.instagram}\nWebsite: {lead.website or 'Nicht angegeben'}\nAnlass/Fokus: {lead.fokus}"

    client = genai.Client(api_key=GOOGLE_API_KEY)
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[user_input],
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
            ),
        )
        
        briefing_content = response.text
        subject = f"Neuer Lead Qualifiziert: {lead.name} ({lead.fokus})"
        
        # Add metadata to the email
        full_content = f"--- INTERNES BRIEFING ---\n\n{briefing_content}\n\n--- LEAD-DETAILS ---\nName: {lead.name}\nInstagram: {lead.instagram}\nWebsite: {lead.website or 'Nicht angegeben'}\nFokus: {lead.fokus}"
        
        send_email(subject, full_content)
        
    except Exception as e:
        print(f"DEBUG: Gemini Error: {str(e)}")

# ── API Endpoints ─────────────────────────────────────

@app.post("/api/qualify")
async def qualify_lead(lead: LeadData, background_tasks: BackgroundTasks):
    # Start the KI qualification and email process in the background
    background_tasks.add_task(process_and_notify_lead, lead)
    
    return JSONResponse(content={
        "status": "success",
        "message": "Lead-Daten empfangen. Qualifizierung läuft im Hintergrund."
    })

# ── Static Files ────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
