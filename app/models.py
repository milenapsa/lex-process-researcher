from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


SearchStatus = Literal[
    "found",
    "not_found",
    "manual_required",
    "source_unavailable",
    "not_configured",
    "invalid_input",
    "rate_limited",
]


class ProcessSearchRequest(BaseModel):
    numero_cnj: str = Field(min_length=1, max_length=40)
    tribunal: str | None = Field(default=None, max_length=30)


class JurisprudenceSearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    tribunal: str | None = Field(default=None, max_length=30)
    limit: int = Field(default=10, ge=1, le=50)


class SourceEvidence(BaseModel):
    source_id: str
    source_name: str
    source_url: str
    retrieved_at: datetime
    automated: bool
    official: bool = True


class SearchResponse(BaseModel):
    status: SearchStatus
    query: dict[str, Any]
    records: list[dict[str, Any]] = Field(default_factory=list)
    evidence: SourceEvidence | None = None
    limitations: list[str] = Field(default_factory=list)
    human_review_required: bool = True


class TimelineEvent(BaseModel):
    date: datetime | None = None
    code: int | str | None = None
    name: str | None = None
    complements: list[dict[str, Any]] = Field(default_factory=list)
    source_order: int | None = None


class TimelineResponse(BaseModel):
    status: SearchStatus
    numero_cnj: str
    tribunal: str
    events: list[TimelineEvent] = Field(default_factory=list)
    evidence: SourceEvidence | None = None
    limitations: list[str] = Field(default_factory=list)
    human_review_required: bool = True
