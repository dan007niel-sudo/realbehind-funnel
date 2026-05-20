from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import config
from schemas import LeadData, TrackingEvent
from services.lead_processor import process_and_notify_lead
from services.storage import LeadRepository


app = FastAPI(title="RealBehind Lead-Funnel API", version="1.2.0")

# Re-exported for existing tests and local checks that patch these values.
GOOGLE_API_KEY = config.GOOGLE_API_KEY
GEMINI_MODEL = config.GEMINI_MODEL
SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
SMTP_USER = config.SMTP_USER
SMTP_PASSWORD = config.SMTP_PASSWORD
NOTIFICATION_EMAIL = config.NOTIFICATION_EMAIL

lead_repository = LeadRepository(config.LEADS_DB_PATH)


@app.post("/api/qualify")
async def qualify_lead(lead: LeadData, background_tasks: BackgroundTasks):
    lead_id = lead_repository.create_lead(lead)
    background_tasks.add_task(
        process_and_notify_lead,
        lead_id,
        lead,
        lead_repository,
        google_api_key=GOOGLE_API_KEY,
        gemini_model=GEMINI_MODEL,
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
        smtp_user=SMTP_USER,
        smtp_password=SMTP_PASSWORD,
        notification_email=NOTIFICATION_EMAIL,
    )

    return JSONResponse(
        content={
            "status": "success",
            "lead_id": lead_id,
            "message": "Lead-Daten empfangen. Qualifizierung läuft im Hintergrund.",
        }
    )


@app.post("/api/events")
async def record_event(event: TrackingEvent):
    event_id = lead_repository.record_event(event)
    return {"status": "success", "event_id": event_id}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "realbehind-funnel"}


app.mount("/static", StaticFiles(directory=config.BASE_DIR / "static"), name="static")


@app.get("/")
async def root():
    return FileResponse(config.BASE_DIR / "static" / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
