from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class LeadData(BaseModel):
    name: str
    instagram: str
    website: Optional[str] = None
    fokus: str
    datum: str
    momente: str
    investitionsrahmen: str


class TrackingEvent(BaseModel):
    event: str = Field(min_length=1)
    session_id: Optional[str] = None
    lead_id: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("event")
    @classmethod
    def event_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("event must not be blank")
        return cleaned
