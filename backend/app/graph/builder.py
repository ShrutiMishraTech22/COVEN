"""Evidence graph builder — turns a flat event list into nodes/edges."""
from typing import List, Dict, Any


def build_graph(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    nodes: Dict[str, Any] = {}
    edges = []
    for e in events:
        if e.get("actor") and e["actor"] not in nodes:
            nodes[e["actor"]] = {"id": e["actor"], "type": "person", "label": e["actor"]}
        if e.get("device") and e["device"] not in nodes:
            nodes[e["device"]] = {"id": e["device"], "type": "device", "label": e["device"]}
        if e.get("object") and e["object"] not in nodes:
            obj_type = "file" if e["action"] in ("file_access", "archive_create") else "entity"
            nodes[e["object"]] = {"id": e["object"], "type": obj_type, "label": e["object"]}

        if e.get("actor") and e.get("device"):
            edges.append({"source": e["actor"], "target": e["device"], "relation": "uses"})
        if e.get("device") and e.get("object"):
            edges.append({"source": e["device"], "target": e["object"], "relation": e["action"]})

    return {"nodes": list(nodes.values()), "edges": edges}
