"""
Correlation engine — groups events by shared actor/device within a
rolling time window into incident clusters.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any

DEFAULT_WINDOW_MINUTES = 15


def correlate_events(events: List[Dict[str, Any]], window_minutes: int = DEFAULT_WINDOW_MINUTES) -> List[Dict[str, Any]]:
    sorted_events = sorted(events, key=lambda e: e["timestamp"])
    window = timedelta(minutes=window_minutes)
    clusters: List[Dict[str, Any]] = []

    for event in sorted_events:
        ts = _parse_ts(event["timestamp"])
        actor = event.get("actor")
        device = event.get("device")

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

    for c in clusters:
        c["sources_involved"] = sorted(c["sources_involved"])

    return clusters


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))
