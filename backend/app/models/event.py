"""Event table — the normalized, unified record all reasoning modules consume."""
import uuid
from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from app.db import Base


def _uuid():
    return str(uuid.uuid4())


class Event(Base):
    __tablename__ = "events"

    event_id = Column(String, primary_key=True, default=lambda: f"EVT-{_uuid()[:8]}")
    evidence_id = Column(String, ForeignKey("evidence.evidence_id"), nullable=False)
    case_id = Column(String, ForeignKey("cases.case_id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    actor = Column(String, nullable=True)
    device = Column(String, nullable=True)
    action = Column(String, nullable=False)
    object = Column(String, nullable=True)
    location = Column(String, nullable=True)
    source = Column(String, nullable=False)
    confidence = Column(Float, default=1.0)
