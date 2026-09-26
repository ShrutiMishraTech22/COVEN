"""
COVEN log evidence processor.

This module parses uploaded JSON log evidence and converts it into
normalized event dictionaries.

Database insertion is intentionally NOT handled here.

Integration contract:
    parse_log_file(
        file_bytes: bytes,
        evidence_id: str,
        source: str
    ) -> list[dict]
"""

import json
from datetime import datetime
from typing import Any


# Canonical Event fields expected by the COVEN pipeline.
EVENT_FIELDS = (
    "actor",
    "device",
    "action",
    "object",
    "location",
    "timestamp",
    "source",
    "evidence_id",
)


# Possible names that synthetic evidence may use for the same concept.
FIELD_ALIASES = {
    "actor": (
        "actor",
        "user",
        "username",
        "user_id",
        "account",
    ),
    "device": (
        "device",
        "device_id",
        "hostname",
        "host",
        "machine",
    ),
    "action": (
        "action",
        "event",
        "event_type",
        "activity",
        "operation",
    ),
    "object": (
        "object",
        "object_id",
        "target",
        "resource",
        "file",
    ),
    "location": (
        "location",
        "location_name",
        "place",
        "gps",
        "ip_location",
    ),
    "timestamp": (
        "timestamp",
        "time",
        "datetime",
        "date",
        "created_at",
    ),
}


def _first_value(record: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    """Return the first available value for a group of field aliases."""

    for field in aliases:
        if field in record:
            return record[field]

    return None


def _normalize_timestamp(value: Any) -> Any:
    """
    Normalize timestamps when possible.

    The original value is returned if it cannot be parsed. This keeps
    the processor from destroying source evidence simply because a
    timestamp uses an unexpected format.
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.isoformat()

    if not isinstance(value, str):
        return value

    value = value.strip()

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).isoformat()
    except ValueError:
        return value


def _extract_records(payload: Any) -> list[dict[str, Any]]:
    """
    Extract event records from common JSON structures.

    Supported forms:

        [
            {...},
            {...}
        ]

    or:

        {
            "events": [...]
        }

    or:

        {
            "logs": [...]
        }

    or:

        {
            "records": [...]
        }

    or a single event object.
    """

    if isinstance(payload, list):
        records = payload

    elif isinstance(payload, dict):
        for container_name in ("events", "logs", "records"):
            container = payload.get(container_name)

            if isinstance(container, list):
                records = container
                break
        else:
            records = [payload]

    else:
        raise ValueError(
            "JSON evidence must contain an object or an array of objects."
        )

    if not all(isinstance(record, dict) for record in records):
        raise ValueError(
            "Every log event must be represented by a JSON object."
        )

    return records


def _normalize_record(
    record: dict[str, Any],
    evidence_id: str,
    source: str,
) -> dict[str, Any]:
    """Convert one raw log record into the COVEN event format."""

    normalized = {
        "actor": _first_value(record, FIELD_ALIASES["actor"]),
        "device": _first_value(record, FIELD_ALIASES["device"]),
        "action": _first_value(record, FIELD_ALIASES["action"]),
        "object": _first_value(record, FIELD_ALIASES["object"]),
        "location": _first_value(record, FIELD_ALIASES["location"]),
        "timestamp": _normalize_timestamp(
            _first_value(record, FIELD_ALIASES["timestamp"])
        ),
        "source": source,
        "evidence_id": evidence_id,
    }

    return normalized


def parse_log_file(
    file_bytes: bytes,
    evidence_id: str,
    source: str,
) -> list[dict]:
    """
    Parse a JSON log file into normalized COVEN event dictionaries.

    Parameters
    ----------
    file_bytes:
        Raw bytes from the uploaded JSON evidence file.

    evidence_id:
        Identifier of the Evidence record associated with the file.

    source:
        Source label for the evidence, such as "laptop", "network",
        "usb", or another project-defined source.

    Returns
    -------
    list[dict]
        Normalized event dictionaries ready for the API/data layer.

    Raises
    ------
    ValueError
        If the uploaded file is not valid JSON or does not contain
        valid event records.
    """

    if not isinstance(file_bytes, bytes):
        raise TypeError("file_bytes must be bytes.")

    if not file_bytes:
        raise ValueError("The uploaded log file is empty.")

    try:
        payload = json.loads(file_bytes.decode("utf-8-sig"))
    except UnicodeDecodeError as exc:
        raise ValueError(
            "Log file must be UTF-8 encoded JSON."
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON log file: {exc.msg} "
            f"at line {exc.lineno}, column {exc.colno}."
        ) from exc

    records = _extract_records(payload)

    return [
        _normalize_record(
            record=record,
            evidence_id=evidence_id,
            source=source,
        )
        for record in records
    ]