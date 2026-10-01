"""Findings / reliability endpoint, reading real Event rows from the DB."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.event import Event as EventModel
from app.contradiction.engine import detect_contradictions
from app.reliability.scorer import compute_reliability, estimate_cross_source_agreement

router = APIRouter(prefix="/api/cases", tags=["analysis"])


def _serialize(e: EventModel) -> dict:
    return {
        "event_id": e.event_id, "evidence_id": e.evidence_id, "case_id": e.case_id,
        "timestamp": e.timestamp.isoformat(), "actor": e.actor, "device": e.device,
        "action": e.action, "object": e.object, "location": e.location,
        "source": e.source, "confidence": e.confidence,
    }


@router.get("/{case_id}/contradictions")
def get_contradictions(case_id: str, db: Session = Depends(get_db)):
    events = [_serialize(e) for e in db.query(EventModel).filter(EventModel.case_id == case_id).all()]
    return detect_contradictions(events)


@router.get("/{case_id}/findings")
def get_findings(case_id: str, db: Session = Depends(get_db)):
    events = [
        _serialize(e)
        for e in db.query(EventModel)
        .filter(EventModel.case_id == case_id)
        .order_by(EventModel.timestamp.asc())
        .all()
    ]

    if not events:
        return []

    actions = {
        (event.get("action") or "").lower()
        for event in events
    }

    required_actions = {
        "login",
        "file_access",
        "file_copy",
    }

    if not required_actions.issubset(actions):
        return []

    supporting_evidence = list(
        dict.fromkeys(
            event["evidence_id"]
            for event in events
            if event.get("evidence_id")
        )
    )

    contradictions = detect_contradictions(events)

    contradicting_evidence = list(
        dict.fromkeys(
            evidence_id
            for contradiction in contradictions
            for evidence_id in contradiction.get("evidence_ids", [])
        )
    )

    sources = list({
        event["source"]
        for event in events
        if event.get("source")
    })

    agreement = estimate_cross_source_agreement(
        len(contradictions),
        len(events),
    )

    result = compute_reliability(
        model_confidence=0.87,
        evidence_integrity=1.0,
        sources_involved=sources,
        cross_source_agreement=agreement,
        reproducibility=0.95,
    )

    return [{
        "finding_id": "FIND-001",
        "case_id": case_id,
        "model": "rule-engine",
        "model_version": "0.1",
        "confidence": 0.87,
        "supporting_evidence": supporting_evidence,
        "contradicting_evidence": contradicting_evidence,
        "provenance": {},
        **result,
        "explanation": (
            "A sequence of login, sensitive file access, and "
            "file copy activity was observed for the investigation."
        ),
    }]