import pytest

from backend.app.provenance.tracker import record_transformation


class FakeEvidence:
    def __init__(self, transformation_history=None):
        self.transformation_history = transformation_history


def test_record_first_transformation():
    evidence = FakeEvidence()

    result = record_transformation(
        evidence,
        "hashed",
        timestamp="2026-09-25T00:00:00+00:00",
    )

    assert result is evidence
    assert evidence.transformation_history == [
        {
            "action": "hashed",
            "timestamp": "2026-09-25T00:00:00+00:00",
        }
    ]


def test_record_multiple_transformations():
    evidence = FakeEvidence()

    record_transformation(
        evidence,
        "hashed",
        timestamp="2026-09-25T00:00:00+00:00",
    )

    record_transformation(
        evidence,
        "parsed",
        timestamp="2026-09-25T00:01:00+00:00",
    )

    record_transformation(
        evidence,
        "normalized",
        timestamp="2026-09-25T00:02:00+00:00",
    )

    assert len(evidence.transformation_history) == 3
    assert evidence.transformation_history[0]["action"] == "hashed"
    assert evidence.transformation_history[1]["action"] == "parsed"
    assert evidence.transformation_history[2]["action"] == "normalized"


def test_none_history_is_initialized():
    evidence = FakeEvidence(None)

    record_transformation(
        evidence,
        "parsed",
        timestamp="2026-09-25T00:00:00+00:00",
    )

    assert len(evidence.transformation_history) == 1
    assert evidence.transformation_history[0]["action"] == "parsed"


def test_empty_action_raises_value_error():
    evidence = FakeEvidence()

    with pytest.raises(ValueError, match="cannot be empty"):
        record_transformation(evidence, "")


def test_missing_history_attribute_raises_attribute_error():
    class InvalidEvidence:
        pass

    with pytest.raises(
        AttributeError,
        match="transformation_history",
    ):
        record_transformation(
            InvalidEvidence(),
            "parsed",
        )


def test_invalid_history_type_raises_type_error():
    evidence = FakeEvidence("not a list")

    with pytest.raises(
        TypeError,
        match="must be a list",
    ):
        record_transformation(
            evidence,
            "parsed",
        )