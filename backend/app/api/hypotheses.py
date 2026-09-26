"""Hypotheses endpoint, reading real Event rows from the DB."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.event import Event as EventModel
from app.contradiction.engine import detect_contradictions
from app.hypotheses.engine import generate_hypotheses

router = APIRouter(prefix="/api/cases", tags=["hypotheses"])


def _serialize(e: EventModel) -> dict:
    return {
        "event_id": e.event_id, "evidence_id": e.evidence_id, "case_id": e.case_id,
        "timestamp": e.timestamp.isoformat(), "actor": e.actor, "device": e.device,
        "action": e.action, "object": e.object, "location": e.location,
        "source": e.source, "confidence": e.confidence,
    }


@router.get("/{case_id}/hypotheses")
def get_hypotheses(case_id: str, db: Session = Depends(get_db)):
    events = [_serialize(e) for e in db.query(EventModel).filter(EventModel.case_id == case_id).all()]
    contradictions = detect_contradictions(events)
    return generate_hypotheses(events, contradictions)
