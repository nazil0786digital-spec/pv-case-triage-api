import json
import logging
import time
from uuid import UUID, uuid4

from fastapi import FastAPI, Request

from app.engine import RULESET_VERSION, triage_case
from app.models import CaseInput, TriageResult

logger = logging.getLogger("pv_case_triage.api")

app = FastAPI(
    title="PV Case Triage API",
    version=RULESET_VERSION,
    description=(
        "Explainable, rules-first triage for synthetic pharmacovigilance cases. "
        "For demonstration and portfolio use only."
    ),
)


def _request_id(request: Request) -> str:
    candidate = request.headers.get("X-Request-ID")
    if candidate:
        try:
            return str(UUID(candidate))
        except ValueError:
            pass
    return str(uuid4())


@app.middleware("http")
async def request_observability(request: Request, call_next):
    request_id = _request_id(request)
    started_at = time.perf_counter()

    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request_id

    logger.info(
        json.dumps(
            {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
        )
    )
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "ruleset_version": RULESET_VERSION}


@app.post("/v1/triage", response_model=TriageResult)
def triage(payload: CaseInput) -> TriageResult:
    return triage_case(payload)
