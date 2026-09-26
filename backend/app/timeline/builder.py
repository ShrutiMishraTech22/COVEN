"""Timeline builder — chronological event ordering, grouped incident phases."""
from typing import List, Dict, Any


def build_timeline(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(events, key=lambda e: e["timestamp"])
