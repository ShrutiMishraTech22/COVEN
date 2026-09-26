"""Evidence graph endpoint, reading real Event rows from the DB."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.event import Event as EventModel
from app.graph.builder import build_graph

router = APIRouter(prefix="/api/cases", tags=["graph"])


def _serialize(e: EventModel) -> dict:
    return {
        "actor": e.actor, "device": e.device, "action": e.action, "object": e.object,
    }


@router.get("/{case_id}/graph")
def get_graph(case_id: str, db: Session = Depends(get_db)):
    events = [_serialize(e) for e in db.query(EventModel).filter(EventModel.case_id == case_id).all()]
    return build_graph(events)
