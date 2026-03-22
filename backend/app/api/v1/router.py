from fastapi import APIRouter

from backend.app.api.v1.routes.document_routes import router as document_router
from backend.app.api.v1.routes.health_routes import router as health_router
from backend.app.api.v1.routes.session_routes import router as session_router

router = APIRouter()

router.include_router(document_router, prefix="/documents", tags=["Documents"])
router.include_router(health_router, prefix="/health", tags=["Health"])
router.include_router(session_router, prefix="/session", tags=["Session"])
