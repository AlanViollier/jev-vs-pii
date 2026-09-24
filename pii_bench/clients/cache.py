"""Disk cache of every model response, keyed by the exact request. Hits are free and replayable."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class CachedResponse(BaseModel):
    """A stored response body and how long the real call took."""

    body: dict[str, Any]
    latency_s: float


class ResponseCache:
    """Request-keyed response store. In replay mode a hit waits its recorded latency."""

    def __init__(self, directory: Path, replay: bool = False) -> None:
        raise NotImplementedError

    async def get_or_call(
        self,
        request: Mapping[str, Any],
        call: Callable[[], Awaitable[CachedResponse]],
    ) -> tuple[CachedResponse, bool]:
        """Return the cached response for `request`, or make the call and store it.

        Parameters
        ----------
        request:
            Everything that determines the response (endpoint, model, payload).
        call:
            Makes the real call; only awaited on a miss.

        Returns
        -------
        tuple[CachedResponse, bool]
            The response, and whether it came from the cache.
        """
        raise NotImplementedError
