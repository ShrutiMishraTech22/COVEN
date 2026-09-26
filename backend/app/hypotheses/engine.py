"""
Hypothesis engine — scores competing incident explanations against
evidence patterns. Rule-based by design (explainability over black-box).
"""
from typing import List, Dict, Any

HYPOTHESIS_TEMPLATES = [
    {"hypothesis_id": "HYP-EXFIL", "description": "Potential Data Exfiltration",
     "supporting_actions": ["usb_connect", "file_access", "archive_create", "network_connect", "email_sent"],
     "contradicting_actions": ["backup_software_detected"],
     "missing_by_default": ["mail server logs", "destination IP confirmation"]},
    {"hypothesis_id": "HYP-BACKUP", "description": "Legitimate Backup",
     "supporting_actions": ["usb_connect", "backup_software_detected"],
     "contradicting_actions": ["network_connect", "email_sent"],
     "missing_by_default": ["backup schedule logs", "IT department confirmation"]},
    {"hypothesis_id": "HYP-SYNC", "description": "Automated Synchronization",
     "supporting_actions": ["cloud_sync_process"],
     "contradicting_actions": ["usb_connect", "manual_file_access"],
     "missing_by_default": ["sync service audit log"]},
]


def generate_hypotheses(events: List[Dict[str, Any]], contradictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions_present = {e["action"] for e in events}
    contradicting_evidence_ids = {eid for c in contradictions for eid in c["evidence_ids"]}

    results = []
    for template in HYPOTHESIS_TEMPLATES:
        supporting = [a for a in template["supporting_actions"] if a in actions_present]
        contradicting = [a for a in template["contradicting_actions"] if a in actions_present]

        total_signals = len(template["supporting_actions"])
        confidence = len(supporting) / total_signals if total_signals else 0.0
        confidence -= 0.15 * len(contradicting)
        confidence = max(0.0, min(1.0, confidence))

        supporting_evidence = [e["evidence_id"] for e in events if e["action"] in supporting]
        tainted = any(eid in contradicting_evidence_ids for eid in supporting_evidence)
        reliability = confidence * (0.7 if tainted else 1.0)

        results.append({
            "hypothesis_id": template["hypothesis_id"],
            "description": template["description"],
            "confidence": round(confidence, 3),
            "reliability": round(reliability, 3),
            "supporting_evidence": supporting_evidence,
            "contradicting_evidence": [e["evidence_id"] for e in events if e["action"] in contradicting],
            "missing_evidence": template["missing_by_default"],
            "explanation": _build_explanation(template, supporting, contradicting),
        })

    return sorted(results, key=lambda h: h["confidence"], reverse=True)


def _build_explanation(template, supporting, contradicting) -> str:
    parts = [f"Matched signals: {', '.join(supporting) if supporting else 'none'}."]
    if contradicting:
        parts.append(f"Contradicting signals present: {', '.join(contradicting)}.")
    return " ".join(parts)
