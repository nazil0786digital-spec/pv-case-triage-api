from datetime import date

import pytest
from pydantic import ValidationError

from app.engine import triage_case
from app.models import CaseInput, MinimumCriteria, SeriousnessCriterion


def make_case(**overrides) -> CaseInput:
    payload = {
        "case_id": "CASE-001",
        "event_description": "Synthetic event for testing",
        "receipt_date": date(2026, 9, 16),
        "minimum_criteria": MinimumCriteria(
            identifiable_patient=True,
            identifiable_reporter=True,
            suspect_product=True,
            adverse_event=True,
        ),
    }
    payload.update(overrides)
    return CaseInput(**payload)


def test_fatal_unexpected_related_case_is_critical() -> None:
    result = triage_case(
        make_case(
            seriousness=[SeriousnessCriterion.DEATH],
            expectedness="unexpected",
            causality="related",
            medically_confirmed=True,
        )
    )
    assert result.priority == "critical"
    assert result.score == 100
    assert "DEATH_REPORTED" in result.reason_codes


def test_missing_minimum_criterion_is_incomplete() -> None:
    result = triage_case(
        make_case(
            minimum_criteria=MinimumCriteria(
                identifiable_patient=True,
                identifiable_reporter=False,
                suspect_product=True,
                adverse_event=True,
            )
        )
    )
    assert result.valid_icsr is False
    assert result.priority == "incomplete"
    assert result.missing_minimum_criteria == ["identifiable_reporter"]


def test_valid_non_serious_case_is_low_priority() -> None:
    result = triage_case(make_case())
    assert result.valid_icsr is True
    assert result.priority == "low"
    assert result.score == 10


def test_future_onset_date_is_rejected() -> None:
    with pytest.raises(ValidationError):
        make_case(event_onset_date=date(2026, 9, 17))

