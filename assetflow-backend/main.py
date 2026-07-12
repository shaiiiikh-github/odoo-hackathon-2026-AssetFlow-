from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import users, assets, allocations, bookings # We will create these routers

app = FastAPI(
    title="AssetFlow API",
    description="Enterprise Asset & Resource Management System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
# app.include_router(users.router, prefix="/api/v1")
# app.include_router(assets.router, prefix="/api/v1")
# app.include_router(allocations.router, prefix="/api/v1")
# app.include_router(bookings.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AssetFlow API is running"}