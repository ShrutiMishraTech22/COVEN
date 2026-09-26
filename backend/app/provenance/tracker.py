"""
COVEN evidence provenance tracking.

This module records transformations performed on evidence.

It deliberately does not depend on SQLAlchemy or the Evidence model,
so it can be integrated with Half 1A after the model split.
"""

from datetime import datetime, timezone
from typing import Any


def _timestamp() -> str:
    """Return the current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def record_transformation(
    evidence: Any,
    action: str,
    timestamp: str | None = None,
) -> Any:
    """
    Append a transformation entry to Evidence.transformation_history.

    Parameters
    ----------
    evidence:
        An Evidence model/object containing a
        `transformation_history` attribute.

    action:
        Description of the transformation, e.g.
        "hashed", "parsed", or "normalized".

    timestamp:
        Optional timestamp. If omitted, the current UTC time is used.

    Returns
    -------
    evidence
        The same evidence object, after updating its history.
    """

    if not action or not action.strip():
        raise ValueError("Transformation action cannot be empty.")

    if not hasattr(evidence, "transformation_history"):
        raise AttributeError(
            "Evidence object does not have "
            "'transformation_history'."
        )

    history = evidence.transformation_history

    if history is None:
        history = []

    if not isinstance(history, list):
        raise TypeError(
            "transformation_history must be a list."
        )

    history.append(
        {
            "action": action.strip(),
            "timestamp": timestamp or _timestamp(),
        }
    )

    evidence.transformation_history = history

    return evidence