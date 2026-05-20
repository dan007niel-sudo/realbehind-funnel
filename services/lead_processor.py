from schemas import LeadData
from services.email import send_email
from services.gemini import generate_briefing
from services.storage import LeadRepository


def build_raw_lead_email(lead: LeadData) -> str:
    return (
        "--- LEAD-DETAILS ---\n"
        f"Name: {lead.name}\n"
        f"Instagram: {lead.instagram}\n"
        f"Website: {lead.website or 'Nicht angegeben'}\n"
        f"Fokus: {lead.fokus}\n"
        f"Datum/Zeitraum: {lead.datum}\n"
        f"Wichtige Momente: {lead.momente}\n"
        f"Investitionsrahmen: {lead.investitionsrahmen}"
    )


async def process_and_notify_lead(
    lead_id: int,
    lead: LeadData,
    repository: LeadRepository,
    *,
    google_api_key: str,
    gemini_model: str,
    smtp_server: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    notification_email: str,
) -> None:
    briefing_content = ""
    if google_api_key:
        try:
            briefing_content = generate_briefing(
                lead,
                api_key=google_api_key,
                model=gemini_model,
            )
            repository.update_lead_status(lead_id, "briefed", briefing=briefing_content)
        except Exception as exc:
            repository.update_lead_status(lead_id, "briefing_failed", error=str(exc))
            print(f"DEBUG: Gemini Error: {str(exc)}")
    else:
        repository.update_lead_status(lead_id, "briefing_skipped")

    subject = f"Neuer Lead Qualifiziert: {lead.name} ({lead.fokus})"
    if briefing_content:
        full_content = (
            f"--- INTERNES BRIEFING ---\n\n{briefing_content}\n\n"
            f"{build_raw_lead_email(lead)}"
        )
    else:
        full_content = (
            "--- INTERNES BRIEFING ---\n\n"
            "Automatische KI-Aufbereitung war nicht verfügbar. Rohdaten des Leads:\n\n"
            f"{build_raw_lead_email(lead)}"
        )

    sent = send_email(
        subject,
        full_content,
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        notification_email=notification_email,
    )
    repository.update_lead_status(lead_id, "email_sent" if sent else "email_skipped")
