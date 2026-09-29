"""A cached request never calls twice; any change to the request is a different entry."""

from __future__ import annotations

import asyncio
from pathlib import Path

from jev_vs_pii.clients.cache import CachedResponse, ResponseCache


class _Counter:
    def __init__(self) -> None:
        self.calls = 0

    async def __call__(self) -> CachedResponse:
        self.calls += 1
        return CachedResponse(body={"answer": self.calls}, latency_s=0.01)


def test_second_identical_request_is_a_free_hit(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path)
    call = _Counter()
    first, first_hit = asyncio.run(cache.get_or_call({"model": "m", "state": "x"}, call))
    again, again_hit = asyncio.run(cache.get_or_call({"state": "x", "model": "m"}, call))
    assert (first_hit, again_hit) == (False, True)
    assert again == first
    assert call.calls == 1


def test_different_request_misses(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path)
    call = _Counter()
    asyncio.run(cache.get_or_call({"state": "x"}, call))
    asyncio.run(cache.get_or_call({"state": "y"}, call))
    assert call.calls == 2


def test_hits_survive_a_new_cache_object(tmp_path: Path) -> None:
    call = _Counter()
    asyncio.run(ResponseCache(tmp_path).get_or_call({"state": "x"}, call))
    response, hit = asyncio.run(ResponseCache(tmp_path).get_or_call({"state": "x"}, call))
    assert hit
    assert response.latency_s == 0.01
    assert call.calls == 1
