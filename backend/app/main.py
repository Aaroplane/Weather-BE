from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.config import get_settings

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered weather monitoring and suggestion system",
    version="1.0.0",
    docs_url="/docs",  
    redoc_url="/redoc"  
)

allowed_origins = settings.allowed_origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Or specify your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(routes.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "endpoints": {
            "weather": "/api/weather/current"
        }
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Log when server starts."""
    print(f"\n{'='*60}")
    print(f"🚀 {settings.app_name} starting...")
    print(f"📍 Environment: {settings.environment}")
    print(f"🐛 Debug Mode: {settings.debug}")
    print(f"🌍 Default Location: {settings.default_location_name}")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"{'='*60}\n")


