# app/middleware_security.py
from __future__ import annotations
from uuid import uuid4
from starlette.types import ASGIApp, Receive, Scope, Send


class CorrelationIdMiddleware:
    """
    Aggiunge X-Request-ID se assente; lo ripropaga in risposta.
    Utile per audit trail/log correlation.
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID"):
        self.app = app
        self.header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        req_headers = dict(scope.get("headers", []))
        key = self.header_name.lower().encode()
        req_id = req_headers.get(key, None)
        if not req_id:
            req_id = str(uuid4()).encode()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.append((b"x-request-id", req_id))
            await send(message)

        await self.app(scope, receive, send_wrapper)


class SecurityHeadersMiddleware:
    """
    Imposta header di sicurezza comuni.
    Nota: HSTS ha senso solo dietro HTTPS in produzione.
    """

    def __init__(self, app: ASGIApp, enable_hsts: bool = False):
        self.app = app
        self.enable_hsts = enable_hsts

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])

                def add(k, v):
                    headers.append((k.encode(), v.encode()))

                # Clickjacking
                add("X-Frame-Options", "DENY")
                # MIME sniffing
                add("X-Content-Type-Options", "nosniff")
                # XSS protection (legacy-UA)
                add("X-XSS-Protection", "1; mode=block")
                # Referrer policy
                add("Referrer-Policy", "strict-origin-when-cross-origin")
                # COOP/COEP/CORP di base
                add("Cross-Origin-Opener-Policy", "same-origin")
                add("Cross-Origin-Embedder-Policy", "require-corp")
                add("Cross-Origin-Resource-Policy", "same-site")
                # Permissions Policy minimale
                add("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
                # HSTS solo in prod/https
                if self.enable_hsts:
                    add(
                        "Strict-Transport-Security",
                        "max-age=31536000; includeSubDomains",
                    )
            await send(message)

        await self.app(scope, receive, send_wrapper)
