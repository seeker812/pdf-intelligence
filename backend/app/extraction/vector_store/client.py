import logging
from functools import lru_cache

from qdrant_client import QdrantClient

from backend.app.core.config import get_settings

settings = get_settings()

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:

    if settings.QDRANT_URL:
        logger.info("Connecting to remote Qdrant url=%s", settings.QDRANT_URL)
        return QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None,
            timeout=settings.QDRANT_TIMEOUT,
        )

    logger.info("Using local Qdrant storage path=%s", settings.QDRANT_PATH)
    return QdrantClient(path=settings.QDRANT_PATH)
