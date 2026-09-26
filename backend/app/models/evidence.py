"""Evidence table."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from app.db import Base


def _uuid():
    return str(uuid.uuid4())


class Evidence(Base):
    __tablename__ = "evidence"

    evidence_id = Column(String, primary_key=True, default=lambda: f"EV-{_uuid()[:8]}")
    case_id = Column(String, ForeignKey("cases.case_id"), nullable=False)
    source = Column(String, nullable=False)
    type = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    hash = Column(String, nullable=False)
    metadata_json = Column(JSON, default=dict)
    acquisition_info = Column(JSON, default=dict)
    transformation_history = Column(JSON, default=list)
    integrity_status = Column(String, default="verified")
