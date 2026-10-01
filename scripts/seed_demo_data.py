"""
Uploads every per-source synthetic file to a running COVEN backend,
tagging each with its correct source. Run this AFTER starting the
backend (uvicorn app.main:app --reload --port 8000).

Usage: python scripts/seed_demo_data.py
"""
import requests

BASE_URL = "http://localhost:8000/api"
SYNTHETIC_DIR = "data/synthetic"

SOURCE_FILES = {
    "laptop": "laptop.json",
    "usb": "usb.json",
    "network": "network.json",
    "email": "email.json",
    "phone": "phone.json",
}


def main():
    r = requests.post(f"{BASE_URL}/cases", data={
        "name": "Exfiltration Investigation",
        "investigator": "Shruti",
        "description": "Seeded demo case for COVEN"
    })
    r.raise_for_status()
    case_id = r.json()["case_id"]
    print(f"Case created: {case_id}")

    for source, filename in SOURCE_FILES.items():
        path = f"{SYNTHETIC_DIR}/{filename}"
        with open(path, "rb") as f:
            r = requests.post(
                f"{BASE_URL}/evidence/upload",
                data={"case_id": case_id, "source": source},
                files={"file": (filename, f, "application/json")},
            )
        r.raise_for_status()
        print(f"  {source}: {r.json()['events_created']} events uploaded")

    print()
    print(f"Done. Case ID: {case_id}")
    print(f"Check results at:")
    print(f"  {BASE_URL}/cases/{case_id}/contradictions")
    print(f"  {BASE_URL}/cases/{case_id}/findings")
    print(f"  {BASE_URL}/cases/{case_id}/hypotheses")


if __name__ == "__main__":
    main()