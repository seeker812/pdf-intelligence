import logging
import uuid
from collections.abc import Iterable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

ANON_ID_HEADER = "X-Anon-ID"


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

    def _is_public(self, path: str) -> bool:
        normalized = path.rstrip("/") or "/"
        if normalized in self.public_paths:
            return True
        return any(
            normalized == prefix or normalized.startswith(f"{prefix}/")
            for prefix in self.public_prefixes
        )

    def _get_or_create_anon_id(self, request: Request) -> tuple[str, bool]:

        anon_id = request.headers.get(ANON_ID_HEADER)
        if anon_id:
            return anon_id, False
        return str(uuid.uuid4()), True

    async def dispatch(self, request: Request, call_next):
        if self._is_public(request.url.path):
            return await call_next(request)

        anon_id, was_generated = self._get_or_create_anon_id(request)

        if was_generated:
            logger.info(
                "No %s header found | generated new anon_id=%s | path=%s",
                ANON_ID_HEADER,
                anon_id,
                request.url.path,
            )

        request.state.annon_id = anon_id

        response = await call_next(request)

        response.headers[ANON_ID_HEADER] = anon_id

        return response
