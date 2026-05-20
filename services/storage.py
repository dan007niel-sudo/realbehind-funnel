import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from schemas import LeadData, TrackingEvent


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LeadRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_schema(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS leads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        instagram TEXT NOT NULL,
                        website TEXT,
                        fokus TEXT NOT NULL,
                        datum TEXT NOT NULL,
                        momente TEXT NOT NULL,
                        investitionsrahmen TEXT NOT NULL,
                        status TEXT NOT NULL,
                        briefing TEXT,
                        error TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                existing_columns = {
                    row["name"]
                    for row in connection.execute("PRAGMA table_info(leads)").fetchall()
                }
                if "privacy_consent" not in existing_columns:
                    connection.execute(
                        "ALTER TABLE leads ADD COLUMN privacy_consent INTEGER NOT NULL DEFAULT 0"
                    )
                if "consent_timestamp" not in existing_columns:
                    connection.execute("ALTER TABLE leads ADD COLUMN consent_timestamp TEXT")
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tracking_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event TEXT NOT NULL,
                        session_id TEXT,
                        lead_id INTEGER,
                        metadata TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )

    def create_lead(self, lead: LeadData) -> int:
        now = utc_now()
        consent_timestamp = lead.consent_timestamp or now
        with closing(self._connect()) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO leads (
                        name, instagram, website, fokus, datum, momente,
                        investitionsrahmen, privacy_consent, consent_timestamp,
                        status, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        lead.name,
                        lead.instagram,
                        lead.website,
                        lead.fokus,
                        lead.datum,
                        lead.momente,
                        lead.investitionsrahmen,
                        1 if lead.privacy_consent else 0,
                        consent_timestamp,
                        "received",
                        now,
                        now,
                    ),
                )
                return int(cursor.lastrowid)

    def update_lead_status(
        self,
        lead_id: int,
        status: str,
        *,
        briefing: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    UPDATE leads
                    SET status = ?, briefing = COALESCE(?, briefing), error = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (status, briefing, error, utc_now(), lead_id),
                )

    def get_lead(self, lead_id: int) -> dict[str, Any]:
        with closing(self._connect()) as connection:
            row = connection.execute(
                    "SELECT * FROM leads WHERE id = ?",
                    (lead_id,),
                ).fetchone()
        if row is None:
            raise KeyError(f"Lead {lead_id} not found")
        return dict(row)

    def record_event(self, event: TrackingEvent) -> int:
        with closing(self._connect()) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO tracking_events (event, session_id, lead_id, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        event.event,
                        event.session_id,
                        event.lead_id,
                        json.dumps(event.metadata, ensure_ascii=False),
                        utc_now(),
                    ),
                )
                return int(cursor.lastrowid)

    def list_events(self) -> list[dict[str, Any]]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                    "SELECT * FROM tracking_events ORDER BY id ASC"
                ).fetchall()
        events = []
        for row in rows:
            item = dict(row)
            item["metadata"] = json.loads(item["metadata"])
            events.append(item)
        return events
