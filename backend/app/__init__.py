"""
Import every real model here so app.db.init_db() (which calls
Base.metadata.create_all) knows about all tables — SQLAlchemy only
creates tables for models it has actually seen imported.
"""
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.event import Event

__all__ = ["Case", "Evidence", "Event"]
