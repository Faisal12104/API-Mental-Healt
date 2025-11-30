from fastapi import FastAPI
from app.config import settings
from app.routes import auth, users

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Mental Health App API - Authentication & User Management",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }