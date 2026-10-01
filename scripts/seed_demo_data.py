"""
COVEN demo data utilities.

This script provides two seed workflows:

1. seed_local_demo()
   Creates the deterministic CASE-DEMO-001 dataset directly in SQLite.

2. upload_source_datasets()
   Uploads the per-source synthetic datasets to a running COVEN backend.

Run from the project root.

Local SQLite seed:
    python scripts/seed_demo_data.py local

API upload:
    python scripts/seed_demo_data.py upload
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import requests


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# ---------------------------------------------------------------------------
# API upload configuration
# ---------------------------------------------------------------------------

BASE_URL = "http://localhost:8000/api"
SYNTHETIC_DIR = PROJECT_ROOT / "data" / "synthetic"

SOURCE_FILES = {
    "laptop": "laptop.json",
    "usb": "usb.json",
    "network": "network.json",
    "email": "email.json",
    "phone": "phone.json",
}


# ---------------------------------------------------------------------------
# Local deterministic demo seed
# ---------------------------------------------------------------------------

def seed_local_demo():
    """
    Seed the deterministic CASE-DEMO-001 dataset directly into SQLite.

    The seed is idempotent: records belonging to CASE-DEMO-001 are removed
    before being recreated.
    """
    from app.db import SessionLocal
    from app.models.case import Case
    from app.models.evidence import Evidence
    from app.models.event import Event

    db = SessionLocal()

    try:
        case_id = "CASE-DEMO-001"
        evidence_id = "EV-DEMO-001"

        # Remove existing demo records first.
        db.query(Event).filter(Event.case_id == case_id).delete(
            synchronize_session=False
        )
        db.query(Evidence).filter(Evidence.case_id == case_id).delete(
            synchronize_session=False
        )
        db.query(Case).filter(Case.case_id == case_id).delete(
            synchronize_session=False
        )

        now = datetime.utcnow()

        case = Case(
            case_id=case_id,
            name="Data Exfiltration Investigation",
            investigator="COVEN Demo Investigator",
            description="Synthetic demo investigation for COVEN.",
            created_at=now,
        )
        db.add(case)

        evidence = Evidence(
            evidence_id=evidence_id,
            case_id=case_id,
            source="WORKSTATION_01",
            type="log",
            original_filename="workstation_demo.json",
            storage_path="data/evidence/workstation_demo.json",
            timestamp=now,
            hash="demo-sha256-workstation-001",
            metadata_json=json.dumps(
                {
                    "synthetic": True,
                    "scenario": "data_exfiltration",
                }
            ),
            acquisition_info=json.dumps(
                {
                    "method": "synthetic_seed",
                    "operator": "COVEN",
                }
            ),
            transformation_history=[],
            integrity_status="verified",
        )
        db.add(evidence)

        events = [
            Event(
                event_id="EVT-DEMO-001",
                evidence_id=evidence_id,
                case_id=case_id,
                timestamp=datetime.fromisoformat(
                    "2026-01-15T10:15:00"
                ),
                actor="alice",
                device="WORKSTATION-01",
                action="login",
                object="system",
                location="Delhi",
                source="WORKSTATION_01",
                confidence=0.99,
            ),
            Event(
                event_id="EVT-DEMO-002",
                evidence_id=evidence_id,
                case_id=case_id,
                timestamp=datetime.fromisoformat(
                    "2026-01-15T10:20:00"
                ),
                actor="alice",
                device="WORKSTATION-01",
                action="file_access",
                object="confidential.pdf",
                location="Delhi",
                source="WORKSTATION_01",
                confidence=0.95,
            ),
            Event(
                event_id="EVT-DEMO-003",
                evidence_id=evidence_id,
                case_id=case_id,
                timestamp=datetime.fromisoformat(
                    "2026-01-15T10:25:00"
                ),
                actor="alice",
                device="WORKSTATION-01",
                action="file_copy",
                object="confidential.pdf",
                location="Delhi",
                source="WORKSTATION_01",
                confidence=0.93,
            ),
        ]

        db.add_all(events)
        db.commit()

        print(f"Local demo seeded: {case_id}")
        print(f"Evidence: {evidence_id}")
        print(f"Events: {len(events)}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ---------------------------------------------------------------------------
# Per-source API upload
# ---------------------------------------------------------------------------

def upload_source_datasets():
    """
    Upload every per-source synthetic file to a running COVEN backend.
    """

    response = requests.post(
        f"{BASE_URL}/cases",
        data={
            "name": "Exfiltration Investigation",
            "investigator": "Shruti",
            "description": "Seeded demo case for COVEN",
        },
    )
    response.raise_for_status()

    case_id = response.json()["case_id"]
    print(f"Case created: {case_id}")

    for source, filename in SOURCE_FILES.items():
        path = SYNTHETIC_DIR / filename

        if not path.exists():
            raise FileNotFoundError(f"Synthetic dataset not found: {path}")

        with path.open("rb") as file:
            response = requests.post(
                f"{BASE_URL}/evidence/upload",
                data={
                    "case_id": case_id,
                    "source": source,
                },
                files={
                    "file": (
                        filename,
                        file,
                        "application/json",
                    )
                },
            )

        response.raise_for_status()

        result = response.json()
        print(
            f"  {source}: "
            f"{result.get('events_created', 0)} events uploaded"
        )

    print()
    print(f"Done. Case ID: {case_id}")
    print("Check results at:")
    print(f"  {BASE_URL}/cases/{case_id}/contradictions")
    print(f"  {BASE_URL}/cases/{case_id}/findings")
    print(f"  {BASE_URL}/cases/{case_id}/hypotheses")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/seed_demo_data.py local")
        print("  python scripts/seed_demo_data.py upload")
        return

    command = sys.argv[1].lower()

    if command == "local":
        seed_local_demo()
    elif command == "upload":
        upload_source_datasets()
    else:
        raise SystemExit(
            f"Unknown command: {command}. Use 'local' or 'upload'."
        )


if __name__ == "__main__":
    main()