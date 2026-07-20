from fastapi import FastAPI, Query

from app.cnj import CNJValidationError, normalize_cnj, validate_cnj_check_digits
from app.connectors.datajud import DataJudConnector
from app.connectors.manual import ManualOfficialConnector
from app.models import (
    JurisprudenceSearchRequest,
    ProcessSearchRequest,
    SearchResponse,
    TimelineResponse,
)
from app.registry import (
    CURATED_AUTOMATED_SOURCES,
    DATAJUD_ALIASES,
    MANUAL_OFFICIAL_SOURCES,
    TJS,
)
from app.services import search_process, timeline


app = FastAPI(
    title="Lex Process Researcher",
    version="0.3.1",
    description=(
        "Pesquisa auxiliar de processos públicos com fontes oficiais, "
        "sem automação de sistemas restritos."
    ),
)

datajud = DataJudConnector()
manual = ManualOfficialConnector()


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "service": "lex-process-researcher",
        "version": "0.3.1",
        "secret_returned": False,
    }


@app.get("/ready")
async def ready() -> dict:
    connector = await datajud.health()
    return {
        "status": "ready" if connector["configured"] else "ready_with_limits",
        "datajud": connector,
        "manual_official_fallback": True,
        "human_review_required": True,
        "no_invention_policy": True,
    }


@app.get("/v1/datajud/health")
async def datajud_health() -> dict:
    connector = await datajud.health()
    return {
        "status": "ok" if connector["configured"] else "degraded",
        "service": "lex-process-researcher",
        "version": "0.3.1",
        "source": "cnj_datajud",
        "configured": connector["configured"],
        "key_source": connector["key_source"],
        "secret_returned": False,
        "tribunals_mapped": connector["tribunals_mapped"],
        "local_rpm_limit": connector["local_rpm_limit"],
        "max_concurrency": connector["max_concurrency"],
        "human_review_required": True,
        "no_invention_policy": True,
    }


@app.get("/v1/sources")
async def sources() -> dict:
    health_state = await datajud.health()
    return {
        "datajud": {
            "official": True,
            "automated": True,
            "tribunals": sorted(DATAJUD_ALIASES),
            "tribunals_count": len(DATAJUD_ALIASES),
            "key_available": health_state["configured"],
            "key_source": health_state["key_source"],
        },
        "curated_automated": CURATED_AUTOMATED_SOURCES,
        "manual_official": MANUAL_OFFICIAL_SOURCES,
        "restrictions": [
            "sem CAPTCHA bypass",
            "sem login",
            "sem certificado digital",
            "sem protocolo ou peticionamento",
        ],
    }


@app.get("/v1/status-matrix")
async def status_matrix() -> dict:
    health_state = await datajud.health()
    return {
        "portal_completo_tjsc_eproc": {
            "status": "manual_official",
            "reason": "portal integral protegido; fallback oficial preservado",
        },
        "metadados_tjsc_datajud": {
            "status": "active" if health_state["configured"] else "degraded",
            "key_source": health_state["key_source"],
        },
        "demais_26_tjs_datajud": {
            "status": "active" if health_state["configured"] else "degraded",
            "mapped": len(TJS) - 1,
        },
        "jurisprudencia_integral_tjs": {
            "status": "hybrid_expansion",
            "automated_curated_sources": len(CURATED_AUTOMATED_SOURCES),
            "manual_official_portals": len(MANUAL_OFFICIAL_SOURCES),
            "rule": "automatizar somente fonte oficial tecnicamente permitida",
        },
    }


@app.get("/v1/compliance")
async def compliance() -> dict:
    return {
        "source": "CNJ DataJud API Pública",
        "terms_review_date": "2026-07-11",
        "max_requests_per_minute_cnj": 120,
        "configured_local_limit": min(
            datajud._limiter.max_requests,
            110,
        ),
        "personal_data_collection": False,
        "sealed_cases": "excluded",
        "commercial_exploitation": "not_authorized_by_service",
        "human_review_required": True,
        "restrictions": [
            "sem contorno de autenticação ou segurança",
            "sem coleta de dados pessoais de terceiros",
            "sem protocolo ou peticionamento",
            "sem conclusão jurídica automática",
        ],
    }


@app.post("/v1/processes/search", response_model=SearchResponse)
async def process_search(payload: ProcessSearchRequest) -> SearchResponse:
    return await search_process(payload.numero_cnj, payload.tribunal)


@app.get("/v1/processes/{numero_cnj}", response_model=SearchResponse)
async def process_get(
    numero_cnj: str,
    tribunal: str | None = Query(default=None),
) -> SearchResponse:
    return await search_process(numero_cnj, tribunal)


@app.get(
    "/v1/processes/{numero_cnj}/timeline",
    response_model=TimelineResponse,
)
async def process_timeline(
    numero_cnj: str,
    tribunal: str | None = Query(default=None),
) -> TimelineResponse:
    return await timeline(numero_cnj, tribunal)


@app.get(
    "/v1/datajud/processos/{numero_cnj}",
    response_model=SearchResponse,
)
async def datajud_process_get(
    numero_cnj: str,
    tribunal: str | None = Query(default=None),
    size: int = Query(default=1, ge=1, le=25),
) -> SearchResponse:
    result = await search_process(numero_cnj, tribunal)
    if result.records:
        result.records = result.records[:size]
    return result


@app.get(
    "/v1/datajud/processos/{numero_cnj}/timeline",
    response_model=TimelineResponse,
)
async def datajud_process_timeline(
    numero_cnj: str,
    tribunal: str | None = Query(default=None),
) -> TimelineResponse:
    return await timeline(numero_cnj, tribunal)


@app.post("/v1/jurisprudence/search", response_model=SearchResponse)
async def jurisprudence_search(
    payload: JurisprudenceSearchRequest,
) -> SearchResponse:
    tribunal = (payload.tribunal or "").lower()
    return await manual.jurisprudence(payload.query, tribunal)


@app.get("/v1/validate-cnj/{numero_cnj}")
async def validate_cnj(numero_cnj: str) -> dict:
    try:
        normalized = normalize_cnj(numero_cnj)
    except CNJValidationError as exc:
        return {"valid": False, "error": str(exc)}
    return {
        "valid": validate_cnj_check_digits(normalized),
        "normalized": normalized,
    }
