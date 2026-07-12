from datetime import UTC, datetime

from app.models import SearchResponse, SourceEvidence
from app.registry import MANUAL_OFFICIAL_SOURCES


class ManualOfficialConnector:
    async def process(self, numero_cnj: str, tribunal: str) -> SearchResponse:
        source_key = f"{tribunal}_process"
        source = MANUAL_OFFICIAL_SOURCES.get(source_key)
        if not source:
            return SearchResponse(
                status="manual_required",
                query={"numero_cnj": numero_cnj, "tribunal": tribunal},
                limitations=[
                    "Consulte o portal processual oficial do tribunal.",
                    "O robô não contorna CAPTCHA, autenticação ou proteção anti-automação.",
                ],
            )

        return SearchResponse(
            status="manual_required",
            query={"numero_cnj": numero_cnj, "tribunal": tribunal},
            evidence=SourceEvidence(
                source_id=source_key,
                source_name=source["name"],
                source_url=source["url"],
                retrieved_at=datetime.now(UTC),
                automated=False,
                official=True,
            ),
            limitations=[
                source["reason"],
                "A consulta deve ser conferida no portal oficial.",
            ],
        )

    async def jurisprudence(self, query: str, tribunal: str) -> SearchResponse:
        source_key = f"{tribunal}_jurisprudence"
        source = MANUAL_OFFICIAL_SOURCES.get(source_key)
        if not source:
            return SearchResponse(
                status="manual_required",
                query={"query": query, "tribunal": tribunal},
                limitations=[
                    "A versão atual não dispõe de fonte oficial integral automatizável "
                    "para este tribunal.",
                    "Consulte o portal oficial e confira o inteiro teor.",
                ],
            )

        return SearchResponse(
            status="manual_required",
            query={"query": query, "tribunal": tribunal},
            evidence=SourceEvidence(
                source_id=source_key,
                source_name=source["name"],
                source_url=source["url"],
                retrieved_at=datetime.now(UTC),
                automated=False,
                official=True,
            ),
            limitations=[
                source["reason"],
                "Resultados devem ser conferidos antes do uso profissional.",
            ],
        )
