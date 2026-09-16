from fastapi import FastAPI

from app.engine import RULESET_VERSION, triage_case
from app.models import CaseInput, TriageResult

app = FastAPI(
    title="PV Case Triage API",
    version=RULESET_VERSION,
    description=(
        "Explainable, rules-first triage for synthetic pharmacovigilance cases. "
        "For demonstration and portfolio use only."
    ),
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "ruleset_version": RULESET_VERSION}


@app.post("/v1/triage", response_model=TriageResult)
def triage(payload: CaseInput) -> TriageResult:
    return triage_case(payload)

