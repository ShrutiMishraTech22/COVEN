import pytest

from backend.app.processors.log_processor import parse_log_file


def test_parse_single_event():
    data = b"""
    [
        {
            "user": "alice",
            "device": "laptop-01",
            "event_type": "login",
            "target": "system",
            "location": "Delhi",
            "time": "2026-09-20T10:30:00Z"
        }
    ]
    """

    result = parse_log_file(
        data,
        evidence_id="EV-001",
        source="laptop",
    )

    assert len(result) == 1

    event = result[0]

    assert event["actor"] == "alice"
    assert event["device"] == "laptop-01"
    assert event["action"] == "login"
    assert event["object"] == "system"
    assert event["location"] == "Delhi"
    assert event["timestamp"] == "2026-09-20T10:30:00+00:00"
    assert event["source"] == "laptop"
    assert event["evidence_id"] == "EV-001"


def test_parse_multiple_events():
    data = b"""
    [
        {
            "user": "alice",
            "event_type": "login",
            "time": "2026-09-20T10:30:00Z"
        },
        {
            "user": "bob",
            "event_type": "logout",
            "time": "2026-09-20T11:30:00Z"
        }
    ]
    """

    result = parse_log_file(
        data,
        evidence_id="EV-002",
        source="network",
    )

    assert len(result) == 2
    assert result[0]["actor"] == "alice"
    assert result[0]["action"] == "login"
    assert result[1]["actor"] == "bob"
    assert result[1]["action"] == "logout"


def test_parse_events_wrapper():
    data = b"""
    {
        "events": [
            {
                "actor": "alice",
                "action": "login",
                "timestamp": "2026-09-20T10:30:00Z"
            },
            {
                "actor": "bob",
                "action": "logout",
                "timestamp": "2026-09-20T11:30:00Z"
            }
        ]
    }
    """

    result = parse_log_file(
        data,
        evidence_id="EV-003",
        source="laptop",
    )

    assert len(result) == 2
    assert result[0]["actor"] == "alice"
    assert result[1]["actor"] == "bob"


def test_missing_optional_fields_become_none():
    data = b"""
    [
        {
            "user": "alice",
            "event_type": "login"
        }
    ]
    """

    result = parse_log_file(
        data,
        evidence_id="EV-004",
        source="network",
    )

    event = result[0]

    assert event["actor"] == "alice"
    assert event["action"] == "login"
    assert event["device"] is None
    assert event["object"] is None
    assert event["location"] is None
    assert event["timestamp"] is None


def test_invalid_json_raises_value_error():
    with pytest.raises(ValueError, match="Invalid JSON log file"):
        parse_log_file(
            b"{invalid json}",
            evidence_id="EV-005",
            source="network",
        )


def test_empty_file_raises_value_error():
    with pytest.raises(ValueError, match="empty"):
        parse_log_file(
            b"",
            evidence_id="EV-006",
            source="network",
        )


def test_non_bytes_input_raises_type_error():
    with pytest.raises(TypeError, match="bytes"):
        parse_log_file(
            "not bytes",
            evidence_id="EV-007",
            source="network",
        )