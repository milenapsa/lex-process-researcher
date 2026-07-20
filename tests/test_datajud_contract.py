from fastapi.testclient import TestClient

import app.main as main_module
from app.models import SearchResponse, TimelineResponse


client = TestClient(main_module.app)


def test_datajud_health_contract(monkeypatch):
    async def fake_health():
        return {
            "configured": True,
            "key_source": "environment",
            "tribunals_mapped": 27,
            "local_rpm_limit": 110,
            "max_concurrency": 4,
        }

    monkeypatch.setattr(main_module.datajud, "health", fake_health)

    response = client.get("/v1/datajud/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["source"] == "cnj_datajud"
    assert payload["configured"] is True
    assert payload["secret_returned"] is False
    assert payload["human_review_required"] is True
    assert payload["no_invention_policy"] is True


def test_datajud_process_alias_limits_records(monkeypatch):
    async def fake_search_process(numero_cnj: str, tribunal: str | None):
        return SearchResponse(
            status="found",
            query={"numero_cnj": numero_cnj, "tribunal": tribunal},
            records=[{"id": 1}, {"id": 2}, {"id": 3}],
            limitations=[],
            human_review_required=True,
        )

    monkeypatch.setattr(main_module, "search_process", fake_search_process)

    response = client.get(
        "/v1/datajud/processos/0000000-00.0000.0.00.0000",
        params={"tribunal": "tjsc", "size": 2},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "found"
    assert payload["query"]["tribunal"] == "tjsc"
    assert payload["records"] == [{"id": 1}, {"id": 2}]
    assert payload["human_review_required"] is True


def test_datajud_process_alias_rejects_invalid_size():
    too_small = client.get(
        "/v1/datajud/processos/0000000-00.0000.0.00.0000",
        params={"size": 0},
    )
    too_large = client.get(
        "/v1/datajud/processos/0000000-00.0000.0.00.0000",
        params={"size": 26},
    )

    assert too_small.status_code == 422
    assert too_large.status_code == 422


def test_datajud_timeline_alias(monkeypatch):
    async def fake_timeline(numero_cnj: str, tribunal: str | None):
        return TimelineResponse(
            status="found",
            numero_cnj=numero_cnj,
            tribunal=tribunal or "tjsc",
            events=[],
            limitations=["metadados públicos"],
            human_review_required=True,
        )

    monkeypatch.setattr(main_module, "timeline", fake_timeline)

    response = client.get(
        "/v1/datajud/processos/0000000-00.0000.0.00.0000/timeline",
        params={"tribunal": "tjsc"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "found"
    assert payload["tribunal"] == "tjsc"
    assert payload["events"] == []
    assert payload["human_review_required"] is True
