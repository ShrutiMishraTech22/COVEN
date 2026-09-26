"""
Contradiction engine.

Logic: for each pair of events involving the SAME actor, check for
disagreement. Each rule below is deliberately simple and explainable —
that's the point (see research paper 3: rule/graph-based explanations
beat black-box for forensic trust).

Start with these 3 rule types. Add more only if time allows — location
mismatch is your strongest demo case.
"""
from datetime import datetime, timedelta
from itertools import combinations
from typing import List, Dict, Any

# Two events at "the same time" if within this many minutes of each other.
SIMULTANEITY_WINDOW_MINUTES = 5


def detect_contradictions(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    contradictions = []
    counter = 1

    # Group events by actor first — contradictions only make sense
    # when comparing the SAME person/account across sources.
    by_actor: Dict[str, List[Dict[str, Any]]] = {}
    for e in events:
        by_actor.setdefault(e.get("actor"), []).append(e)

    for actor, actor_events in by_actor.items():
        if actor is None or len(actor_events) < 2:
            continue

        for e1, e2 in combinations(actor_events, 2):
            if e1["source"] == e2["source"]:
                continue  # only cross-source disagreement counts

            t1, t2 = _parse_ts(e1["timestamp"]), _parse_ts(e2["timestamp"])
            simultaneous = abs((t1 - t2)) <= timedelta(minutes=SIMULTANEITY_WINDOW_MINUTES)

            # Rule 1: LOCATION contradiction
            # Same actor, same/overlapping time, different location.
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

            # Rule 2: TEMPORAL contradiction
            # An event that should logically follow another instead
            # precedes it (e.g. "email sent" before "file accessed").
            if _violates_expected_order(e1, e2):
                contradictions.append(_make_contradiction(
                    counter, "temporal", "medium",
                    [e1["evidence_id"], e2["evidence_id"]],
                    f"{actor}: '{e2['action']}' logged before '{e1['action']}', "
                    f"which is out of expected sequence",
                    ["clock drift between systems", "log delay", "manual timestamp edit"]
                ))
                counter += 1

            # Rule 3: IDENTITY contradiction
            # Same account, but device fingerprint changes implausibly
            # fast, or a device is used that isn't registered to the actor.
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
    """
    Very small ordering rulebook — extend as needed.
    Example: 'email_sent' should never precede 'file_access' for the
    same actor if they reference the same object/file.
    """
    order_rules = {
        ("email_sent", "file_access"): False,  # email_sent should come AFTER file_access
    }
    pair = (e1["action"], e2["action"])
    if pair in order_rules:
        expected_after = order_rules[pair] is False
        t1, t2 = _parse_ts(e1["timestamp"]), _parse_ts(e2["timestamp"])
        if expected_after and t1 < t2:
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
