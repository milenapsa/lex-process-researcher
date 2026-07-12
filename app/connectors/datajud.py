from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any

import asyncio
import httpx

from app.config import settings
from app.key_provider import key_provider
from app.models import SearchResponse, SourceEvidence
from app.outbound_limit import SlidingWindowLimiter
from app.registry import DATAJUD_ALIASES


class DataJudConnector:
    source_id = "cnj_datajud"
    source_name = "CNJ DataJud API Pública"

    def __init__(self) -> None:
        self._limiter = SlidingWindowLimiter(
            max_requests=min(settings.datajud_max_requests_per_minute, 110),
            window_seconds=60.0,
        )
        self._concurrency = asyncio.Semaphore(
            max(1, settings.datajud_max_concurrency)
        )

    def build_endpoint(self, tribunal: str) -> str:
        alias = DATAJUD_ALIASES[tribunal]
        return f"{settings.datajud_base_url.rstrip('/')}/{alias}/_search"

    async def health(self) -> dict[str, Any]:
        key, state = await key_provider.get_key()
        return {
            "source_id": self.source_id,
            "configured": bool(key),
            "key_source": state.source,
            "secret_returned": False,
            "tribunals_mapped": len(DATAJUD_ALIASES),
            "local_rpm_limit": min(
                settings.datajud_max_requests_per_minute, 110
            ),
            "max_concurrency": max(1, settings.datajud_max_concurrency),
        }

    @staticmethod
    def _retry_after_seconds(response: httpx.Response) -> int | None:
        value = response.headers.get("retry-after")
        if not value:
            return None
        try:
            return max(0, int(value))
        except ValueError:
            try:
                when = parsedate_to_datetime(value)
                return max(0, int((when - datetime.now(UTC)).total_seconds()))
            except (TypeError, ValueError):
                return None

    async def search_process(
        self,
        numero_cnj_digits: str,
        tribunal: str,
        retried_after_key_refresh: bool = False,
    ) -> SearchResponse:
        tribunal = tribunal.lower()
        if tribunal not in DATAJUD_ALIASES:
            return SearchResponse(
                status="invalid_input",
                query={"numero_cnj": numero_cnj_digits, "tribunal": tribunal},
                limitations=["Tribunal não reconhecido no registro oficial desta versão."],
            )

        key, state = await key_provider.get_key()
        if not key:
            return SearchResponse(
                status="not_configured",
                query={"numero_cnj": numero_cnj_digits, "tribunal": tribunal},
                limitations=[
                    "Não foi possível adquirir a chave pública vigente do DataJud "
                    f"(estado: {state.source})."
                ],
            )

        url = self.build_endpoint(tribunal)
        headers = {
            "Authorization": f"APIKey {key}",
            "Content-Type": "application/json",
            "User-Agent": "HomoSapiens-Lex-ProcessResearcher/0.3.0",
        }
        payload = {
            "size": 25,
            "query": {"match": {"numeroProcesso": numero_cnj_digits}},
        }

        evidence = SourceEvidence(
            source_id=self.source_id,
            source_name=self.source_name,
            source_url=url,
            retrieved_at=datetime.now(UTC),
            automated=True,
            official=True,
        )

        await self._limiter.acquire()
        try:
            async with self._concurrency:
                async with httpx.AsyncClient(
                    timeout=settings.http_timeout_seconds,
                    follow_redirects=False,
                ) as client:
                    response = await client.post(url, headers=headers, json=payload)
        except httpx.HTTPError:
            return SearchResponse(
                status="source_unavailable",
                query={"numero_cnj": numero_cnj_digits, "tribunal": tribunal},
                evidence=evidence,
                limitations=["Falha de transporte ao consultar a fonte oficial."],
            )

        if response.status_code in {401, 403} and not retried_after_key_refresh:
            key_provider.invalidate()
            refreshed, _ = await key_provider.get_key(force_refresh=True)
            if refreshed:
                return await self.search_process(
                    numero_cnj_digits,
                    tribunal,
                    retried_after_key_refresh=True,
                )

        if response.status_code in {401, 403}:
            return SearchResponse(
                status="not_configured",
                query={"numero_cnj": numero_cnj_digits, "tribunal": tribunal},
                evidence=evidence,
                limitations=[
                    "A fonte rejeitou a chave pública mesmo após atualização automática."
                ],
            )

        if response.status_code == 429:
            retry_after = self._retry_after_seconds(response)
            detail = "Limite de requisições da fonte oficial atingido."
            if retry_after is not None:
                detail += f" Nova tentativa recomendada após {retry_after} segundos."
            return SearchResponse(
                status="rate_limited",
                query={"numero_cnj": numero_cnj_digits, "tribunal": tribunal},
                evidence=evidence,
                limitations=[detail],
            )

        if response.status_code >= 500:
            return SearchResponse(
                status="source_unavailable",
                query={"numero_cnj": numero_cnj_digits, "tribunal": tribunal},
                evidence=evidence,
                limitations=[f"Fonte oficial retornou HTTP {response.status_code}."],
            )

        if response.status_code >= 400:
            return SearchResponse(
                status="source_unavailable",
                query={"numero_cnj": numero_cnj_digits, "tribunal": tribunal},
                evidence=evidence,
                limitations=[
                    f"Consulta recusada pela fonte oficial: HTTP {response.status_code}."
                ],
            )

        try:
            data = response.json()
        except ValueError:
            return SearchResponse(
                status="source_unavailable",
                query={"numero_cnj": numero_cnj_digits, "tribunal": tribunal},
                evidence=evidence,
                limitations=["A fonte oficial retornou resposta não JSON."],
            )

        hits = data.get("hits", {}).get("hits", [])
        records = []
        for hit in hits:
            source = hit.get("_source") or {}
            if source.get("nivelSigilo", 0) not in {0, "0", None}:
                continue
            records.append(
                {
                    "id_fonte": hit.get("_id"),
                    "numeroProcesso": source.get("numeroProcesso"),
                    "tribunal": source.get("tribunal"),
                    "grau": source.get("grau"),
                    "classe": source.get("classe"),
                    "assuntos": source.get("assuntos", []),
                    "orgaoJulgador": source.get("orgaoJulgador"),
                    "dataAjuizamento": source.get("dataAjuizamento"),
                    "dataHoraUltimaAtualizacao": source.get(
                        "dataHoraUltimaAtualizacao"
                    ),
                    "movimentos": source.get("movimentos", []),
                }
            )

        return SearchResponse(
            status="found" if records else "not_found",
            query={"numero_cnj": numero_cnj_digits, "tribunal": tribunal},
            records=records,
            evidence=evidence,
            limitations=[
                "DataJud fornece metadados públicos; não substitui a consulta aos autos.",
                "Ausência de resultado não prova inexistência do processo.",
                "A fonte oficial não garante precisão, integridade ou atualidade dos dados.",
            ],
        )
