"""
Reliability engine — separates model confidence from evidence
trustworthiness. Core philosophical differentiator of the project.
"""
from typing import Dict, Any, List

SOURCE_RELIABILITY = {
    "laptop": 0.95, "network": 0.90, "usb": 0.90, "email": 0.92,
    "phone": 0.75, "cctv": 0.80, "other": 0.60,
}


def compute_reliability(
    model_confidence: float,
    evidence_integrity: float,
    sources_involved: List[str],
    cross_source_agreement: float,
    reproducibility: float = 0.9,
) -> Dict[str, Any]:
    source_reliability = _average_source_reliability(sources_involved)

    breakdown = {
        "model_confidence": round(model_confidence, 3),
        "evidence_integrity": round(evidence_integrity, 3),
        "source_reliability": round(source_reliability, 3),
        "cross_source_agreement": round(cross_source_agreement, 3),
        "reproducibility": round(reproducibility, 3),
    }

    final = (model_confidence * evidence_integrity * source_reliability *
             cross_source_agreement * reproducibility)
    final_scaled = final ** (1 / 3)

    return {"reliability": round(final_scaled, 3), "reliability_breakdown": breakdown}


def _average_source_reliability(sources: List[str]) -> float:
    if not sources:
        return 0.5
    scores = [SOURCE_RELIABILITY.get(s, 0.6) for s in sources]
    return sum(scores) / len(scores)


def estimate_cross_source_agreement(contradiction_count: int, total_evidence: int) -> float:
    if total_evidence == 0:
        return 1.0
    penalty = min(contradiction_count / max(total_evidence, 1), 1.0)
    return round(1.0 - penalty, 3)
