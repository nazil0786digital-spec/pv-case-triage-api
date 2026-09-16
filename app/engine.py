from app.models import CaseInput, SeriousnessCriterion, TriageResult

RULESET_VERSION = "1.0.0"
DISCLAIMER = (
    "Decision-support demonstration only. It does not replace medical review, "
    "regulatory assessment, or an organization's validated procedures."
)


def _missing_criteria(case: CaseInput) -> list[str]:
    return [
        name
        for name, present in case.minimum_criteria.model_dump().items()
        if not present
    ]


def triage_case(case: CaseInput) -> TriageResult:
    """Apply transparent, deterministic rules to a synthetic PV case."""
    missing = _missing_criteria(case)
    if missing:
        return TriageResult(
            case_id=case.case_id,
            valid_icsr=False,
            priority="incomplete",
            score=0,
            reason_codes=["MINIMUM_CRITERIA_INCOMPLETE"],
            recommended_actions=[
                "Request follow-up for: " + ", ".join(missing),
                "Do not treat the record as a valid ICSR until minimum criteria are met",
            ],
            missing_minimum_criteria=missing,
            ruleset_version=RULESET_VERSION,
            disclaimer=DISCLAIMER,
        )

    score = 10
    reasons = ["VALID_MINIMUM_CRITERIA"]
    actions = ["Queue for standard case intake"]
    serious = set(case.seriousness)

    if serious:
        score += 40
        reasons.append("SERIOUS_EVENT")
        actions.append("Route for expedited seriousness review")

    if SeriousnessCriterion.DEATH in serious:
        score += 25
        reasons.append("DEATH_REPORTED")
        actions.append("Escalate immediately for fatal-case assessment")
    elif SeriousnessCriterion.LIFE_THREATENING in serious:
        score += 20
        reasons.append("LIFE_THREATENING_EVENT")

    if case.expectedness == "unexpected":
        score += 15
        reasons.append("UNEXPECTED_EVENT")
        actions.append("Verify expectedness against the applicable reference safety information")

    if case.causality == "related":
        score += 10
        reasons.append("RELATED_CAUSALITY")
    elif case.causality == "possibly_related":
        score += 5
        reasons.append("POSSIBLE_CAUSALITY")

    if case.medically_confirmed:
        score += 5
        reasons.append("MEDICALLY_CONFIRMED")

    score = min(score, 100)
    if score >= 75:
        priority = "critical"
    elif score >= 50:
        priority = "high"
    elif score >= 25:
        priority = "medium"
    else:
        priority = "low"

    if case.follow_up:
        actions.append("Reconcile new information with the prior case version")

    return TriageResult(
        case_id=case.case_id,
        valid_icsr=True,
        priority=priority,
        score=score,
        reason_codes=reasons,
        recommended_actions=actions,
        missing_minimum_criteria=[],
        ruleset_version=RULESET_VERSION,
        disclaimer=DISCLAIMER,
    )

