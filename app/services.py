from datetime import datetime
from typing import Any

from app.cnj import (
    CNJValidationError,
    cnj_digits,
    infer_state_tribunal,
    normalize_cnj,
    validate_cnj_check_digits,
)
from app.connectors.datajud import DataJudConnector
from app.connectors.manual import ManualOfficialConnector
from app.models import SearchResponse, TimelineEvent, TimelineResponse


datajud = DataJudConnector()
manual = ManualOfficialConnector()


def _parse_date(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    cleaned = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


async def search_process(numero_cnj: str, tribunal: str | None) -> SearchResponse:
    try:
        normalized = normalize_cnj(numero_cnj)
    except CNJValidationError as exc:
        return SearchResponse(
            status="invalid_input",
            query={"numero_cnj": numero_cnj, "tribunal": tribunal},
            limitations=[str(exc)],
        )

    if not validate_cnj_check_digits(normalized):
        return SearchResponse(
            status="invalid_input",
            query={"numero_cnj": normalized, "tribunal": tribunal},
            limitations=["Dígitos verificadores do número CNJ não conferem."],
        )

    resolved_tribunal = (tribunal or infer_state_tribunal(normalized) or "").lower()
    if not resolved_tribunal:
        return SearchResponse(
            status="invalid_input",
            query={"numero_cnj": normalized, "tribunal": tribunal},
            limitations=[
                "Informe o tribunal explicitamente para ramos não estaduais."
            ],
        )

    result = await datajud.search_process(cnj_digits(normalized), resolved_tribunal)
    result.query["numero_cnj_formatado"] = normalized

    if result.status in {"source_unavailable", "not_configured", "rate_limited"}:
        fallback = await manual.process(normalized, resolved_tribunal)
        fallback.limitations.insert(
            0,
            f"DataJud retornou estado '{result.status}'.",
        )
        return fallback

    return result


async def timeline(numero_cnj: str, tribunal: str | None) -> TimelineResponse:
    result = await search_process(numero_cnj, tribunal)
    resolved_tribunal = (
        tribunal
        or result.query.get("tribunal")
        or infer_state_tribunal(numero_cnj)
        or "desconhecido"
    )

    if result.status != "found":
        return TimelineResponse(
            status=result.status,
            numero_cnj=result.query.get("numero_cnj_formatado", numero_cnj),
            tribunal=resolved_tribunal,
            evidence=result.evidence,
            limitations=result.limitations,
        )

    events: list[TimelineEvent] = []
    for record in result.records:
        for index, movement in enumerate(record.get("movimentos", [])):
            events.append(
                TimelineEvent(
                    date=_parse_date(
                        movement.get("dataHora")
                        or movement.get("dataHoraMovimento")
                        or movement.get("data")
                    ),
                    code=movement.get("codigo"),
                    name=movement.get("nome"),
                    complements=movement.get("complementosTabelados", []),
                    source_order=index,
                )
            )

    events.sort(
        key=lambda event: (
            event.date is None,
            event.date or datetime.max,
            event.source_order or 0,
        )
    )

    return TimelineResponse(
        status="found",
        numero_cnj=result.query.get("numero_cnj_formatado", numero_cnj),
        tribunal=resolved_tribunal,
        events=events,
        evidence=result.evidence,
        limitations=[
            *result.limitations,
            "A linha do tempo reflete somente movimentos retornados pela fonte.",
        ],
    )
