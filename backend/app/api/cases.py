"""Case endpoints. Mounted at /api/cases in main.py."""
from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.case import Case as CaseModel

router = APIRouter(prefix="/api/cases", tags=["cases"])


def _serialize(case: CaseModel) -> dict:
    return {
        "case_id": case.case_id, "name": case.name, "investigator": case.investigator,
        "description": case.description, "created_at": case.created_at.isoformat(),
    }


@router.post("")
def create_case(name: str = Form(...), investigator: str = Form(...),
                 description: str = Form(""), db: Session = Depends(get_db)):
    case = CaseModel(name=name, investigator=investigator, description=description)
    db.add(case)
    db.commit()
    db.refresh(case)
    return _serialize(case)


@router.get("")
def list_cases(db: Session = Depends(get_db)):
    return [_serialize(c) for c in db.query(CaseModel).all()]


@router.get("/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(CaseModel).filter(CaseModel.case_id == case_id).first()
    if not case:
        return {"error": "case not found"}
    return _serialize(case)
