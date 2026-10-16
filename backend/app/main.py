from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.supabase import supabase
from fastapi import HTTPException
from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.academic import router as academic_router
from app.api.coordinator import router as coordinator_router
app = FastAPI(
    title="LifeOps API",
    description="Backend for the LifeOps Student Operating System",
    version="0.1.0",
)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(academic_router)
app.include_router(coordinator_router)
# Temporary development configuration.
# We will restrict origins when connecting the frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to LifeOps API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "LifeOps Backend",
    }

@app.get("/health/supabase")
def check_supabase_config():
    return {
        "status": "configured",
        "project": settings.app_name,
    }

@app.get("/health/supabase-db")
def check_supabase_database():
    try:
        result = supabase.table("profiles").select("id").limit(1).execute()

        return {
            "status": "connected",
            "message": "Supabase database query successful"
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Supabase query failed: {str(e)}"
        )