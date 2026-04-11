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
Du bist der Automatisierungs-Kern für "RealBehind". Die Marke steht für echte Momente, die man fühlt – ungestellte Behind-the-Scenes-Augenblicke bei Hochzeiten, Events und Markenauftritten.
Deine Aufgabe ist es, eingehende Leads (Brautpaare, Eventplaner, Creator) vorzuqualifizieren und ein kreatives Briefing sowie eine authentische Antwort-E-Mail zu generieren.

### KONTEXT
- Marke: RealBehind (Mission: Echtheit über Perfektion. Festhalten von Momenten, die sonst verloren gehen).
- Zielgruppe: Brautpaare, Eventveranstalter, Marken mit Fokus auf nahbaren Social Media Content.
- Tonfall: Empathisch, professionell, nahbar, kreativ.

### AUFGABE
Generiere zwei strukturierte Blöcke basierend auf den Lead-Daten:

1. BRIEFING (Intern für Daniel):
- Potenzial-Check: Welche Art von "unseen moments" oder BTS-Content wäre für diesen Anlass (Hochzeit, Event, Brand) besonders wertvoll?
- Kreativ-Idee: 1-2 erste Ideen für authentischen Content, den Daniel im Call als Inspiration pitchen kann.

2. BESTÄTIGUNGS-MAIL (Extern an Lead):
- Betreff: Echte Momente: Dein Kennenlernen mit Real Behind
- Text: Bestätigung des Gesprächs.
- Vorbereitung: Gib einen kurzen Impuls mit auf den Weg (z.B. "Überlege dir, welche 3 kleinen Momente dir an deinem Tag am wichtigsten sind, die auf gestellten Fotos oft fehlen.")
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
