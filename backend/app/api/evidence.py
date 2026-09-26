"""
Evidence endpoints. Mounted at /api/evidence in main.py.

Handles: real SHA-256 hashing, saving the raw file to disk, type
detection by extension, EXIF extraction for images, persisting the
Evidence row, AND — the piece that was previously missing — parsing
log-type evidence into normalized Event rows via log_processor, with
provenance tracked at each transformation step via tracker.
"""
from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, Form, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.evidence import Evidence as EvidenceModel
from app.models.event import Event as EventModel
from app.utils.hashing import sha256_of_file
from app.processors.image_processor import extract_image_metadata
from app.processors.log_processor import parse_log_file
from app.provenance.tracker import record_transformation
from sqlalchemy.orm.attributes import flag_modified

router = APIRouter(prefix="/api/evidence", tags=["evidence"])

STORAGE_DIR = Path(__file__).resolve().parents[3] / "data" / "evidence"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
LOG_EXTENSIONS = {".json", ".log"}


def _detect_type_and_metadata(filename: str, file_bytes: bytes) -> tuple[str, dict]:
    ext = Path(filename).suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return "image", extract_image_metadata(file_bytes)
    if ext == ".pdf":
        return "document", {}
    if ext in LOG_EXTENSIONS or ext == ".csv" or ext == ".txt":
        return "log", {}
    if ext in (".eml", ".msg"):
        return "email", {}
    return "file", {}


def _serialize_evidence(e: EvidenceModel) -> dict:
    return {
        "evidence_id": e.evidence_id, "case_id": e.case_id, "source": e.source,
        "type": e.type, "original_filename": e.original_filename,
        "timestamp": e.timestamp.isoformat(), "hash": e.hash,
        "metadata": e.metadata_json, "integrity_status": e.integrity_status,
        "transformation_history": e.transformation_history,
    }


@router.post("/upload")
async def upload_evidence(
    case_id: str = Form(...),
    source: str = Form(...),
    file: UploadFile = None,
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()
    file_hash = sha256_of_file(file_bytes)

    dest_path = STORAGE_DIR / f"{file_hash.split(':')[1][:16]}_{file.filename}"
    with open(dest_path, "wb") as f:
        f.write(file_bytes)

    evidence_type, metadata = _detect_type_and_metadata(file.filename, file_bytes)

    evidence = EvidenceModel(
        case_id=case_id,
        source=source,
        type=evidence_type,
        original_filename=file.filename,
        storage_path=str(dest_path),
        timestamp=datetime.now(timezone.utc),
        hash=file_hash,
        metadata_json=metadata,
        acquisition_info={"collector": "system"},
        transformation_history=[],
        integrity_status="verified",
    )
    record_transformation(evidence, "hashed_and_stored")
    flag_modified(evidence, "transformation_history")

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    # --- the previously-missing integration step ---
    # If this is log-type evidence, parse it into normalized Event rows
    # and persist them, so the reasoning engine can run on real data.
    events_created = 0
    if evidence_type == "log":
        try:
            parsed_events = parse_log_file(file_bytes, evidence.evidence_id, source)
            for pe in parsed_events:
                if not pe.get("timestamp") or not pe.get("action"):
                    continue  # skip malformed records rather than failing the whole upload
                db.add(EventModel(
                    evidence_id=evidence.evidence_id,
                    case_id=case_id,
                    timestamp=datetime.fromisoformat(pe["timestamp"].replace("Z", "+00:00")),
                    actor=pe.get("actor"),
                    device=pe.get("device"),
                    action=pe["action"],
                    object=pe.get("object"),
                    location=pe.get("location"),
                    source=source,
                    confidence=1.0,
                ))
                events_created += 1
            record_transformation(evidence, f"parsed_and_normalized ({events_created} events)")
            flag_modified(evidence, "transformation_history")
            db.commit()
            db.refresh(evidence)
        except ValueError as exc:
            record_transformation(evidence, f"parse_failed: {exc}")
            db.commit()

    result = _serialize_evidence(evidence)
    result["events_created"] = events_created
    return result


@router.get("")
def list_evidence(case_id: str, db: Session = Depends(get_db)):
    items = db.query(EvidenceModel).filter(EvidenceModel.case_id == case_id).all()
    return [_serialize_evidence(e) for e in items]


@router.get("/{evidence_id}")
def get_evidence(evidence_id: str, db: Session = Depends(get_db)):
    e = db.query(EvidenceModel).filter(EvidenceModel.evidence_id == evidence_id).first()
    if not e:
        return {"error": "evidence not found"}
    return _serialize_evidence(e)


@router.get("/{evidence_id}/provenance")
def get_provenance(evidence_id: str, db: Session = Depends(get_db)):
    e = db.query(EvidenceModel).filter(EvidenceModel.evidence_id == evidence_id).first()
    if not e:
        return {"error": "evidence not found"}
    return {
        "evidence_id": e.evidence_id,
        "transformation_history": e.transformation_history,
        "hash": e.hash,
        "integrity_status": e.integrity_status,
    }
