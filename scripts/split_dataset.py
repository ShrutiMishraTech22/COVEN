"""
One-time script: splits data/synthetic/laptop.json (the combined
multi-source file) into separate per-source files, since contradiction
detection only works when each source is uploaded separately.

Run from the repo root: python scripts/split_dataset.py
"""
import json
from pathlib import Path

SYNTHETIC_DIR = Path("data/synthetic")
COMBINED_FILE = SYNTHETIC_DIR / "laptop_scenario.json"

with open(COMBINED_FILE) as f:
    events = json.load(f)

by_source = {}
for e in events:
    source = e["source"]
    # strip fields that get regenerated on upload anyway
    clean_event = {
        "timestamp": e["timestamp"],
        "actor": e["actor"],
        "device": e["device"],
        "action": e["action"],
        "object": e["object"],
        "location": e["location"],
    }
    by_source.setdefault(source, []).append(clean_event)

for source, evs in by_source.items():
    out_path = SYNTHETIC_DIR / f"{source}.json"
    with open(out_path, "w") as f:
        json.dump(evs, f, indent=2)
    print(f"Wrote {out_path} — {len(evs)} event(s)")

# rename the original combined file so it's not confused with the new laptop.json
backup_path = SYNTHETIC_DIR / "combined_scenario_backup.json"
COMBINED_FILE.rename(backup_path)
print(f"\nOriginal combined file moved to {backup_path}")