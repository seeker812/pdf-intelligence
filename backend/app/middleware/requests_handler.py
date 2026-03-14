from collections.abc import Iterable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class ApiRequestHandler(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        public_paths: Iterable[str] | None = None,
        public_prefixes: Iterable[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.public_paths = {p.rstrip("/") or "/" for p in (public_paths or [])}
        self.public_prefixes = {p.rstrip("/") or "/" for p in (public_prefixes or [])}

    async def dispatch(self, request: Request, call_next):
        # You can replace this with JWT/session validation logic.
        normalized_path = request.url.path.rstrip("/") or "/"
        is_public_path = normalized_path in self.public_paths
        is_public_prefix = any(
            normalized_path == prefix or normalized_path.startswith(f"{prefix}/")
            for prefix in self.public_prefixes
        )

        if not is_public_path and not is_public_prefix:
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": {"code": "UNAUTHORIZED", "message": "Missing Authorization header"}},
                )

        return await call_next(request)
