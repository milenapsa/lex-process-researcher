import asyncio
import time

import pytest

from app.outbound_limit import SlidingWindowLimiter


@pytest.mark.asyncio
async def test_limiter_allows_configured_burst():
    limiter = SlidingWindowLimiter(max_requests=2, window_seconds=0.05)
    await limiter.acquire()
    await limiter.acquire()


@pytest.mark.asyncio
async def test_limiter_waits_after_limit():
    limiter = SlidingWindowLimiter(max_requests=1, window_seconds=0.05)
    await limiter.acquire()
    start = time.monotonic()
    await limiter.acquire()
    assert time.monotonic() - start >= 0.04
