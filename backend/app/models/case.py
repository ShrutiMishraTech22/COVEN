"""Case table."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from app.db import Base


def _uuid():
    return str(uuid.uuid4())


class Case(Base):
    __tablename__ = "cases"

    case_id = Column(String, primary_key=True, default=lambda: f"CASE-{_uuid()[:8]}")
    name = Column(String, nullable=False)
    investigator = Column(String, nullable=False)
    description = Column(String, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
