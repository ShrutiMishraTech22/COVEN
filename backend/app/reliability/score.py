"""
Reliability engine — the core philosophical differentiator (see research
paper 2: computational reliabilism).

Model confidence is ONE input, not the whole answer. We combine it with
evidence integrity, source reliability, cross-source agreement, and
reproducibility into a separate, lower-trust-inflating number.

Every weight below is a hackathon-reasonable starting point — document
in your pitch that these are calibrated by domain expertise/data in a
real deployment, not fixed constants.
"""
from typing import Dict, Any, List

# Per-source trust weights — logs are generally more reliable than GPS,
# GPS more reliable than user-editable metadata, etc. Tune as needed.
SOURCE_RELIABILITY = {
    "laptop": 0.95,
    "network": 0.90,
    "usb": 0.90,
    "email": 0.92,
    "phone": 0.75,   # GPS/location data is noisier
    "cctv": 0.80,
    "other": 0.60,
}


def compute_reliability(
    model_confidence: float,
    evidence_integrity: float,
    sources_involved: List[str],
    cross_source_agreement: float,
    reproducibility: float = 0.9,
) -> Dict[str, Any]:
    """
    Returns the breakdown dict matching schemas.ReliabilityBreakdown,
    plus the final combined score.
    """
    source_reliability = _average_source_reliability(sources_involved)

    breakdown = {
        "model_confidence": round(model_confidence, 3),
        "evidence_integrity": round(evidence_integrity, 3),
        "source_reliability": round(source_reliability, 3),
        "cross_source_agreement": round(cross_source_agreement, 3),
        "reproducibility": round(reproducibility, 3),
    }

    # Weighted geometric-ish combination — deliberately NOT a simple
    # average, so that one very weak factor drags the score down hard.
    # This mirrors the blueprint's multiplicative formula (section 6).
    final = (
        model_confidence *
        evidence_integrity *
        source_reliability *
        cross_source_agreement *
        reproducibility
    )
    # Raw product shrinks fast with 5 factors — rescale so a case with
    # genuinely strong evidence still lands in a legible range.
    final_scaled = final ** (1 / 3)  # cube-root rescale, tune as needed

    return {
        "reliability": round(final_scaled, 3),
        "reliability_breakdown": breakdown,
    }


def _average_source_reliability(sources: List[str]) -> float:
    if not sources:
        return 0.5
    scores = [SOURCE_RELIABILITY.get(s, 0.6) for s in sources]
    return sum(scores) / len(scores)


def estimate_cross_source_agreement(contradiction_count: int, total_evidence: int) -> float:
    """
    Simple heuristic: more contradictions relative to evidence volume
    -> lower agreement. Replace with a more principled measure later
    if time allows.
    """
    if total_evidence == 0:
        return 1.0
    penalty = min(contradiction_count / max(total_evidence, 1), 1.0)
    return round(1.0 - penalty, 3)
