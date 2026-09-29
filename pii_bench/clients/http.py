"""The one paid POST both OpenRouter clients make: budget hold, retries on blips, real cost charged."""

from __future__ import annotations

import time
from collections.abc import Callable
from decimal import Decimal
from typing import Any

import httpx
from tenacity import AsyncRetrying, retry_if_exception, stop_after_attempt, wait_exponential

from pii_bench.clients.budget import Ledger
from pii_bench.clients.cache import CachedResponse
from pii_bench.exceptions import ProviderError

_TRANSIENT_STATUS = {408, 429, 500, 502, 503, 504}


async def paid_post(
    http: httpx.AsyncClient,
    url: str,
    payload: dict[str, Any],
    ledger: Ledger,
    estimate_usd: Decimal,
    cost_of: Callable[[dict[str, Any]], Decimal],
) -> CachedResponse:
    """POST `payload` under a budget hold and charge what the provider says it cost.

    Parameters
    ----------
    http:
        Client carrying the auth header.
    url:
        Endpoint.
    payload:
        JSON body.
    ledger:
        Project spend ledger.
    estimate_usd:
        Upper bound on the call's cost, held while it is in flight.
    cost_of:
        Reads the real cost from a response body; raises `ProviderError` if it can't.

    Returns
    -------
    CachedResponse
        Body and latency, ready to store. Raises `BudgetExceeded` before sending if the
        hold would pass the cap, `ProviderError` on a non-transient HTTP error or after
        the retries run out.
    """
    with ledger.reserve(estimate_usd) as charge:
        try:
            async for attempt in AsyncRetrying(
                ## Shared provider pools rate-limit for tens of seconds; wait them out.
                stop=stop_after_attempt(6),
                wait=wait_exponential(multiplier=2, max=60),
                retry=retry_if_exception(_is_transient),
                reraise=True,
            ):
                with attempt:
                    ## Latency is the answering attempt alone, not time spent waiting out retries.
                    started = time.perf_counter()
                    response = await http.post(url, json=payload)
                    latency = time.perf_counter() - started
                    response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise ProviderError(
                f"{url} {error.response.status_code}: {error.response.text[:500]}"
            ) from error
        except httpx.TransportError as error:
            raise ProviderError(f"{url} unreachable: {error!r}") from error
        body = response.json()
        charge(cost_of(body))
    return CachedResponse(body=body, latency_s=latency)


def _is_transient(error: BaseException) -> bool:
    if isinstance(error, httpx.HTTPStatusError):
        return error.response.status_code in _TRANSIENT_STATUS
    return isinstance(error, httpx.TransportError)
