"""
Correlation engine.

Logic: group Events that share an actor OR device, and fall within a
rolling time window, into a single "incident cluster". This is what
lets scattered logs (laptop, USB, network, email) become one coherent
narrative instead of isolated rows.

No ML needed here — this is deliberately simple, explainable grouping.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any

# How far apart two events can be and still be considered "related".
# Tune this per case type — exfiltration incidents tend to unfold over
# minutes, not hours.
DEFAULT_WINDOW_MINUTES = 15


def correlate_events(events: List[Dict[str, Any]], window_minutes: int = DEFAULT_WINDOW_MINUTES) -> List[Dict[str, Any]]:
    """
    events: list of Event dicts (see schemas.Event) sorted or unsorted.
    Returns: list of clusters, each cluster a dict:
        {
            "cluster_id": "CLUSTER-1",
            "actor": "employee_a",
            "event_ids": [...],
            "start": iso timestamp,
            "end": iso timestamp,
            "sources_involved": ["laptop", "usb", "network", "email"]
        }
    """
    sorted_events = sorted(events, key=lambda e: e["timestamp"])
    window = timedelta(minutes=window_minutes)

    clusters: List[Dict[str, Any]] = []

    for event in sorted_events:
        ts = _parse_ts(event["timestamp"])
        actor = event.get("actor")
        device = event.get("device")

        # Try to attach this event to an existing open cluster for the
        # same actor/device where the time gap is still within the window.
        attached = False
        for cluster in clusters:
            same_entity = cluster["actor"] == actor or cluster.get("device") == device
            within_window = ts - _parse_ts(cluster["end"]) <= window
            if same_entity and within_window:
                cluster["event_ids"].append(event["event_id"])
                cluster["end"] = event["timestamp"]
                cluster["sources_involved"].add(event["source"])
                attached = True
                break

        if not attached:
            clusters.append({
                "cluster_id": f"CLUSTER-{len(clusters) + 1}",
                "actor": actor,
                "device": device,
                "event_ids": [event["event_id"]],
                "start": event["timestamp"],
                "end": event["timestamp"],
                "sources_involved": {event["source"]},
            })

    # Convert sets to lists for JSON serialization
    for c in clusters:
        c["sources_involved"] = sorted(c["sources_involved"])

    return clusters


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))
