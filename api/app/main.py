"""FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.db.mongodb import MongoDB
from app.routes import conversations, health

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(conversations.router)
from app.routes.mongodb_tool import router as mongodb_tool_router
app.include_router(mongodb_tool_router)


# Lifespan events
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting AI Chat API...")
    try:
        MongoDB.connect_db()
        # Create indexes
        db = MongoDB.get_db()
        db.conversations.create_index("user_id")
        db.conversations.create_index("created_at")
        print("✓ Database indexes created")
    except Exception as e:
        print(f"✗ Startup error: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    print("🛑 Shutting down AI Chat API...")
    MongoDB.close_db()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Chat API",
        "version": settings.api_version,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
