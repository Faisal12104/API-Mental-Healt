from fastapi import FastAPI
from app.config import settings
from app.routes import (
    auth, users, mood, psychologists, consultations, messaging,
    forum, forum_posts, forum_comments  # ADD new forum routes
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Mental Health App API - Complete System with Authentication, Mood Tracking, Consultation Management, and Forum Community",  # UPDATE
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(mood.router)
app.include_router(psychologists.router)
app.include_router(consultations.router)
app.include_router(messaging.router)
app.include_router(forum.router)           # ADD
app.include_router(forum_posts.router)     # ADD
app.include_router(forum_comments.router)  # ADD

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running",
        "modules": [
            "authentication", 
            "user-management", 
            "mood-tracking", 
            "consultation-management",
            "forum-community"  # ADD
        ]
    }

@app.get("/health")
async def health_check():
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": [
            "auth", 
            "users", 
            "mood", 
            "psychologists", 
            "consultations", 
            "messaging",
            "forum-rooms",
            "forum-posts",
            "forum-comments"  # ADD
        ]
    }