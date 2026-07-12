from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.presentation.api.v1.routers import (
    allocation_router,
    asset_router,
    audit_router,
    auth_router,
    booking_router,
    employee_router,
    maintenance_router,
    organization_router,
)
from src.presentation.middleware.error_handler import register_exception_handlers

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],  # tighten for production via env-driven allowlist
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(organization_router.router, prefix="/api/v1")
app.include_router(employee_router.router, prefix="/api/v1")
app.include_router(asset_router.router, prefix="/api/v1")
app.include_router(allocation_router.router, prefix="/api/v1")
app.include_router(booking_router.router, prefix="/api/v1")
app.include_router(maintenance_router.router, prefix="/api/v1")
app.include_router(audit_router.router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.APP_NAME}
