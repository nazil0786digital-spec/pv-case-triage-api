from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class SeriousnessCriterion(StrEnum):
    DEATH = "death"
    LIFE_THREATENING = "life_threatening"
    HOSPITALIZATION = "hospitalization"
    DISABILITY = "disability"
    CONGENITAL_ANOMALY = "congenital_anomaly"
    MEDICALLY_SIGNIFICANT = "medically_significant"


class MinimumCriteria(BaseModel):
    identifiable_patient: bool
    identifiable_reporter: bool
    suspect_product: bool
    adverse_event: bool


class CaseInput(BaseModel):
    case_id: str = Field(min_length=1, max_length=80)
    event_description: str = Field(min_length=1, max_length=2000)
    receipt_date: date
    event_onset_date: date | None = None
    reporter_type: str = Field(default="unknown", max_length=50)
    medically_confirmed: bool = False
    seriousness: list[SeriousnessCriterion] = Field(default_factory=list)
    expectedness: str = Field(default="unknown", pattern="^(expected|unexpected|unknown)$")
    causality: str = Field(
        default="unknown",
        pattern="^(related|possibly_related|not_related|unknown)$",
    )
    follow_up: bool = False
    minimum_criteria: MinimumCriteria

    @model_validator(mode="after")
    def onset_cannot_follow_receipt(self) -> "CaseInput":
        if self.event_onset_date and self.event_onset_date > self.receipt_date:
            raise ValueError("event_onset_date cannot be after receipt_date")
        return self


class TriageResult(BaseModel):
    case_id: str
    valid_icsr: bool
    priority: str
    score: int = Field(ge=0, le=100)
    reason_codes: list[str]
    recommended_actions: list[str]
    missing_minimum_criteria: list[str]
    ruleset_version: str
    disclaimer: str
