# app/middleware_rate_limit.py
from __future__ import annotations
import time
from collections import deque, defaultdict
from typing import Deque, Dict, Tuple
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse


class RateLimitMiddleware:
    """
    Per-IP token bucket semplice: max `burst` richieste in `window_sec`.
    Ideale per proteggere endpoint di upload da flood/abuso.
    """

    def __init__(self, app: ASGIApp, burst: int = 5, window_sec: int = 60):
        self.app = app
        self.burst = burst
        self.window_sec = window_sec
        self._hits: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        now = time.time()
        path = scope.get("path", "")
        client = (scope.get("client") or ("-", 0))[0]  # IP
        key = (client, path)

        dq = self._hits[key]
        # drop vecchi
        while dq and now - dq[0] > self.window_sec:
            dq.popleft()

        if len(dq) >= self.burst:
            resp = JSONResponse(
                {"detail": "Too Many Requests"},
                status_code=429,
                headers={"Retry-After": str(self.window_sec)},
            )
            await resp(scope, receive, send)
            return

        dq.append(now)
        await self.app(scope, receive, send)
