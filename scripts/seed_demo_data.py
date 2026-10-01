"""
Seed reproducible demo data for COVEN.

Run from the project root:

    python scripts/seed_demo_data.py

The script is idempotent: running it again replaces only the
records belonging to CASE-DEMO-001.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


# Allow imports from backend/app when this script is run from the
# project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from app.db import SessionLocal, init_db
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.event import Event


CASE_ID = "CASE-DEMO-001"
EVIDENCE_ID = "EV-DEMO-001"

EVENT_IDS = [
    "EVT-DEMO-001",
    "EVT-DEMO-002",
    "EVT-DEMO-003",
]


def seed_demo_data():
    init_db()

    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # 1. Remove only previously seeded demo records
        # ---------------------------------------------------------

        db.query(Event).filter(
            Event.event_id.in_(EVENT_IDS)
        ).delete(synchronize_session=False)

        db.query(Evidence).filter(
            Evidence.evidence_id == EVIDENCE_ID
        ).delete(synchronize_session=False)

        db.query(Case).filter(
            Case.case_id == CASE_ID
        ).delete(synchronize_session=False)

        db.commit()

        # ---------------------------------------------------------
        # 2. Create demo case
        # ---------------------------------------------------------

        demo_case = Case(
            case_id=CASE_ID,
            name="Data Exfiltration Investigation",
            investigator="COVEN Demo Investigator",
            description=(
                "Demo investigation showing evidence ingestion, "
                "event extraction, timeline reconstruction, "
                "graph relationships, findings, and hypotheses."
            ),
            created_at=datetime.fromisoformat(
                "2026-09-28T10:00:00"
            ),
        )

        db.add(demo_case)

        # ---------------------------------------------------------
        # 3. Create demo evidence
        # ---------------------------------------------------------

        demo_evidence = Evidence(
            evidence_id=EVIDENCE_ID,
            case_id=CASE_ID,
            source="WORKSTATION_01",
            type="log",
            original_filename="workstation_demo.json",
            storage_path="data/evidence/workstation_demo.json",
            timestamp=datetime.fromisoformat(
                "2026-09-28T10:15:00"
            ),
            hash=(
                "demo-sha256-workstation-001"
            ),
            metadata_json=json.dumps({
                "device": "WORKSTATION-01",
                "format": "json",
                "description": "Synthetic workstation activity log",
            }),
            acquisition_info=json.dumps({
                "method": "COVEN demo seed",
                "collector": "COVEN",
            }),
            transformation_history=json.dumps([
                {
                    "action": "evidence_ingested",
                    "timestamp": "2026-09-28T10:15:00",
                },
                {
                    "action": "log_parsed",
                    "timestamp": "2026-09-28T10:15:01",
                },
            ]),
            integrity_status="verified",
        )

        db.add(demo_evidence)

        # ---------------------------------------------------------
        # 4. Create normalized events
        # ---------------------------------------------------------

        demo_events = [
            Event(
                event_id="EVT-DEMO-001",
                evidence_id=EVIDENCE_ID,
                case_id=CASE_ID,
                timestamp=datetime.fromisoformat(
                    "2026-09-28T10:15:00"
                ),
                actor="alice",
                device="WORKSTATION-01",
                action="login",
                object="system",
                location="Delhi",
                source="WORKSTATION_01",
                confidence=1.0,
            ),
            Event(
                event_id="EVT-DEMO-002",
                evidence_id=EVIDENCE_ID,
                case_id=CASE_ID,
                timestamp=datetime.fromisoformat(
                    "2026-09-28T10:20:00"
                ),
                actor="alice",
                device="WORKSTATION-01",
                action="file_access",
                object="confidential.pdf",
                location="Delhi",
                source="WORKSTATION_01",
                confidence=1.0,
            ),
            Event(
                event_id="EVT-DEMO-003",
                evidence_id=EVIDENCE_ID,
                case_id=CASE_ID,
                timestamp=datetime.fromisoformat(
                    "2026-09-28T10:25:00"
                ),
                actor="alice",
                device="WORKSTATION-01",
                action="file_copy",
                object="confidential.pdf",
                location="Delhi",
                source="WORKSTATION_01",
                confidence=1.0,
            ),
        ]

        db.add_all(demo_events)

        # ---------------------------------------------------------
        # 5. Commit everything
        # ---------------------------------------------------------

        db.commit()

        print()
        print("COVEN demo data seeded successfully.")
        print()
        print(f"Case:     {CASE_ID}")
        print(f"Evidence: {EVIDENCE_ID}")
        print("Events:")
        for event_id in EVENT_IDS:
            print(f"  - {event_id}")
        print()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()