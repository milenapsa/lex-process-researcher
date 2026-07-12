from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from app.config import settings


KEY_PATTERN = re.compile(
    r"Authorization\s*:\s*APIKey\s+([A-Za-z0-9_\-+/=]{20,})",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class KeyState:
    available: bool
    source: str
    expires_at: float | None = None


class DataJudKeyProvider:
    def __init__(self) -> None:
        self._cached_key: str | None = None
        self._expires_at: float = 0
        self._lock = asyncio.Lock()

    @staticmethod
    def extract_key(html: str) -> str | None:
        match = KEY_PATTERN.search(html)
        return match.group(1) if match else None

    @staticmethod
    def _validate_key_page_url(url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise ValueError("A página da chave deve usar HTTPS.")
        if parsed.hostname not in {"datajud-wiki.cnj.jus.br"}:
            raise ValueError("Domínio da página da chave não autorizado.")

    async def get_key(self, force_refresh: bool = False) -> tuple[str | None, KeyState]:
        configured = (settings.datajud_api_key or "").strip()
        if configured:
            return configured, KeyState(available=True, source="environment")

        if not settings.datajud_auto_discover_key:
            return None, KeyState(available=False, source="disabled")

        now = time.time()
        if not force_refresh and self._cached_key and now < self._expires_at:
            return self._cached_key, KeyState(
                available=True,
                source="official_wiki_cache",
                expires_at=self._expires_at,
            )

        async with self._lock:
            now = time.time()
            if not force_refresh and self._cached_key and now < self._expires_at:
                return self._cached_key, KeyState(
                    available=True,
                    source="official_wiki_cache",
                    expires_at=self._expires_at,
                )

            self._validate_key_page_url(settings.datajud_key_page_url)
            try:
                async with httpx.AsyncClient(
                    timeout=settings.http_timeout_seconds,
                    follow_redirects=True,
                ) as client:
                    response = await client.get(settings.datajud_key_page_url)
                    response.raise_for_status()
            except httpx.HTTPError:
                return None, KeyState(available=False, source="official_wiki_unavailable")

            key = self.extract_key(response.text)
            if not key:
                return None, KeyState(available=False, source="official_wiki_parse_failed")

            self._cached_key = key
            self._expires_at = time.time() + max(settings.datajud_key_cache_seconds, 300)
            return key, KeyState(
                available=True,
                source="official_wiki",
                expires_at=self._expires_at,
            )

    def invalidate(self) -> None:
        self._cached_key = None
        self._expires_at = 0


key_provider = DataJudKeyProvider()
