"""Disk cache of every model response, keyed by the exact request. Hits are free and replayable."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Awaitable, Callable, Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class CachedResponse(BaseModel):
    """A stored response body and how long the real call took."""

    body: dict[str, Any]
    latency_s: float


class ResponseCache:
    """Request-keyed response store, one readable JSON file per request.

    In replay mode a hit waits its recorded latency, so a replayed run looks like the real one.
    """

    def __init__(self, directory: Path, replay: bool = False) -> None:
        self._directory = directory
        self._replay = replay

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
        path = self._path_for(request)
        if path.exists():
            cached = CachedResponse.model_validate_json(path.read_text())
            if self._replay:
                await asyncio.sleep(cached.latency_s)
            return cached, True
        response = await call()
        path.parent.mkdir(parents=True, exist_ok=True)
        partial = path.with_name(f"{path.name}.part")
        partial.write_text(
            json.dumps({"request": request, **response.model_dump()}, ensure_ascii=False)
        )
        partial.replace(path)
        return response, False

    def _path_for(self, request: Mapping[str, Any]) -> Path:
        """Two-level fan-out on the request hash keeps directories small."""
        canonical = json.dumps(request, sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        return self._directory / digest[:2] / f"{digest}.json"
