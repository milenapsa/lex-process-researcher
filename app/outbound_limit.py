from __future__ import annotations

import asyncio
import time
from collections import deque


class SlidingWindowLimiter:
    """Limite local por processo para proteger a API oficial.

    Não substitui um rate limiter distribuído no gateway, mas impede que uma
    instância exceda o teto configurado.
    """

    def __init__(self, max_requests: int, window_seconds: float = 60.0) -> None:
        self.max_requests = max(1, max_requests)
        self.window_seconds = max(1.0, window_seconds)
        self._events: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        while True:
            async with self._lock:
                now = time.monotonic()
                cutoff = now - self.window_seconds
                while self._events and self._events[0] <= cutoff:
                    self._events.popleft()

                if len(self._events) < self.max_requests:
                    self._events.append(now)
                    return

                wait_for = self.window_seconds - (now - self._events[0])

            await asyncio.sleep(max(wait_for, 0.05))
