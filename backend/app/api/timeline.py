"""Timeline + correlation endpoints, reading real Event rows from the DB."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.event import Event as EventModel
from app.timeline.builder import build_timeline
from app.correlation.engine import correlate_events

router = APIRouter(prefix="/api/cases", tags=["timeline"])


def _serialize(e: EventModel) -> dict:
    return {
        "event_id": e.event_id, "evidence_id": e.evidence_id, "case_id": e.case_id,
        "timestamp": e.timestamp.isoformat(), "actor": e.actor, "device": e.device,
        "action": e.action, "object": e.object, "location": e.location,
        "source": e.source, "confidence": e.confidence,
    }


@router.get("/{case_id}/timeline")
def get_timeline(case_id: str, db: Session = Depends(get_db)):
    events = [_serialize(e) for e in db.query(EventModel).filter(EventModel.case_id == case_id).all()]
    return build_timeline(events)


@router.get("/{case_id}/correlations")
def get_correlations(case_id: str, db: Session = Depends(get_db)):
    events = [_serialize(e) for e in db.query(EventModel).filter(EventModel.case_id == case_id).all()]
    return correlate_events(events)
