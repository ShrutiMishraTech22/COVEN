"""
Contradiction engine — the core novelty.

For each pair of events involving the SAME actor, check for disagreement.
Each rule is deliberately simple and explainable (rule-based over
black-box, per project's research-backed design decision).
"""
from datetime import datetime, timedelta
from itertools import combinations
from typing import List, Dict, Any

SIMULTANEITY_WINDOW_MINUTES = 5


def detect_contradictions(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    contradictions = []
    counter = 1

    by_actor: Dict[str, List[Dict[str, Any]]] = {}
    for e in events:
        by_actor.setdefault(e.get("actor"), []).append(e)

    for actor, actor_events in by_actor.items():
        if actor is None or len(actor_events) < 2:
            continue

        for e1, e2 in combinations(actor_events, 2):
            if e1["source"] == e2["source"]:
                continue

            t1, t2 = _parse_ts(e1["timestamp"]), _parse_ts(e2["timestamp"])
            simultaneous = abs((t1 - t2)) <= timedelta(minutes=SIMULTANEITY_WINDOW_MINUTES)

            loc1, loc2 = e1.get("location"), e2.get("location")
            if simultaneous and loc1 and loc2 and loc1 != loc2:
                contradictions.append(_make_contradiction(
                    counter, "location", "high",
                    [e1["evidence_id"], e2["evidence_id"]],
                    f"{actor}: {e1['source']} shows {loc1}, {e2['source']} shows {loc2} "
                    f"at ~{e1['timestamp']}",
                    ["VPN or proxy", "timestamp mismatch", "device relocation",
                     "account sharing", "GPS inaccuracy"]
                ))
                counter += 1

            if _violates_expected_order(e1, e2):
                contradictions.append(_make_contradiction(
                    counter, "temporal", "medium",
                    [e1["evidence_id"], e2["evidence_id"]],
                    f"{actor}: '{e2['action']}' logged before '{e1['action']}', "
                    f"which is out of expected sequence",
                    ["clock drift between systems", "log delay", "manual timestamp edit"]
                ))
                counter += 1

            dev1, dev2 = e1.get("device"), e2.get("device")
            if simultaneous and dev1 and dev2 and dev1 != dev2 and e1["source"] == "network" and e2["source"] == "network":
                contradictions.append(_make_contradiction(
                    counter, "identity", "medium",
                    [e1["evidence_id"], e2["evidence_id"]],
                    f"{actor}: simultaneous network activity from two different devices "
                    f"({dev1} and {dev2})",
                    ["account sharing", "credential compromise", "concurrent sessions"]
                ))
                counter += 1

    return contradictions


def _violates_expected_order(e1: Dict[str, Any], e2: Dict[str, Any]) -> bool:
    order_rules = {("email_sent", "file_access"): False}
    pair = (e1["action"], e2["action"])
    if pair in order_rules:
        t1, t2 = _parse_ts(e1["timestamp"]), _parse_ts(e2["timestamp"])
        if t1 < t2:
            return True
    return False


def _make_contradiction(counter, ctype, severity, evidence_ids, description, explanations):
    return {
        "contradiction_id": f"CONTRA-{counter:03d}",
        "type": ctype,
        "severity": severity,
        "evidence_ids": evidence_ids,
        "description": description,
        "possible_explanations": explanations,
    }


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))
